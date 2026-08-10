"""Tests for the paths where codegen degrades instead of failing.

Each produces a working SDK that is quietly worse than intended: a parameter
that lost its type, a batch method that does not typecheck, models nothing
accepts. The warning is the only signal, so it is what these assert on.

`addLedgerEntries` and its `entries` argument are owned upstream in
fragment-dev/graphql-queries. Neither degraded path is reachable from the
queries as they stand; they cover a rename of either name.

Offline; no credentials required.
"""

import ast
import logging
from pathlib import Path
from typing import Any, Dict

import pytest
from graphql import GraphQLSchema, OperationDefinitionNode, parse

from fragment.codegen.plugins.generate_typed_entries import GenerateTypedLedgerEntries
from fragment.codegen.typed_entries import extract_entry_spec

BATCH_METHOD = '''async def add_ledger_entries(
    self, entries: list[AddLedgerEntryInput], **kwargs: Any
) -> AddLedgerEntries:
    query = gql("""mutation addLedgerEntries { __typename }""")
    variables: dict[str, object] = {"entries": entries}
    response = await self.execute(query=query, variables=variables, **kwargs)
    return AddLedgerEntries.model_validate(self.get_data(response))'''

# Carries the `amount` annotation `typed_operation` needs, so extracting a spec
# from it does not trip the unresolvable-parameter warning on its own.
POST_METHOD = """async def post_thing(
    self, ik: Any, ledger_ik: Any, amount: str, **kwargs: Any
) -> PostThing:
    return PostThing.model_validate({})"""


@pytest.fixture(autouse=True)
def capture_console(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.WARNING, logger="console")


def plugin(tmp_path: Path) -> GenerateTypedLedgerEntries:
    config: Dict[str, Any] = {
        "tool": {
            "ariadne-codegen": {
                "target_package_path": str(tmp_path),
                "target_package_name": "sdk",
                "queries_path": "queries/",
            }
        }
    }
    return GenerateTypedLedgerEntries(GraphQLSchema(), config)


def method(source: str) -> ast.AsyncFunctionDef:
    node = ast.parse(source).body[0]
    assert isinstance(node, ast.AsyncFunctionDef)
    return node


def operation(source: str) -> OperationDefinitionNode:
    node = parse(source).definitions[0]
    assert isinstance(node, OperationDefinitionNode)
    return node


BATCH_OPERATION = operation(
    "mutation addLedgerEntries($entries: [AddLedgerEntryInput!]!) "
    "{ addLedgerEntries(entries: $entries) { __typename } }"
)


def typed_operation(name: str = "PostThing") -> OperationDefinitionNode:
    return operation(
        f"""mutation {name}($ik: SafeString!, $ledgerIk: SafeString!, $amount: String!) {{
          addLedgerEntry(
            ik: $ik
            entry: {{ledger: {{ik: $ledgerIk}}, type: "thing",
                    parameters: {{amount: $amount}}}}
          ) {{ __typename }}
        }}"""
    )


# --- Extraction ---------------------------------------------------------------


