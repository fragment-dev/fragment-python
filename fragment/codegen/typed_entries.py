"""Derive strongly-typed batch payloads from single-entry ``addLedgerEntry`` operations.

``addLedgerEntries`` takes ``[AddLedgerEntryInput!]!``, and every entry's
``parameters`` field is an opaque ``JSON`` scalar. GraphQL therefore cannot type
the parameters of an individual entry in a batch: one list means one input type.

The per-entry-type ``addLedgerEntry`` operations already generated for a Schema
carry exactly the missing information, though -- the entry type as a string
literal, and each parameter bound to a typed operation variable:

    mutation PostAuthCapture($ik: SafeString!, ..., $capture_amount: String!) {
      addLedgerEntry(
        ik: $ik
        entry: {ledger: {ik: $ledgerIk}, type: "auth_capture",
                parameters: {capture_amount: $capture_amount}}
      ) { ... }
    }

This module recovers that information into an :class:`EntrySpec` and renders one
pydantic model per entry type, so callers can build batch payloads with real
field names and types instead of untyped dicts.
"""

import ast
from dataclasses import dataclass, field
from functools import cache

from ariadne_codegen.client_generators.constants import UNSET_TYPE_NAME
from ariadne_codegen.utils import process_name, str_to_pascal_case, str_to_snake_case
from graphql import (
    FieldNode,
    IntValueNode,
    NonNullTypeNode,
    ObjectValueNode,
    OperationDefinitionNode,
    OperationType,
    StringValueNode,
    TypeNode,
    ValueNode,
    VariableNode,
)

from fragment.logger import console_log

ADD_LEDGER_ENTRY_FIELD = "addLedgerEntry"
MODULE_NAME = "typed_entries"

# An entry with no `typeVersion` resolves to version 1 server-side, so an
# unpinned operation is normalised to 1 at extraction. That keeps one rule for
# both the model name and the wire payload instead of letting them disagree.
DEFAULT_TYPE_VERSION = 1


@dataclass
class EntryParameter:
    """A single templated parameter of a typed Ledger Entry."""

    # The parameter name as the Schema knows it, e.g. "capture_amount". This is
    # the JSON key sent in `parameters`, so it is preserved verbatim.
    name: str
    # The Python field name. Usually identical to `name`, but snake_cased for
    # Schemas that declare camelCase parameters.
    field_name: str
    # Rendered Python annotation, harvested from the client method ariadne
    # generated for this same operation.
    annotation: str
    required: bool


@dataclass
class EntrySpec:
    """Everything needed to render one typed batch-payload model."""

    entry_type: str
    # Always the unversioned pascal name: `OrderPlaced`, never `OrderPlacedV1`.
    base_name: str
    operation_name: str
    # Kept in the order the parameters appear in the source operation's
    # `parameters: {...}` literal. That order is the cross-SDK canonical key
    # order for the `parameters` payload, so it must not be re-sorted: pydantic
    # emits fields in declaration order, and the Go/Node/Ruby SDKs key off the
    # same source order. Reordering here would silently diverge the wire bytes.
    parameters: list[EntryParameter] = field(default_factory=list)
    # Always concrete: an unpinned operation is normalised to
    # DEFAULT_TYPE_VERSION, because that is what the API resolves it to.
    type_version: int = DEFAULT_TYPE_VERSION

    @property
    def identity(self) -> tuple[str, int]:
        """What a model is keyed on: (entry type, version). Spec 2.2."""
        return (self.entry_type, self.type_version)

    @property
    def versioned_name(self) -> str:
        """`base_name` plus the version it resolves to. Spec 2.5."""
        return f"{self.base_name}V{self.type_version}"


def _safe_field_name(name: str) -> str:
    """Snake_case a Schema parameter into a field name safe to declare.

    `process_name` is ariadne's own helper, so it escapes Python keywords,
    shadowed builtins, and pydantic's reserved field names (derived from
    `dir(BaseModel)`, so it tracks pydantic rather than drifting) exactly the way
    the rest of the generated SDK does. Only `TypedLedgerEntry`'s own attributes
    are ours to handle, and those are read off the base class below.

    PARAMETER_FIELDS keeps the original Schema name, so escaping a field never
    changes the wire format.
    """
    processed = process_name(
        name,
        convert_to_snake_case=True,
        handle_pydantic_resrved_field_names=True,
    )
    if processed in base_class_attribute_names():
        processed += "_"
    return processed


def _is_required(type_node: TypeNode) -> bool:
    """Whether a variable is non-null, i.e. the caller must supply it."""
    return isinstance(type_node, NonNullTypeNode)


def _get_object_field(node: ObjectValueNode, name: str) -> ValueNode | None:
    for field_node in node.fields:
        if field_node.name.value == name:
            return field_node.value
    return None


