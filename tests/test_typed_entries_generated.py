"""Tests that import and use generated code rather than reading it as text.

String assertions on `render_module`'s output cannot distinguish a working
module from one that merely contains the right substrings: a duplicated field
declaration or an annotation the header does not import satisfies both. These
tests import what codegen emits -- header, base class and per-entry classes --
and exercise the resulting classes.

Offline; no credentials required.
"""

import importlib
import itertools
import sys
from pathlib import Path
from types import ModuleType
from typing import Any, Dict, List, Optional, Type

import pytest
from ariadne_codegen.utils import str_to_snake_case
from graphql import OperationDefinitionNode, parse

# `sdk` is the snapshotted client, on sys.path via `pythonpath` in pyproject.toml.
from sdk import typed_entries as snapshot_typed_entries
from sdk.input_types import AddLedgerEntryInput

from fragment.codegen.typed_entries import EntrySpec, extract_entry_spec, render_module

SNAPSHOT_QUERIES = (
    Path(__file__).parent / "snapshots" / "001-marketing-schema" / "queries.graphql"
)

_PACKAGE_COUNTER = itertools.count()


def build_module(tmp_path: Path, specs: List[EntrySpec]) -> ModuleType:
    """Render `specs` and import the result as a module.

    The throwaway package re-exports the snapshot's `base_model` and
    `input_types`, so the rendered module's own relative imports resolve as
    written instead of being replaced by injected names. The package name is
    unique per call so repeated renders are not served from `sys.modules`.
    """
    name = f"generated_typed_entries_{next(_PACKAGE_COUNTER)}"
    package = tmp_path / name
    package.mkdir()
    (package / "__init__.py").write_text("", encoding="utf-8")
    (package / "base_model.py").write_text(
        "from sdk.base_model import BaseModel\n", encoding="utf-8"
    )
    (package / "input_types.py").write_text(
        "from sdk.input_types import *  # noqa: F401,F403\n", encoding="utf-8"
    )
    (package / "typed_entries.py").write_text(render_module(specs), encoding="utf-8")

    sys.path.insert(0, str(tmp_path))
    try:
        return importlib.import_module(f"{name}.typed_entries")
    finally:
        sys.path.remove(str(tmp_path))


def operation(parameters: str, variables: str) -> OperationDefinitionNode:
    doc = parse(
        f"""mutation PostThing($ik: SafeString!, $ledgerIk: SafeString!, {variables}) {{
          addLedgerEntry(
            ik: $ik
            entry: {{ledger: {{ik: $ledgerIk}}, type: "thing", typeVersion: 2,
                    parameters: {{{parameters}}}}}
          ) {{ __typename }}
        }}"""
    )
    node = doc.definitions[0]
    assert isinstance(node, OperationDefinitionNode)
    return node


def spec_from(
    parameters: str, variables: str, annotations: Dict[str, str]
) -> EntrySpec:
    spec = extract_entry_spec(operation(parameters, variables), annotations)
    assert spec is not None
    return spec


def models_in(module: ModuleType) -> List[Type[Any]]:
    base = module.TypedLedgerEntry
    return [
        value
        for value in vars(module).values()
        if isinstance(value, type) and issubclass(value, base) and value is not base
    ]


@pytest.fixture
def thing(tmp_path: Path) -> Type[Any]:
    """A model covering four parameter shapes at once.

    A plain parameter, a camelCase one, one that escapes because it shadows a
    builtin, and an optional one. The optional case is synthetic: every
    CLI-generated parameter is non-null, so no snapshot query produces one.
    """
    module = build_module(
        tmp_path,
        [
            spec_from(
                parameters="amount: $amount, userId: $userId, type: $entryType, "
                "memo: $memo",
                variables="$amount: String!, $userId: String!, "
                "$entryType: String!, $memo: String",
                annotations={
                    "amount": "str",
                    "user_id": "str",
                    "entry_type": "str",
                    "memo": "Optional[str]",
                },
            )
        ],
    )
    return module.ThingV2


