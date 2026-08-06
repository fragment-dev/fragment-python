"""Type-level assertions for the typed batch API. Checked by mypy, never run.

The point of the typed payloads is what a type checker says about them, and
nothing else in the suite can assert that -- a runtime test passes just as
happily against `entries: Any`. `make typecheck` covers this file.

Each `# type: ignore[...]` is an assertion in both directions. It says the call
below is expected to be rejected, and because `warn_unused_ignores` is on, mypy
fails if the call ever starts passing. So loosening the signature breaks this
file just as surely as tightening it too far does.

Imports resolve through `mypy_path` in pyproject.toml, which points at the
snapshotted `sdk` -- the same package the runtime tests import.
"""

from typing import List, Sequence, Union

from sdk.client import Client
from sdk.input_types import AddLedgerEntryInput
from sdk.typed_entries import CardSettleV1, OrderPlacedV1, TypedLedgerEntry


def order_placed() -> OrderPlacedV1:
    return OrderPlacedV1(
        ik="ik",
        ledger_ik="prod",
        user_id="u",
        order_id="o",
        order_cost="1000",
        currency="USD",
        platform_fee="100",
        driver_fee="200",
        restaurant_id="r",
        driver_id="d",
    )


async def accepts_the_shapes_callers_actually_build(
    client: Client,
    typed: OrderPlacedV1,
    other: CardSettleV1,
    raw: AddLedgerEntryInput,
) -> None:
    """None of these may error. A comprehension over orders is the common shape."""
    await client.add_ledger_entries(entries=[typed, typed])

    # `Sequence`, not `list`, is what makes this one work: `list` is invariant,
    # so a pre-built `list[OrderPlacedV1]` is not a `list[Union[...]]`.
    prebuilt: List[OrderPlacedV1] = [order_placed() for _ in range(3)]
    await client.add_ledger_entries(entries=prebuilt)

    await client.add_ledger_entries(entries=[raw])
    await client.add_ledger_entries(entries=[typed, raw])
    await client.add_ledger_entries(entries=(typed,))
    await client.add_ledger_entries(entries=[typed], headers={"X-Test": "1"})

    mixed: Sequence[Union[AddLedgerEntryInput, TypedLedgerEntry]] = [typed, other, raw]
    await client.add_ledger_entries(entries=mixed)


async def rejects_what_is_not_an_entry(client: Client, typed: OrderPlacedV1) -> None:
    """The widening must not have degraded into `Any`."""
    await client.add_ledger_entries(entries=["not an entry"])  # type: ignore[list-item]
    await client.add_ledger_entries(entries=[{"ik": "x"}])  # type: ignore[list-item]
    await client.add_ledger_entries(entries=typed)  # type: ignore[arg-type]
    await client.add_ledger_entries(entries=None)  # type: ignore[arg-type]


def rejects_a_missing_parameter() -> OrderPlacedV1:
    """Every templated parameter of `order_placed` V1 is required."""
    return OrderPlacedV1(  # type: ignore[call-arg]
        ik="ik",
        ledger_ik="prod",
        user_id="u",
    )


def rejects_a_parameter_of_the_wrong_type() -> OrderPlacedV1:
    return OrderPlacedV1(
        ik="ik",
        ledger_ik="prod",
        user_id=1,  # type: ignore[arg-type]
        order_id="o",
        order_cost="1000",
        currency="USD",
        platform_fee="100",
        driver_fee="200",
        restaurant_id="r",
        driver_id="d",
    )


def rejects_a_parameter_this_version_does_not_have() -> OrderPlacedV1:
    """`service_fee` arrived in V2. Asking V1 for it is the mistake the split prevents."""
    return OrderPlacedV1(  # type: ignore[call-arg]
        ik="ik",
        ledger_ik="prod",
        user_id="u",
        order_id="o",
        order_cost="1000",
        currency="USD",
        platform_fee="100",
        service_fee="50",
        driver_fee="200",
        restaurant_id="r",
        driver_id="d",
    )


def parameters_are_reachable_under_their_python_names(typed: OrderPlacedV1) -> str:
    """Snake_cased fields, and `PARAMETER_FIELDS` holding the Schema names."""
    schema_name: str = typed.PARAMETER_FIELDS["user_id"]
    typed.nonexistent_field  # type: ignore[attr-defined]
    return typed.order_cost + typed.driver_fee + schema_name


def to_input_is_the_raw_type(typed: OrderPlacedV1) -> AddLedgerEntryInput:
    """So a caller can adjust the payload before sending without losing types."""
    return typed.to_input()