def _get_entry_argument(
    operation_definition: OperationDefinitionNode,
) -> ObjectValueNode | None:
    """Return the inline `entry:` object of a single-field `addLedgerEntry` post.

    ``None`` for anything else: a query, a multi-field selection, a root fragment
    spread, or an `entry` passed as a variable rather than written inline.
    """
    if operation_definition.operation != OperationType.MUTATION:
        return None

    selections = operation_definition.selection_set.selections
    if len(selections) != 1:
        return None
    root = selections[0]
    if not isinstance(root, FieldNode):
        return None
    if root.name.value != ADD_LEDGER_ENTRY_FIELD:
        return None

    for arg in root.arguments:
        if arg.name.value == "entry" and isinstance(arg.value, ObjectValueNode):
            return arg.value
    return None


def _extract_parameters(
    parameters_node: ValueNode | None,
    operation_definition: OperationDefinitionNode,
    annotations: dict[str, str],
) -> list[EntryParameter]:
    """Recover the typed parameters bound to the entry's `parameters` object."""
    if not isinstance(parameters_node, ObjectValueNode):
        return []

    required_by_variable = {
        vd.variable.name.value: _is_required(vd.type)
        for vd in operation_definition.variable_definitions
    }

    parameters: list[EntryParameter] = []
    taken: set[str] = set()
    for param in parameters_node.fields:
        # Only variable-bound parameters are typeable. A parameter hardcoded in
        # the operation is already fixed and must not become a field.
        if not isinstance(param.value, VariableNode):
            continue
        variable_name = param.value.name.value
        required = required_by_variable.get(variable_name, False)
        # Keyed off the variable, not the parameter: a Schema is free to bind
        # `{captureAmount: $capture_amount}`, and the variable carries the type.
        annotation = annotations.get(str_to_snake_case(variable_name))
        if annotation is None:
            # Falling back keeps the parameter rather than dropping it, but the
            # caller loses type checking on it, so say so rather than degrade
            # quietly.
            console_log.warning(
                "Could not resolve a type for parameter %r (variable $%s) in "
                "operation %s; generating it as Any.",
                param.name.value,
                variable_name,
                operation_definition.name.value if operation_definition.name else "?",
            )
            annotation = "Any"
        parameters.append(
            EntryParameter(
                name=param.name.value,
                field_name=_unique_field_name(
                    param.name.value, taken, operation_definition
                ),
                annotation=annotation,
                required=required,
            )
        )
    return parameters


def _unique_field_name(
    schema_name: str,
    taken: set[str],
    operation_definition: OperationDefinitionNode,
) -> str:
    """Give this parameter a field name no sibling parameter already holds.

    `_safe_field_name` cannot see the other parameters, so two Schema names that
    snake_case alike (`user_id` and `userId`) both arrive as `user_id`. Pydantic
    accepts the duplicate declaration and the last one wins, which puts one
    value under both wire keys. The suffix here is the same idea as the one
    `resolve_class_names` applies to class names, one level down.

    `taken` is mutated so later parameters see the names already claimed.
    """
    field_name = _safe_field_name(schema_name)
    if field_name in taken:
        base = field_name
        counter = 2
        while field_name in taken:
            field_name = f"{base}_{counter}"
            counter += 1
        console_log.warning(
            "Parameters in operation %s map to the same Python field %r; %r is "
            "generated as %r instead. The wire payload is unaffected.",
            operation_definition.name.value if operation_definition.name else "?",
            base,
            schema_name,
            field_name,
        )
    taken.add(field_name)
    return field_name


def extract_entry_spec(
    operation_definition: OperationDefinitionNode,
    annotations: dict[str, str],
) -> EntrySpec | None:
    """Recover an :class:`EntrySpec` from a typed ``addLedgerEntry`` operation.

    Returns ``None`` for any operation that is not a single-entry post with a
    literal entry type -- including the SDK's own ``addLedgerEntry`` and
    ``addLedgerEntryRuntime``, whose type comes from a variable and whose
    parameters are an opaque ``JSON`` blob. Those cannot be typed, and are
    silently skipped rather than treated as an error.

    ``annotations`` maps snake_cased variable names to the Python annotations
    ariadne generated for this operation's client method.
    """
    if not operation_definition.name:
        return None
    entry_arg = _get_entry_argument(operation_definition)
    if entry_arg is None:
        return None

    # A literal `type` is what makes an operation entry-type-specific. Without
    # it there is nothing to key a typed model on.
    type_node = _get_object_field(entry_arg, "type")
    if not isinstance(type_node, StringValueNode):
        return None
    entry_type = type_node.value

    parameters = _extract_parameters(
        _get_object_field(entry_arg, "parameters"),
        operation_definition,
        annotations,
    )

    type_version = DEFAULT_TYPE_VERSION
    version_node = _get_object_field(entry_arg, "typeVersion")
    if isinstance(version_node, IntValueNode):
        type_version = int(version_node.value)

    return EntrySpec(
        entry_type=entry_type,
        # Named for the entry type rather than the operation, so the model is
        # recognisable from the Schema regardless of how the operation that
        # produced it happened to be named.
        base_name=str_to_pascal_case(str_to_snake_case(entry_type)),
        operation_name=operation_definition.name.value,
        parameters=parameters,
        type_version=type_version,
    )


