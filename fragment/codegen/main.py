import errno
import logging
import os
from pathlib import Path

import httpx
from ariadne_codegen.main import client as generate_graphql_client

from fragment.logger import console_log

logging.getLogger("httpx").setLevel(logging.WARNING)

config_dict = dict(
    tool={
        "ariadne-codegen": dict(
            schema_path="schema.graphql",
            queries_path="queries/",
            target_package_name="fragment_graphql_client",
            base_client_name="AsyncFragmentClient",
            base_client_file_path="fragment/client/async_client.py",
            plugins=["fragment.codegen.plugins.generate_client_method.RewriteUnsetTypeMethodArguments"],
        ),
    },
)


def remove_if_file_exists(filename: str):
    try:
        os.remove(filename)
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise


def run():
    console_log.info(
        "Downloading the GraphQL schema from https://api.us-west-2.fragment.dev/schema.graphql"
    )
    r = httpx.get("https://api.fragment.dev/schema.graphql")
    with open("schema.graphql", "w") as f:
        f.write(r.text)
    try:
        generate_graphql_client(config_dict)
    finally:
        remove_if_file_exists("schema.graphql")
