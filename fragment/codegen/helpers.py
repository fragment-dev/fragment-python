import os
from pathlib import Path
from typing import Dict


def get_project_path_relative_to_file(path: str) -> str:
    """
    Get the relative path of a file in the project.
    It is important that this function is in the same directory
    as the commandline entrypoint.
    """
    resolved_path = Path(__file__, path).resolve()
    return os.path.relpath(resolved_path)


def get_codegen_config(
    *, schema_path: str, queries_path: str, target_package_name: str
) -> Dict:
    """ Get the configuration for the codegen tool. """
    return dict(
        tool={
            "ariadne-codegen": dict(
                schema_path=schema_path,
                queries_path=queries_path,
                target_package_name=target_package_name,
                base_client_name="AsyncFragmentClient",
                base_client_file_path=get_project_path_relative_to_file(
                    "../../client/async_client.py"
                ),
                plugins=[
                    "fragment.codegen.plugins.generate_client_method.RewriteUnsetTypeMethodArguments"
                ],
            ),
        },
    )


def get_standard_queries() -> str:
    """ Get the standard SDK queries for the codegen tool. """
    standard_query_file_path = get_project_path_relative_to_file(
        "../../std_queries/queries.graphql"
    )
    return Path(standard_query_file_path).read_text()