def collect_annotations(
    method_def: ast.FunctionDef | ast.AsyncFunctionDef,
    operation_definition: OperationDefinitionNode,
) -> dict[str, str]:
    """Map snake_cased variable names to the annotations ariadne generated.

    Reusing ariadne's own annotations keeps a typed model's fields identical to
    the equivalent client method's arguments, including custom scalar handling.
    ariadne reorders arguments to put required ones first, so this matches by
    name rather than by position.

    Depends on RewriteUnsetTypeMethodArguments having already collapsed
    `Union[Optional[X], UnsetType]` down to `Optional[X]`, which the plugin
    ordering guarantees. Raises if that has not happened.
    """
    generated: dict[str, str] = {}
    for arg in method_def.args.args:
        if arg.arg == "self" or arg.annotation is None:
            continue
        annotation = ast.unparse(arg.annotation)
        if UNSET_TYPE_NAME in annotation:
            # RewriteUnsetTypeMethodArguments has not run yet. Copying this
            # annotation would emit `UnsetType` into a module that does not
            # import it, and the generated SDK would fail to import at all.
            # Better to stop here than to write out a broken package.
            raise RuntimeError(
                f"Annotation {annotation!r} for argument {arg.arg!r} still "
                f"mentions {UNSET_TYPE_NAME}. GenerateTypedLedgerEntries must be "
                "listed after RewriteUnsetTypeMethodArguments in the codegen "
                "plugin list; see get_codegen_config in fragment/codegen/helpers.py."
            )
        generated[arg.arg] = annotation

    annotations: dict[str, str] = {}
    for vd in operation_definition.variable_definitions:
        name = vd.variable.name.value
        snake = str_to_snake_case(name)
        for candidate in (snake, f"{snake}_"):
            if candidate in generated:
                annotations[snake] = generated[candidate]
                break
    return annotations


BASE_CLASS_SOURCE = '''class TypedLedgerEntry(BaseModel):
    """Base class for a strongly-typed `addLedgerEntries` payload.

    Subclasses declare one field per Schema parameter. The serializer below
    reshapes those flat fields into the nested `AddLedgerEntryInput` the API
    expects, so instances can be passed to `add_ledger_entries` directly.

    That makes dumping one-way: `model_dump()` returns the `AddLedgerEntryInput`
    shape rather than this model's own fields, so
    `type(entry).model_validate(entry.model_dump())` does not round-trip. Dumps
    are for sending; keep the instance itself if you need to log or cache one.
    """

    ENTRY_TYPE: ClassVar[str] = ""
    TYPE_VERSION: ClassVar[int] = 1
    # Maps Schema parameter name -> Python field name. These differ only when a
    # parameter is camelCased or collides with a field on this class.
    PARAMETER_FIELDS: ClassVar[Dict[str, str]] = {}

    ik: Any
    ledger_ik: Any
    description: Optional[str] = None
    posted: Optional[Any] = None
    tags: Optional[List[LedgerEntryTagInput]] = None
    groups: Optional[List[LedgerEntryGroupInput]] = None
    conditions: Optional[List[LedgerEntryConditionInput]] = None

    def entry_parameters(self) -> Dict[str, Any]:
        """The `parameters` payload, keyed by Schema parameter name."""
        return {
            parameter_name: getattr(self, field_name)
            for parameter_name, field_name in self.PARAMETER_FIELDS.items()
            if getattr(self, field_name) is not None
        }

    def to_input(self) -> AddLedgerEntryInput:
        """Convert to the `AddLedgerEntryInput` that `addLedgerEntries` takes."""
        return AddLedgerEntryInput(
            ik=self.ik,
            entry=LedgerEntryInput(
                ledger=LedgerMatchInput(ik=self.ledger_ik),
                type=self.ENTRY_TYPE,
                typeVersion=self.TYPE_VERSION,
                parameters=self.entry_parameters(),
                description=self.description,
                posted=self.posted,
                tags=self.tags,
                groups=self.groups,
                conditions=self.conditions,
            ),
        )

    @model_serializer
    def serialize(self) -> Dict[str, Any]:
        """Serialize as `AddLedgerEntryInput`, not as this flat model.

        The base client dumps variables with `model_dump(by_alias=True)`, so
        this is what puts the correct shape on the wire.
        """
        return self.to_input().model_dump(by_alias=True, exclude_none=True)


def to_entry_inputs(
    entries: Sequence[TypedLedgerEntry],
) -> List[AddLedgerEntryInput]:
    """Convert typed entries to raw inputs, preserving order.

    `add_ledger_entries` accepts typed entries directly. This is for callers who
    want to inspect or adjust the raw payload first.
    """
    return [entry.to_input() for entry in entries]'''


