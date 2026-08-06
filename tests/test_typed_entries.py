"""Unit tests for typed batch-entry derivation.

No credentials or network required, unlike the integration tests alongside them.

These cover what the shared conformance fixtures structurally cannot: a fixture
generates once, so it can never catch generation that misbehaves the *second*
time it runs. `resolve_class_names` previously mutated its input, which made
`OrderPlaced` become `OrderPlacedV1` and then `OrderPlacedV1V1`.
"""

import ast
from pathlib import Path
from typing import Any, ClassVar, Dict, List, Optional, Sequence

import pytest
from ariadne_codegen.utils import str_to_pascal_case, str_to_snake_case
from graphql import OperationDefinitionNode, parse
from pydantic import model_serializer

from fragment.codegen.typed_entries import (
    BASE_CLASS_SOURCE,
    DEFAULT_TYPE_VERSION,
    EntryParameter,
    EntrySpec,
    _safe_field_name,
    collect_annotations,
    extract_entry_spec,
    render_module,
    resolve_class_names,
)
from fragment.sdk.base_model import BaseModel

SNAPSHOT_CLIENT = (
    Path(__file__).parent / "snapshots" / "001-marketing-schema" / "sdk" / "client.py"
)

from fragment.sdk.input_types import (
    AddLedgerEntryInput,
    LedgerEntryConditionInput,
    LedgerEntryGroupInput,
    LedgerEntryInput,
    LedgerEntryTagInput,
    LedgerMatchInput,
)


def spec(
    entry_type: str,
    type_version: int = DEFAULT_TYPE_VERSION,
    operation_name: str = "PostSomething",
    parameters: Optional[List[EntryParameter]] = None,
) -> EntrySpec:
    # Derived exactly as `extract_entry_spec` does. Rolling this by hand instead
    # let `authHold` become `Authhold`, which silently stopped the collision test
    # from colliding.
    base_name = str_to_pascal_case(str_to_snake_case(entry_type))
    return EntrySpec(
        entry_type=entry_type,
        base_name=base_name,
        operation_name=operation_name,
        parameters=parameters or [],
        type_version=type_version,
    )


def names(specs: List[EntrySpec]) -> List[str]:
    return [class_name for class_name, _ in resolve_class_names(specs)]


def test_version_is_always_in_the_name() -> None:
    """Spec 2.5: the name always carries the version the entry resolves to.

    An operation that pins no `typeVersion` is normalised to 1 at extraction,
    because that is what the API resolves it to -- so there is no unpinned case
    left by the time a name is chosen.
    """
    assert names([spec("card_settle")]) == ["CardSettleV1"]
    assert names([spec("card_settle", 1)]) == ["CardSettleV1"]
    assert names([spec("card_settle", 3)]) == ["CardSettleV3"]


def test_versions_of_one_type_are_separate_models() -> None:
    """Spec 2.2: identity is (type, version), so v1 and v2 both survive."""
    assert names([spec("order_placed", 1), spec("order_placed", 2)]) == [
        "OrderPlacedV1",
        "OrderPlacedV2",
    ]


def test_same_identity_from_two_operations_is_one_model() -> None:
    """Spec 2.2: deduplicated, and lossless given the CLI/API uniqueness rule."""
    assert names(
        [spec("card_settle", 1, "PostA"), spec("card_settle", 1, "PostB")]
    ) == ["CardSettleV1"]


def test_colliding_base_names_are_disambiguated() -> None:
    """Distinct types that pascal-case alike must not collapse into one model.

    `auth_hold` and `authHold` are different entry types that both pascal-case to
    `AuthHold`, so the second falls back to its source operation name. Operation
    names are realistic: a generator derives them from the entry type too, and
    GraphQL forbids duplicates in one document, so it must already have
    disambiguated them itself.
    """
    resolved = names(
        [spec("auth_hold", 1, "PostAuthHold"), spec("authHold", 1, "PostAuthHold2")]
    )
    assert resolved == ["AuthHoldV1", "AuthHoldV1PostAuthHold2"]


def test_adding_a_version_does_not_rename_the_existing_model() -> None:
    """Spec 2.6: an additive Schema change must not break caller source.

    A name depends only on its own identity, never on which other operations
    happen to be present.
    """
    before = names([spec("order_placed", 1)])
    after = names([spec("order_placed", 1), spec("order_placed", 2)])
    assert before == ["OrderPlacedV1"]
    assert after[0] == before[0]


@pytest.mark.parametrize("calls", [2, 3])
def test_resolve_class_names_is_idempotent(calls: int) -> None:
    specs = [spec("order_placed", 1), spec("order_placed", 2), spec("card_settle")]
    results = [names(specs) for _ in range(calls)]
    assert len(set(map(tuple, results))) == 1, results


def test_resolve_class_names_does_not_mutate_its_input() -> None:
    specs = [spec("order_placed", 1), spec("card_settle")]
    before = [(s.entry_type, s.base_name, s.type_version) for s in specs]
    resolve_class_names(specs)
    resolve_class_names(specs)
    after = [(s.entry_type, s.base_name, s.type_version) for s in specs]
    assert after == before


