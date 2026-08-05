"""Unit tests for typed batch-entry derivation.

No credentials or network required, unlike the integration tests alongside them.

These cover what the shared conformance fixtures structurally cannot: a fixture
generates once, so it can never catch generation that misbehaves the *second*
time it runs. `resolve_class_names` previously mutated its input, which made
`OrderPlaced` become `OrderPlacedV1` and then `OrderPlacedV1V1`.
"""

from typing import List, Optional

import pytest
from ariadne_codegen.utils import str_to_pascal_case, str_to_snake_case

from fragment.codegen.typed_entries import (
    DEFAULT_TYPE_VERSION,
    EntryParameter,
    EntrySpec,
    render_module,
    resolve_class_names,
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