def test_rendered_module_imports_as_written(thing: Type[Any]) -> None:
    """The emitted header covers everything the classes reference."""
    assert thing.ENTRY_TYPE == "thing"
    assert thing.TYPE_VERSION == 2


def test_rendered_class_declares_each_field_exactly_once(thing: Type[Any]) -> None:
    """A duplicated declaration is invisible in the source but not on the class.

    Pydantic keeps the last of two identically named fields, so both Schema
    names would read one value.
    """
    field_names = list(thing.PARAMETER_FIELDS.values())
    assert len(field_names) == len(set(field_names)), field_names
    assert set(field_names) <= set(thing.model_fields)


def test_colliding_parameters_carry_their_own_values(tmp_path: Path) -> None:
    """`user_id` and `userId` reduce to one Python field but two wire keys."""
    module = build_module(
        tmp_path,
        [
            spec_from(
                parameters="user_id: $snake, userId: $camel",
                variables="$snake: String!, $camel: String!",
                annotations={"snake": "str", "camel": "str"},
            )
        ],
    )
    entry = module.ThingV2(
        ik="ik-1", ledger_ik="prod", user_id="SNAKE", user_id_2="CAMEL"
    )
    assert entry.to_input().entry.parameters == {
        "user_id": "SNAKE",
        "userId": "CAMEL",
    }


def test_required_parameters_are_required_and_optional_ones_are_not(
    thing: Type[Any],
) -> None:
    entry = thing(ik="ik-1", ledger_ik="prod", amount="100", user_id="u", type_="t")
    assert entry.memo is None

    with pytest.raises(ValueError):
        thing(ik="ik-1", ledger_ik="prod", amount="100")


def test_optional_parameter_annotation_survives_into_the_model(
    thing: Type[Any],
) -> None:
    field = thing.model_fields["memo"]
    assert field.annotation is Optional[str]
    assert not field.is_required()


def test_unset_optional_parameter_is_left_out_of_the_payload(
    thing: Type[Any],
) -> None:
    entry = thing(ik="ik-1", ledger_ik="prod", amount="100", user_id="u", type_="t")
    assert entry.to_input().entry.parameters == {
        "amount": "100",
        "userId": "u",
        "type": "t",
    }


def test_set_optional_parameter_reaches_the_payload(thing: Type[Any]) -> None:
    entry = thing(
        ik="ik-1", ledger_ik="prod", amount="100", user_id="u", type_="t", memo="note"
    )
    assert entry.to_input().entry.parameters["memo"] == "note"


def test_escaped_field_keeps_its_schema_name_on_the_wire(thing: Type[Any]) -> None:
    """`type` shadows a builtin, so the field is `type_`; the wire key is not."""
    dumped = thing(
        ik="ik-1", ledger_ik="prod", amount="100", user_id="u", type_="t"
    ).model_dump(by_alias=True)
    assert dumped == {
        "ik": "ik-1",
        "entry": {
            "ledger": {"ik": "prod"},
            "type": "thing",
            "typeVersion": 2,
            "parameters": {"amount": "100", "userId": "u", "type": "t"},
        },
    }


def test_to_entry_inputs_preserves_order(thing: Type[Any]) -> None:
    """`addLedgerEntries` commits and reports in input order."""
    module = sys.modules[thing.__module__]
    entries = [
        thing(ik=f"ik-{n}", ledger_ik="prod", amount=str(n), user_id="u", type_="t")
        for n in range(3)
    ]
    inputs = module.to_entry_inputs(entries)
    assert all(isinstance(entry, AddLedgerEntryInput) for entry in inputs)
    assert [entry.ik for entry in inputs] == ["ik-0", "ik-1", "ik-2"]