def test_render_module_is_idempotent() -> None:
    """Rendering twice must produce identical source, or snapshots would churn."""
    specs = [
        spec(
            "order_placed",
            1,
            parameters=[
                EntryParameter(
                    name="order_cost",
                    field_name="order_cost",
                    annotation="str",
                    required=True,
                )
            ],
        ),
        spec("order_placed", 2),
    ]
    first = render_module(specs)
    assert render_module(specs) == first
    assert "class OrderPlacedV1(TypedLedgerEntry):" in first
    assert "class OrderPlacedV2(TypedLedgerEntry):" in first
    assert "V1V1" not in first


# --- Parameter naming: what reaches Python vs what reaches the wire -----------


@pytest.mark.parametrize(
    ("schema_name", "field_name"),
    [
        ("order_cost", "order_cost"),  # already safe, left alone
        ("type", "type_"),  # shadows a builtin
        ("class", "class_"),  # Python keyword
        ("def", "def_"),
        ("json", "json_"),  # pydantic reserved
        ("copy", "copy_"),
        ("model_dump", "model_dump_"),
        ("ik", "ik_"),  # collides with TypedLedgerEntry's own field
        ("posted", "posted_"),
        ("description", "description_"),
        ("userId", "user_id"),  # camelCase is snake_cased
        ("captureAmount", "capture_amount"),
    ],
)
def test_schema_parameter_becomes_a_safe_field_name(
    schema_name: str, field_name: str
) -> None:
    assert _safe_field_name(schema_name) == field_name


def operation(parameters: str, variables: str) -> OperationDefinitionNode:
    doc = parse(
        f"""mutation PostThing($ik: SafeString!, $ledgerIk: SafeString!, {variables}) {{
          addLedgerEntry(
            ik: $ik
            entry: {{ledger: {{ik: $ledgerIk}}, type: "thing", parameters: {{{parameters}}}}}
          ) {{ __typename }}
        }}"""
    )
    node = doc.definitions[0]
    assert isinstance(node, OperationDefinitionNode)
    return node


def test_parameter_fields_keeps_the_schema_name_when_the_field_is_escaped() -> None:
    """The README's promise: escaping is local and never reaches the wire."""
    spec_ = extract_entry_spec(
        operation(
            parameters="type: $entryType, json: $blob, userId: $userId",
            variables="$entryType: String!, $blob: String!, $userId: String!",
        ),
        annotations={"entry_type": "str", "blob": "str", "user_id": "str"},
    )
    assert spec_ is not None
    # (Schema name kept verbatim, Python field escaped or snake_cased.)
    assert [(p.name, p.field_name) for p in spec_.parameters] == [
        ("type", "type_"),
        ("json", "json_"),
        ("userId", "user_id"),
    ]


def test_rendered_parameter_fields_maps_wire_name_to_python_field() -> None:
    spec_ = extract_entry_spec(
        operation(
            parameters="type: $entryType, userId: $userId",
            variables="$entryType: String!, $userId: String!",
        ),
        annotations={"entry_type": "str", "user_id": "str"},
    )
    assert spec_ is not None
    rendered = render_module([spec_])
    assert '"type": "type_",' in rendered
    assert '"userId": "user_id",' in rendered
    assert "    type_: str" in rendered
    assert "    user_id: str" in rendered


# --- to_input() / serialisation ------------------------------------------------


@pytest.fixture(scope="module")
def sample() -> type:
    """A model built on the base class *as rendered*, not as last generated.

    `BASE_CLASS_SOURCE` is a source template, so importing the committed
    `fragment.sdk.typed_entries` would test whenever codegen last ran instead of
    what it emits now. Executing the template keeps these assertions pointed at
    the thing under test.
    """
    namespace: dict = {
        "Any": Any,
        "ClassVar": ClassVar,
        "Dict": Dict,
        "List": List,
        "Optional": Optional,
        "Sequence": Sequence,
        "BaseModel": BaseModel,
        "model_serializer": model_serializer,
        "AddLedgerEntryInput": AddLedgerEntryInput,
        "LedgerEntryInput": LedgerEntryInput,
        "LedgerMatchInput": LedgerMatchInput,
        "LedgerEntryTagInput": LedgerEntryTagInput,
        "LedgerEntryGroupInput": LedgerEntryGroupInput,
        "LedgerEntryConditionInput": LedgerEntryConditionInput,
    }
    exec(BASE_CLASS_SOURCE, namespace)  # noqa: S102
    return type(
        "Sample",
        (namespace["TypedLedgerEntry"],),
        {
            "__annotations__": {
                "type_": str,
                "user_id": str,
                "optional_thing": Optional[str],
            },
            "optional_thing": None,
            "ENTRY_TYPE": "thing",
            "TYPE_VERSION": 2,
            "PARAMETER_FIELDS": {
                "type": "type_",
                "userId": "user_id",
                "optionalThing": "optional_thing",
            },
        },
    )


