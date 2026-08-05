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
from functools import lru_cache
from typing import Dict, FrozenSet, List, Optional

from ariadne_codegen.utils import process_name, str_to_pascal_case, str_to_snake_case
from graphql import (
    FieldNode,
    ObjectValueNode,
    OperationDefinitionNode,
    OperationType,
    StringValueNode,
    VariableNode,
)

ADD_LEDGER_ENTRY_FIELD = "addLedgerEntry"
MODULE_NAME = "typed_entries"

# Used for the model *name* when an operation pins no typeVersion. Naming only:
# the wire payload still omits typeVersion in that case.
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
    class_name: str
    operation_name: str
    # Kept in the order the parameters appear in the source operation's
    # `parameters: {...}` literal. That order is the cross-SDK canonical key
    # order for the `parameters` payload, so it must not be re-sorted: pydantic
    # emits fields in declaration order, and the Go/Node/Ruby SDKs key off the
    # same source order. Reordering here would silently diverge the wire bytes.
    parameters: List[EntryParameter] = field(default_factory=list)
    # Present only when the source operation pins a type version.
    type_version: Optional[int] = None


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


def _unwrap_type(type_node) -> tuple:
    """Return ``(named_type_name, required)`` for a variable's type node."""
    required = type_node.kind == "non_null_type"
    node = type_node
    while hasattr(node, "type"):
        node = node.type
    return node.name.value, required


def _get_object_field(node: ObjectValueNode, name: str):
    for f in node.fields:
        if f.name.value == name:
            return f.value
    return None


def _get_entry_argument(
    operation_definition: OperationDefinitionNode,
) -> Optional[ObjectValueNode]:
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
    parameters_node,
    operation_definition: OperationDefinitionNode,
    annotations: Dict[str, str],
) -> List[EntryParameter]:
    """Recover the typed parameters bound to the entry's `parameters` object."""
    if not isinstance(parameters_node, ObjectValueNode):
        return []

    variable_types = {
        vd.variable.name.value: _unwrap_type(vd.type)
        for vd in operation_definition.variable_definitions
    }

    parameters: List[EntryParameter] = []
    for param in parameters_node.fields:
        # Only variable-bound parameters are typeable. A parameter hardcoded in
        # the operation is already fixed and must not become a field.
        if not isinstance(param.value, VariableNode):
            continue
        variable_name = param.value.name.value
        _, required = variable_types.get(variable_name, (None, False))
        # Keyed off the variable, not the parameter: a Schema is free to bind
        # `{captureAmount: $capture_amount}`, and the variable carries the type.
        # Falls back to the loosest annotation rather than dropping a parameter.
        annotation = annotations.get(str_to_snake_case(variable_name)) or "Any"
        parameters.append(
            EntryParameter(
                name=param.name.value,
                field_name=_safe_field_name(param.name.value),
                annotation=annotation,
                required=required,
            )
        )
    return parameters


def extract_entry_spec(
    operation_definition: OperationDefinitionNode,
    annotations: Dict[str, str],
) -> Optional[EntrySpec]:
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

    type_version = None
    version_node = _get_object_field(entry_arg, "typeVersion")
    if version_node is not None and version_node.kind == "int_value":
        type_version = int(version_node.value)

    return EntrySpec(
        entry_type=entry_type,
        # Named for the entry type rather than the operation, so the model is
        # recognisable from the Schema regardless of how the operation that
        # produced it happened to be named.
        class_name=str_to_pascal_case(str_to_snake_case(entry_type)),
        operation_name=operation_definition.name.value,
        parameters=parameters,
        type_version=type_version,
    )


def collect_annotations(
    method_def,
    operation_definition: OperationDefinitionNode,
) -> Dict[str, str]:
    """Map snake_cased variable names to the annotations ariadne generated.

    Reusing ariadne's own annotations keeps a typed model's fields identical to
    the equivalent client method's arguments, including custom scalar handling.
    ariadne reorders arguments to put required ones first, so this matches by
    name rather than by position.
    """
    generated: Dict[str, str] = {}
    for arg in method_def.args.args:
        if arg.arg == "self" or arg.annotation is None:
            continue
        generated[arg.arg] = ast.unparse(arg.annotation)

    annotations: Dict[str, str] = {}
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
    """

    ENTRY_TYPE: ClassVar[str] = ""
    TYPE_VERSION: ClassVar[Optional[int]] = None
    # Maps Schema parameter name -> Python field name. These differ only when a
    # parameter is camelCased or collides with a field on this class.
    PARAMETER_FIELDS: ClassVar[Dict[str, str]] = {}

    ik: Any
    ledger_ik: Any
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


@lru_cache(maxsize=1)
def base_class_attribute_names() -> FrozenSet[str]:
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


def assign_class_names(specs: List[EntrySpec]) -> List[EntrySpec]:
    """Give every distinct entry type and version its own uniquely named model.

    A model's identity is the (entry type, type version) pair, not the entry type
    alone: the same type at two versions is two different parameter sets, and
    collapsing them would silently drop one and post the wrong version.

    Every name carries a version, defaulting to V1 when the operation pins none.
    A name therefore depends only on that payload's own identity, never on which
    other operations are in the input: suffixing only on collision would mean
    adding a second version later renames the first and breaks every existing
    call site (spec §2.6).

    The default is naming-only. `TYPE_VERSION` stays `None` when unpinned, so
    `typeVersion` is still omitted from the wire -- "unspecified" and "explicitly
    1" are not assumed to be equivalent to the API.

    Remaining collisions (distinct entry types that pascal-case alike, e.g.
    `auth_hold` and `authHold`) fall back to the source operation name, then to a
    counter, so a model is never dropped.
    """
    unique: Dict[tuple, EntrySpec] = {}
    for spec in specs:
        # The same (type, version) from two operations really is one model.
        unique.setdefault((spec.entry_type, spec.type_version), spec)

    named: List[EntrySpec] = []
    seen: set = set()
    for spec in unique.values():
        version = (
            DEFAULT_TYPE_VERSION if spec.type_version is None else spec.type_version
        )
        base = f"{spec.class_name}V{version}"
        name = base
        if name in seen:
            name = f"{base}{str_to_pascal_case(spec.operation_name)}"
        counter = 2
        while name in seen:
            name = f"{base}{counter}"
            counter += 1
        spec.class_name = name
        seen.add(name)
        named.append(spec)
    return named


def _render_class(spec: EntrySpec) -> List[str]:
    lines = [
        f"class {spec.class_name}(TypedLedgerEntry):",
        f'    """Typed `addLedgerEntries` payload for the '
        f'"{spec.entry_type}" Ledger Entry.',
        "",
        f"    Derived from the `{spec.operation_name}` operation.",
        '    """',
        "",
        f'    ENTRY_TYPE: ClassVar[str] = "{spec.entry_type}"',
    ]
    if spec.type_version is not None:
        lines.append(f"    TYPE_VERSION: ClassVar[Optional[int]] = {spec.type_version}")

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


def render_module(specs: List[EntrySpec]) -> str:
    """Render the `typed_entries` module source for the given entry specs."""
    blocks = [MODULE_HEADER, BASE_CLASS_SOURCE]
    for spec in sorted(assign_class_names(specs), key=lambda s: s.class_name):
        blocks.append("\n".join(_render_class(spec)))
    if not specs:
        blocks.append(EMPTY_MODULE_NOTE.strip("\n"))
    return "\n\n\n".join(blocks) + "\n"