@cache
def base_class_attribute_names() -> frozenset[str]:
    """The attribute names TypedLedgerEntry itself declares.

    Read out of the rendered source rather than hand-listed, so adding a field or
    method to the base class cannot silently start shadowing a Schema parameter.
    """
    module = ast.parse(BASE_CLASS_SOURCE)
    class_def = next(
        node
        for node in module.body
        if isinstance(node, ast.ClassDef) and node.name == "TypedLedgerEntry"
    )
    names = set()
    for node in class_def.body:
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names.add(node.target.id)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            names.add(node.name)
    return frozenset(names)


MODULE_HEADER = """from typing import Any, ClassVar, Dict, List, Optional, Sequence

from pydantic import model_serializer

from .base_model import BaseModel
from .input_types import (
    AddLedgerEntryInput,
    LedgerEntryConditionInput,
    LedgerEntryGroupInput,
    LedgerEntryInput,
    LedgerEntryTagInput,
    LedgerMatchInput,
)"""


EMPTY_MODULE_NOTE = """
# No typed Ledger Entry operations were found in the input queries, so no
# per-entry-type payload models were generated. Add the per-entry-type
# `addLedgerEntry` operations for your Schema to the codegen input directory to
# generate them."""


def resolve_class_names(specs: list[EntrySpec]) -> list[tuple[str, EntrySpec]]:
    """Pair each distinct (entry type, version) with a unique model name.

    Deduplicates on identity, then names each `<BaseName>V<n>` -- see spec 2.2 and
    2.5 for why identity is the pair and why the version is always present.
    Distinct entry types that pascal-case alike (`auth_hold`, `authHold`) fall
    back to the operation name, then a counter, so a model is never dropped.

    Pure, so repeated calls agree. Both callers -- the renderer and the plugin's
    `__init__` re-exports -- resolve names independently rather than one reading
    what the other left behind.
    """
    unique: dict[tuple[str, int], EntrySpec] = {}
    for spec in specs:
        # The same (type, version) from two operations really is one model.
        unique.setdefault(spec.identity, spec)

    resolved: list[tuple[str, EntrySpec]] = []
    seen: set[str] = set()
    for spec in unique.values():
        base = spec.versioned_name
        name = base
        if name in seen:
            name = f"{base}{str_to_pascal_case(spec.operation_name)}"
        counter = 2
        while name in seen:
            name = f"{base}{counter}"
            counter += 1
        seen.add(name)
        resolved.append((name, spec))
    return resolved


def _render_class(class_name: str, spec: EntrySpec) -> list[str]:
    lines = [
        f"class {class_name}(TypedLedgerEntry):",
        f'    """Typed `addLedgerEntries` payload for the '
        f'"{spec.entry_type}" Ledger Entry.',
        "",
        f"    Derived from the `{spec.operation_name}` operation.",
        '    """',
        "",
        f'    ENTRY_TYPE: ClassVar[str] = "{spec.entry_type}"',
    ]
    lines.append(f"    TYPE_VERSION: ClassVar[int] = {spec.type_version}")

    parameters = spec.parameters
    if parameters:
        lines.append("    PARAMETER_FIELDS: ClassVar[Dict[str, str]] = {")
        for parameter in parameters:
            lines.append(f'        "{parameter.name}": "{parameter.field_name}",')
        lines.append("    }")
        lines.append("")
        for parameter in parameters:
            suffix = "" if parameter.required else " = None"
            lines.append(f"    {parameter.field_name}: {parameter.annotation}{suffix}")
    else:
        lines.append("    PARAMETER_FIELDS: ClassVar[Dict[str, str]] = {}")
    return lines


def render_module(specs: list[EntrySpec]) -> str:
    """Render the `typed_entries` module source for the given entry specs."""
    blocks = [MODULE_HEADER, BASE_CLASS_SOURCE]
    for class_name, spec in sorted(resolve_class_names(specs)):
        blocks.append("\n".join(_render_class(class_name, spec)))
    if not specs:
        blocks.append(EMPTY_MODULE_NOTE.strip("\n"))
    return "\n\n\n".join(blocks) + "\n"