def test_unresolvable_parameter_type_warns_and_falls_back_to_any(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """A parameter with no matching client argument keeps its wire key.

    Dropping it would change the payload, so `Any` is the fallback; the cost is
    the caller's type checking on that one field.
    """
    spec = extract_entry_spec(typed_operation(), annotations={})
    assert spec is not None
    assert [(p.name, p.annotation) for p in spec.parameters] == [("amount", "Any")]

    assert "Could not resolve a type for parameter 'amount'" in caplog.text
    assert "PostThing" in caplog.text


def test_resolvable_parameter_type_warns_about_nothing(
    caplog: pytest.LogCaptureFixture,
) -> None:
    spec = extract_entry_spec(typed_operation(), annotations={"amount": "str"})
    assert spec is not None
    assert caplog.text == ""


def test_field_collision_names_the_parameter_that_moved(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """The rename is invisible in the payload, so the log is the only signal."""
    spec = extract_entry_spec(
        operation("""mutation PostThing($ik: SafeString!, $ledgerIk: SafeString!,
                                  $a: String!, $b: String!) {
              addLedgerEntry(
                ik: $ik
                entry: {ledger: {ik: $ledgerIk}, type: "thing",
                        parameters: {user_id: $a, userId: $b}}
              ) { __typename }
            }"""),
        annotations={"a": "str", "b": "str"},
    )
    assert spec is not None
    assert "'userId'" in caplog.text
    assert "'user_id_2'" in caplog.text
    assert "wire payload is unaffected" in caplog.text


# --- The batch method ---------------------------------------------------------


def test_missing_entries_argument_warns(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """A renamed argument costs callers their type checking."""
    renamed = method(BATCH_METHOD.replace("entries:", "items:", 1))
    instance = plugin(tmp_path)

    instance.generate_client_method(renamed, BATCH_OPERATION)

    assert not instance.widened_entries_argument
    assert "Could not find an 'entries' argument" in caplog.text
    assert "will not typecheck" in caplog.text


def test_missing_variables_assignment_warns(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """Widening without the coercion lets a non-list sequence reach json.dumps."""
    without_assignment = method(
        BATCH_METHOD.replace(
            'variables: dict[str, object] = {"entries": entries}', "pass"
        )
    )
    instance = plugin(tmp_path)

    instance.generate_client_method(without_assignment, BATCH_OPERATION)

    assert instance.widened_entries_argument
    assert "Could not find the 'entries' variables assignment" in caplog.text
    assert "fail to serialise" in caplog.text


def test_the_intact_batch_method_warns_about_nothing(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """An intact method is silent, so the warnings above mean what they say."""
    instance = plugin(tmp_path)

    rewritten = instance.generate_client_method(method(BATCH_METHOD), BATCH_OPERATION)

    assert instance.widened_entries_argument
    assert caplog.text == ""
    source = ast.unparse(rewritten)
    assert "Sequence[Union[AddLedgerEntryInput, TypedLedgerEntry]]" in source
    assert "{'entries': list(entries)}" in source


def test_typed_models_with_no_batch_operation_warns(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """Typed models with no batch method to accept them."""
    instance = plugin(tmp_path)
    instance.generate_client_method(method(POST_METHOD), typed_operation())

    instance.generate_init_code("__all__ = []\n")

    assert not instance.saw_batch_operation
    assert "found no 'addLedgerEntries' operation" in caplog.text


def test_seeing_the_batch_operation_warns_about_nothing(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    instance = plugin(tmp_path)
    instance.generate_client_method(method(POST_METHOD), typed_operation())
    instance.generate_client_method(method(BATCH_METHOD), BATCH_OPERATION)

    instance.generate_init_code("__all__ = []\n")

    assert caplog.text == ""


# --- What the plugin writes ---------------------------------------------------


def test_generate_init_code_writes_a_module_that_parses(tmp_path: Path) -> None:
    instance = plugin(tmp_path)
    instance.generate_client_method(method(POST_METHOD), typed_operation())
    instance.generate_client_method(method(BATCH_METHOD), BATCH_OPERATION)

    init_code = instance.generate_init_code("__all__ = []\n")

    written = (tmp_path / "sdk" / "typed_entries.py").read_text(encoding="utf-8")
    ast.parse(written)
    assert written.startswith("# Generated by fragment")
    assert "# Source: queries/" in written
    assert "class ThingV1(TypedLedgerEntry):" in written

    ast.parse(init_code)
    assert '"ThingV1",' in init_code
    assert "from .typed_entries import" in init_code


def test_generate_init_code_creates_the_package_directory(tmp_path: Path) -> None:
    """The hook does not depend on ariadne having made the directory first."""
    instance = plugin(tmp_path / "nested" / "deeper")
    instance.generate_init_code("__all__ = []\n")

    assert (tmp_path / "nested" / "deeper" / "sdk" / "typed_entries.py").exists()


def test_client_imports_are_only_added_when_the_argument_was_widened(
    tmp_path: Path,
) -> None:
    """An unwidened client imports no name it never references."""
    instance = plugin(tmp_path)
    code = "from typing import Any\n\nclass Client:\n    pass\n"

    assert instance.generate_client_code(code) == code

    instance.generate_client_method(method(BATCH_METHOD), BATCH_OPERATION)
    widened = instance.generate_client_code(code)

    assert "from .typed_entries import TypedLedgerEntry" in widened
    assert "from typing import Sequence" in widened
    ast.parse(widened)
