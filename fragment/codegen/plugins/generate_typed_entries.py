import ast
from pathlib import Path

from ariadne_codegen.plugins.base import Plugin
from graphql import OperationDefinitionNode

from fragment.codegen.typed_entries import (
    MODULE_NAME,
    EntrySpec,
    collect_annotations,
    extract_entry_spec,
    render_module,
    resolve_class_names,
)
from fragment.logger import console_log

ADD_LEDGER_ENTRIES_OPERATION = "addLedgerEntries"
ENTRIES_ARGUMENT = "entries"


class GenerateTypedLedgerEntries(Plugin):
    """Emit strongly-typed `addLedgerEntries` payload models.

    `addLedgerEntries` accepts a list of a single input type whose `parameters`
    field is an opaque `JSON` scalar, so GraphQL alone cannot type an individual
    entry in a batch. The per-entry-type `addLedgerEntry` operations already in
    the input queries do carry that information, so this plugin recovers it and
    renders one pydantic model per entry type into a `typed_entries` module.

    Specs are collected in `generate_client_method`, which ariadne calls for
    every operation. The module is written in `generate_init_code`, the last
    hook to run, by which point every operation has been seen.
    """

    def __init__(self, schema, config_dict: dict) -> None:
        super().__init__(schema, config_dict)
        settings = config_dict.get("tool", {}).get("ariadne-codegen", {})
        self.package_path = Path(
            settings.get("target_package_path", Path.cwd())
        ) / settings.get("target_package_name", "graphql_client")
        self.specs: list[EntrySpec] = []
        # Both names below are owned upstream in fragment-dev/graphql-queries,
        # so track whether each was actually seen rather than assuming.
        self.saw_batch_operation = False
        self.widened_entries_argument = False

    def generate_client_method(
        self,
        method_def: ast.FunctionDef | ast.AsyncFunctionDef,
        operation_definition: OperationDefinitionNode,
    ) -> ast.FunctionDef | ast.AsyncFunctionDef:
        annotations: dict[str, str] = collect_annotations(
            method_def, operation_definition
        )
        spec = extract_entry_spec(operation_definition, annotations)
        if spec is not None:
            self.specs.append(spec)
        if (
            operation_definition.name
            and operation_definition.name.value == ADD_LEDGER_ENTRIES_OPERATION
        ):
            self.saw_batch_operation = True
            self._widen_entries_argument(method_def)
        return method_def

    def _widen_entries_argument(
        self, method_def: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> None:
        """Let `add_ledger_entries` take typed entries as well as raw inputs.

        ariadne annotates the argument `list[AddLedgerEntryInput]`, which typed
        entries satisfy at runtime but not under a type checker. Widening to a
        `Sequence` of either keeps raw inputs working while accepting typed
        models directly -- `Sequence` because `list` is invariant, so
        `list[AuthCapture]` would otherwise be rejected.
        """
        for arg in method_def.args.args:
            if arg.arg != ENTRIES_ARGUMENT:
                continue
            # Parsed rather than hand-built: an ast.Name whose id is an entire
            # expression unparses fine but is not a valid tree, so anything that
            # visits or compiles it breaks.
            arg.annotation = ast.parse(
                "Sequence[Union[AddLedgerEntryInput, TypedLedgerEntry]]",
                mode="eval",
            ).body
            self.widened_entries_argument = True
            return

        console_log.warning(
            "Could not find an %r argument on the generated add_ledger_entries "
            "method, so its signature was left as-is. Typed entry payloads will "
            "still serialise correctly but will not typecheck when passed to it.",
            ENTRIES_ARGUMENT,
        )

    def generate_client_code(self, generated_code: str) -> str:
        if not self.widened_entries_argument:
            return generated_code
        return self._insert_imports(
            generated_code,
            [
                "from typing import Sequence",
                f"from .{MODULE_NAME} import TypedLedgerEntry",
            ],
        )

    @staticmethod
    def _insert_imports(code: str, imports: list[str]) -> str:
        """Insert imports after the module's existing top-level import block."""
        lines = code.splitlines()
        last_import_line = 0
        for node in ast.parse(code).body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                last_import_line = max(last_import_line, node.end_lineno or 0)
        lines[last_import_line:last_import_line] = imports
        return "\n".join(lines) + "\n"

    def generate_init_code(self, generated_code: str) -> str:
        if self.specs and not self.saw_batch_operation:
            # Typed payloads exist but no batch operation was generated to take
            # them. Silence here would leave users with models nothing accepts.
            console_log.warning(
                "Generated %d typed entry payload(s) but found no %r operation, "
                "so no batch method accepts them. Has the operation been renamed "
                "upstream?",
                len(self.specs),
                ADD_LEDGER_ENTRIES_OPERATION,
            )
        module_path = self.package_path / f"{MODULE_NAME}.py"
        module_path.parent.mkdir(parents=True, exist_ok=True)
        module_path.write_text(
            self._add_comment(render_module(self.specs)), encoding="utf-8"
        )
        return generated_code + self._init_additions()

    def _add_comment(self, code: str) -> str:
        # This module is written directly rather than through ariadne's module
        # pipeline, so it does not pass through the GenerateFileComment hook.
        queries_path = (
            self.config_dict.get("tool", {})
            .get("ariadne-codegen", {})
            .get("queries_path", "")
        )
        comment = "# Generated by fragment (with the help of ariadne-codegen)"
        if queries_path:
            comment += f"\n# Source: {queries_path}"
        return f"{comment}\n\n{code}"

    def _init_additions(self) -> str:
        """Re-export the typed models and extend `__all__`.

        Resolves names itself; `resolve_class_names` being pure is what makes this
        agree with the renderer without depending on hook order.
        """
        names = ["TypedLedgerEntry", "to_entry_inputs"] + [
            class_name for class_name, _ in resolve_class_names(self.specs)
        ]
        names.sort()
        imported = ",\n    ".join(names)
        exported = "\n".join(f'    "{name}",' for name in names)
        return (
            f"\nfrom .{MODULE_NAME} import (\n    {imported},\n)\n"
            f"\n__all__ += [\n{exported}\n]\n"
        )