def test_to_input_builds_the_nested_add_ledger_entry_input(sample: type) -> None:
    entry = sample(ik="ik-1", ledger_ik="prod", type_="t", user_id="u").to_input()
    assert entry.ik == "ik-1"
    assert entry.entry.ledger is not None
    assert entry.entry.ledger.ik == "prod"
    assert entry.entry.type_ == "thing"
    assert entry.entry.type_version == 2
    assert entry.entry.parameters == {"type": "t", "userId": "u"}
    assert entry.entry.lines is None


def test_serialisation_uses_schema_names_and_omits_what_was_not_set(
    sample: type,
) -> None:
    dumped = sample(ik="ik-1", ledger_ik="prod", type_="t", user_id="u").model_dump(
        by_alias=True
    )
    assert dumped == {
        "ik": "ik-1",
        "entry": {
            "ledger": {"ik": "prod"},
            "type": "thing",
            "typeVersion": 2,
            "parameters": {"type": "t", "userId": "u"},
        },
    }


def test_optional_parameter_is_carried_when_set(sample: type) -> None:
    dumped = sample(
        ik="ik-1",
        ledger_ik="prod",
        type_="t",
        user_id="u",
        optional_thing="here",
        description="a description",
        posted="1968-01-01T16:45:00Z",
    ).model_dump(by_alias=True)
    assert dumped["entry"]["parameters"] == {
        "type": "t",
        "userId": "u",
        "optionalThing": "here",
    }
    assert dumped["entry"]["description"] == "a description"
    assert dumped["entry"]["posted"] == "1968-01-01T16:45:00Z"


# --- The widened argument must not outrun what the base client converts -------


def test_generated_batch_method_coerces_entries_to_a_list() -> None:
    """Widening to `Sequence` is only safe if the body narrows back.

    The base client recurses into variables with `isinstance(value, list)`, so a
    tuple would satisfy the annotation, skip conversion, and reach `json.dumps`
    still holding model objects.
    """
    source = (SNAPSHOT_CLIENT).read_text()
    tree = ast.parse(source)
    method = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "add_ledger_entries"
    )
    assignments = [
        ast.unparse(node)
        for node in ast.walk(method)
        if isinstance(node, ast.Dict)
        and any(isinstance(k, ast.Constant) and k.value == "entries" for k in node.keys)
    ]
    assert assignments == ["{'entries': list(entries)}"]


def test_parameters_that_snake_case_alike_get_separate_fields() -> None:
    """Two Schema names can collapse to one Python field; they must not share it.

    Pydantic accepts a duplicated field declaration and lets the last one win,
    which would put a single value under both wire keys.
    """
    spec_ = extract_entry_spec(
        operation(
            parameters="user_id: $snake, userId: $camel",
            variables="$snake: String!, $camel: String!",
        ),
        annotations={"snake": "str", "camel": "str"},
    )
    assert spec_ is not None
    assert [(p.name, p.field_name) for p in spec_.parameters] == [
        ("user_id", "user_id"),
        ("userId", "user_id_2"),
    ]


def test_three_way_field_collision_keeps_going() -> None:
    spec_ = extract_entry_spec(
        operation(
            parameters="user_id: $a, userId: $b, USER_ID: $c",
            variables="$a: String!, $b: String!, $c: String!",
        ),
        annotations={"a": "str", "b": "str", "c": "str"},
    )
    assert spec_ is not None
    field_names = [p.field_name for p in spec_.parameters]
    assert len(set(field_names)) == 3, field_names


def test_colliding_parameters_keep_distinct_wire_keys(sample: type) -> None:
    """The rename is local. Each Schema name still carries its own value."""
    spec_ = extract_entry_spec(
        operation(
            parameters="user_id: $snake, userId: $camel",
            variables="$snake: String!, $camel: String!",
        ),
        annotations={"snake": "str", "camel": "str"},
    )
    assert spec_ is not None
    rendered = render_module([spec_])
    assert '"user_id": "user_id",' in rendered
    assert '"userId": "user_id_2",' in rendered


def test_collect_annotations_rejects_an_unrewritten_unset_type() -> None:
    """Guards a load-bearing plugin order.

    `collect_annotations` copies annotations off the generated client method, so
    it depends on `RewriteUnsetTypeMethodArguments` having already collapsed
    `Union[Optional[X], UnsetType]`. Listed the other way round, the typed module
    gets `UnsetType` without importing it and the whole SDK fails to import.
    """
    method = ast.parse(
        "async def post_thing(self, memo: Union[Optional[str], UnsetType] = None): ..."
    ).body[0]
    assert isinstance(method, ast.AsyncFunctionDef)
    op = operation(parameters="memo: $memo", variables="$memo: String")

    with pytest.raises(RuntimeError, match="UnsetType"):
        collect_annotations(method, op)


def test_collect_annotations_accepts_a_rewritten_annotation() -> None:
    method = ast.parse(
        "async def post_thing(self, memo: Optional[str] = None): ..."
    ).body[0]
    assert isinstance(method, ast.AsyncFunctionDef)
    op = operation(parameters="memo: $memo", variables="$memo: String")

    assert collect_annotations(method, op) == {"memo": "Optional[str]"}
