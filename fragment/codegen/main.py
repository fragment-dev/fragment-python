import contextlib
import logging
import sys
import tempfile
from typing import Iterator

import click
import httpx
from ariadne_codegen.main import client as generate_graphql_client

from fragment.codegen.helpers import get_codegen_config, get_standard_queries
from fragment.logger import console_log

logging.getLogger("httpx").setLevel(logging.WARNING)


GRAPHQL_SCHEMA_API_URL = "https://api.us-west-2.fragment.dev/schema.graphql"


@contextlib.contextmanager
def resolved_schema_path(schema_path: str | None) -> Iterator[str]:
    """Yield a path to the schema to generate against.

    A local path is used as-is, which keeps generation reproducible and offline.
    Without one the current schema is downloaded to a temporary file, so output
    depends on whatever the API looks like at that moment.
    """
    if schema_path is not None:
        console_log.info(f"Using the GraphQL schema at {schema_path}")
        yield schema_path
        return

    console_log.info(f"Downloading the GraphQL schema from {GRAPHQL_SCHEMA_API_URL}")
    try:
        response = httpx.get(GRAPHQL_SCHEMA_API_URL)
    except httpx.RequestError as error:
        console_log.error(f"An error occurred while downloading the schema: {error}")
        sys.exit(1)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".graphql") as schema_file:
        schema_file.write(response.text)
        schema_file.flush()
        yield schema_file.name


@click.command()
@click.option(
    "-i",
    "--input-dir",
    default=None,
    help="Path to your Schema queries",
    required=True,
)
@click.option(
    "-n",
    "--target-package-name",
    default="fragment_graphql_client",
    help="The package name for the generated SDK",
    required=False,
)
@click.option(
    "-o",
    "--output-dir",
    default=None,
    help="The output directory for the generated SDK. Defaults to CWD.",
    required=False,
)
@click.option(
    "-s",
    "--schema-path",
    default=None,
    type=click.Path(exists=True, dir_okay=False, readable=True),
    help=(
        "Path to a local GraphQL schema. Defaults to downloading the current "
        "schema. Pass a file to make generation reproducible and offline."
    ),
    required=False,
)
@click.option(
    "--sync",
    help="Generate a synchronous client. Defaults to async.",
    required=False,
    is_flag=True,
)
def run(input_dir, target_package_name, sync, output_dir=None, schema_path=None):
    with resolved_schema_path(schema_path) as resolved, tempfile.NamedTemporaryFile(
        dir=input_dir, mode="w", suffix=".graphql"
    ) as standard_query_file:
        # Write and flush the standard queries to the provided input
        standard_query_file.write(get_standard_queries())
        standard_query_file.flush()
        config_dict = get_codegen_config(
            use_sync_client=sync,
            schema_path=resolved,
            queries_path=input_dir,
            target_package_name=target_package_name,
            target_package_path=output_dir,
        )
        generate_graphql_client(config_dict)
