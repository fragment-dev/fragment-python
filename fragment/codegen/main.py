import logging
import sys
import tempfile

import click
import httpx
from ariadne_codegen.main import client as generate_graphql_client

from fragment.codegen.helpers import get_codegen_config, get_standard_queries
from fragment.logger import console_log

logging.getLogger("httpx").setLevel(logging.WARNING)


GRAPHQL_SCHEMA_API_URL = "https://api.us-west-2.fragment.dev/schema.graphql"


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
    "--sync",
    help="Generate a synchronous client. Defaults to async.",
    required=False,
    is_flag=True,
)
def run(input_dir, target_package_name, sync, output_dir=None):
    console_log.info(f"Downloading the GraphQL schema from {GRAPHQL_SCHEMA_API_URL}")
    try:
        r = httpx.get(GRAPHQL_SCHEMA_API_URL)
        with tempfile.NamedTemporaryFile(
            mode="w"
        ) as schema_file, tempfile.NamedTemporaryFile(
            dir=input_dir, mode="w", suffix=".graphql"
        ) as standard_query_file:
            # Write and flush the most recent schema
            schema_file.write(r.text)
            schema_file.flush()
            # Write and flush the standard queries to the provided input
            standard_query_file.write(get_standard_queries())
            standard_query_file.flush()
            config_dict = get_codegen_config(
                use_sync_client=sync,
                schema_path=schema_file.name,
                queries_path=input_dir,
                target_package_name=target_package_name,
                target_package_path=output_dir,
            )
            generate_graphql_client(config_dict)
    except httpx.RequestError as e:
        console_log.error(f"An error occurred while downloading the schema: {e}")
        sys.exit(1)