def test_module_with_no_entry_types_is_still_importable(tmp_path: Path) -> None:
    """The shape `fragment/sdk/typed_entries.py` has.

    The std queries type nothing, so the shipped SDK gets the base class, the
    helper and the explanatory note -- and `fragment/sdk/__init__.py` imports
    that module on every import of the package.
    """
    module = build_module(tmp_path, [])
    assert module.TypedLedgerEntry.ENTRY_TYPE == ""
    assert module.to_entry_inputs([]) == []


# --- The committed snapshot, the artifact a customer gets ---------------------


def snapshot_models() -> List[Type[Any]]:
    return models_in(snapshot_typed_entries)


def test_the_snapshot_generated_some_models() -> None:
    """Keeps the parametrized tests below from passing vacuously."""
    assert len(snapshot_models()) == 9


@pytest.mark.parametrize("model", snapshot_models(), ids=lambda m: m.__name__)
def test_every_snapshot_model_serialises(model: Type[Any]) -> None:
    """Every parameter in the marketing Schema is a required `String`."""
    entry = model(
        ik="ik-1",
        ledger_ik="prod",
        **{field: field for field in model.PARAMETER_FIELDS.values()},
    )
    dumped: Dict[str, Any] = entry.model_dump(by_alias=True)
    assert dumped["entry"]["type"] == model.ENTRY_TYPE
    assert dumped["entry"]["typeVersion"] == model.TYPE_VERSION
    assert set(dumped["entry"]["parameters"]) == set(model.PARAMETER_FIELDS)


@pytest.mark.parametrize("model", snapshot_models(), ids=lambda m: m.__name__)
def test_every_snapshot_model_is_exported(model: Type[Any]) -> None:
    import sdk

    assert model.__name__ in sdk.__all__
    assert getattr(sdk, model.__name__) is model


def test_snapshot_models_do_not_shadow_a_base_class_field() -> None:
    """A parameter named `ik` or `posted` escapes rather than replacing the base."""
    base_fields = set(snapshot_typed_entries.TypedLedgerEntry.model_fields)
    for model in snapshot_models():
        overlap = set(model.PARAMETER_FIELDS.values()) & base_fields
        assert not overlap, f"{model.__name__} shadows {overlap}"


def test_versioned_snapshot_models_are_distinct() -> None:
    v1 = snapshot_typed_entries.OrderPlacedV1
    v2 = snapshot_typed_entries.OrderPlacedV2
    assert (v1.ENTRY_TYPE, v1.TYPE_VERSION) == ("order_placed", 1)
    assert (v2.ENTRY_TYPE, v2.TYPE_VERSION) == ("order_placed", 2)
    assert set(v2.PARAMETER_FIELDS) - set(v1.PARAMETER_FIELDS) == {"service_fee"}


def test_no_snapshot_parameter_is_optional() -> None:
    """Why the optional case in `thing` is synthetic.

    A CLI-generated Schema that produces a nullable parameter fails this, and
    the optional path gains real coverage.
    """
    assert all(
        model.model_fields[name].is_required()
        for model in snapshot_models()
        for name in model.PARAMETER_FIELDS.values()
    )


def test_snapshot_module_matches_a_fresh_render_of_its_own_queries(
    tmp_path: Path,
) -> None:
    """Narrows `make check-snapshots` to the renderer, without the network."""
    document = parse(SNAPSHOT_QUERIES.read_text(encoding="utf-8"))
    specs = []
    for definition in document.definitions:
        if not isinstance(definition, OperationDefinitionNode):
            continue
        spec = extract_entry_spec(definition, _annotations_for(definition))
        if spec is not None:
            specs.append(spec)

    module = build_module(tmp_path, specs)
    assert {model.__name__ for model in models_in(module)} == {
        model.__name__ for model in snapshot_models()
    }


def _annotations_for(definition: OperationDefinitionNode) -> Dict[str, str]:
    """Every marketing-Schema variable is a non-null String."""
    return {
        str_to_snake_case(vd.variable.name.value): "str"
        for vd in definition.variable_definitions
    }
