import os
from pathlib import Path
from typing import Dict, Optional


def get_project_path_relative_to_file(path: str) -> str:
    """
    Get the relative path of a file in the project.
    It is important that this function is in the same directory
    as the commandline entrypoint.
    """
    resolved_path = Path(__file__, path).resolve()
    return os.path.relpath(resolved_path)


def get_codegen_config(
    *,
    schema_path: str,
    queries_path: str,
    target_package_name: str,
    target_package_path: Optional[str] = None,
    use_sync_client: bool = False,
) -> Dict:
    """Get the configuration for the codegen tool."""
    client_name, file_path = (
        ("AsyncFragmentClient", "../../client/async_client.py")
        if not use_sync_client
        else ("SyncFragmentClient", "../../client/sync_client.py")
    )
    return dict(
        tool={
            "ariadne-codegen": dict(
                schema_path=schema_path,
                queries_path=queries_path,
                target_package_name=target_package_name,
                target_package_path=(
                    target_package_path if target_package_path else Path.cwd()
                ),
                base_client_name=client_name,
                base_client_file_path=get_project_path_relative_to_file(file_path),
                async_client=False if use_sync_client else True,
                # Order matters. GenerateTypedLedgerEntries copies annotations
                # off the generated client methods, so it has to run after
                # RewriteUnsetTypeMethodArguments has turned
                # `Union[Optional[X], UnsetType]` into `Optional[X]`. Listed
                # earlier, it emits `UnsetType` into a module that never imports
                # it. collect_annotations raises if that ever happens.
                plugins=[
                    "fragment.codegen.plugins.get_file_comment.GenerateFileComment",
                    "fragment.codegen.plugins.generate_client_method.RewriteUnsetTypeMethodArguments",
                    "fragment.codegen.plugins.generate_typed_entries.GenerateTypedLedgerEntries",
                ],
            ),
        },
    )


def get_standard_queries() -> str:
    """Get the standard SDK queries for the codegen tool."""
    standard_query_file_path = get_project_path_relative_to_file(
        "../../std_queries/queries.graphql"
    )
    return Path(standard_query_file_path).read_text()
