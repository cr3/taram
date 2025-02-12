"""Command-line interface."""

import json
import os
import sys
from argparse import (
    ArgumentParser,
    FileType,
    RawDescriptionHelpFormatter,
)
from collections import defaultdict
from textwrap import dedent

import requests
from lookuper import lookup
from more_itertools import bucket, only
from yarl import URL

DEFAULT_API_TIMEOUT = "10"
DEFAULT_API_URL = "https://taram.ca"

API_TIMEOUT = int(os.environ.get("TARAM_API_TIMEOUT", DEFAULT_API_TIMEOUT))
API_URL = os.environ.get("TARAM_API_URL", DEFAULT_API_URL)


def get_arg_type(arg, default=str):
    """OpenAPI data type to arg type."""
    return {
        "boolean": bool,
        "integer": int,
        "number": float,
        "string": str,
    }.get(arg, default)


def get_openapi_schema(api_url=API_URL, api_timeout=API_TIMEOUT):
    """Get and parse the OpenAPI schema from the API."""
    openapi_url = URL(api_url) / "openapi.json"
    response = requests.get(openapi_url, timeout=api_timeout)
    response.raise_for_status()
    return json.loads(response.content)


def call_api(method, path, args, keys, api_url=API_URL):
    """Make an API request with query parameters and request body."""
    values = bucket(args.items(), lambda a: keys.get(a[0]))
    values = defaultdict(dict, {k: dict(values[k]) for k in values})
    url = URL(api_url).with_path(path.format(**values["path"]))

    headers = {"Content-Type": "application/json"} if values["body"] else {}
    response = requests.request(
        method.upper(),
        url,
        params=values["query"],
        json=values["body"],
        headers=headers,
    )

    return response.json()


def make_args_parser(schema):
    epilog = dedent(f"""\
    environments:
      TARAM_API_TIMEOUT Seconds to wait for the API (default: {DEFAULT_API_TIMEOUT})
      TARAM_API_URL     URL of the API (default: {DEFAULT_API_URL})
    """)
    args_parser = ArgumentParser(
        epilog=epilog,
        formatter_class=RawDescriptionHelpFormatter,
    )
    args_parser.add_argument(
        "--output",
        type=FileType("w"),
        default=sys.stdout,
        help="output file (default: stdout)",
    )
    command = args_parser.add_subparsers(
        dest="command",
    )

    # Add schema paths.
    for path, methods in schema.get("paths", {}).items():
        for method, details in methods.items():
            default_name = f"{method}_{path.strip('/').replace('/', '_')}"
            command_name = details.get("operationId", default_name)
            command_parser = command.add_parser(
                command_name,
                help=details.get("summary", "No summary available"),
            )

            # Add query/path parameters.
            keys = {}
            for param in details.get("parameters", []):
                keys[param["name"]] = param["in"]
                required = param.get("required", False)
                param_name = param["name"] if required else f"--{param['name']}"
                param_type = get_arg_type(param["schema"].get("type"))
                command_parser.add_argument(
                    param_name,
                    type=param_type,
                    help=param["schema"].get("title"),
                )

            # Add requestBody properties.
            if content_schema := only(lookup(details, "requestBody", "content", "application/json", "schema")):
                if ref := content_schema.get("$ref"):
                    content_schema = only(lookup(schema, *ref.split("/")[1:]))

                for prop_name, prop_details in content_schema.get("properties", {}).items():

                    keys[prop_name] = "body"
                    required = prop_name in content_schema.get("required", [])
                    arg_name = prop_name if required else f"--{prop_name}"
                    arg_type = get_arg_type(param["schema"].get("type"))
                    command_parser.add_argument(
                        arg_name,
                        type=arg_type,
                        default=prop_details.get("default"),
                        help=prop_details.get("title"),
                    )

            command_parser.set_defaults(
                func=lambda args, m=method, p=path, keys=keys: call_api(m, p, args, keys),
            )

    return args_parser


def main(argv=None, api_url=API_URL):
    """Entry point to the taram command-line interface."""
    schema = get_openapi_schema(api_url)
    parser = make_args_parser(schema)
    args = parser.parse_args(argv)
    data = args.func(vars(args))
    output = json.dumps(data, indent=2)
    args.output.write(output)
