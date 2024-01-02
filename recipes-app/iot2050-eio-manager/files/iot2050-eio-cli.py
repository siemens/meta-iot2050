#!/usr/bin/env python3
#
# Copyright (c) Siemens AG, 2023
#
# Authors:
#  Su Bao Cheng <baocheng.su@siemens.com>
#
# SPDX-License-Identifier: MIT
import argparse
import sys
import textwrap
import grpc
from gRPC.EIOManager.iot2050_eio_pb2 import (
    DeployRequest,
    RetrieveRequest
)
from gRPC.EIOManager.iot2050_eio_pb2_grpc import EIOManagerStub
from iot2050_eio_global import (
    iot2050_eio_api_server
)


def do_deploy(yaml_data):
    with grpc.insecure_channel(iot2050_eio_api_server) as channel:
        stub = EIOManagerStub(channel)
        response = stub.Deploy(DeployRequest(yaml_data=yaml_data))
    print(f"Extended IO config deploy result: {response.status}")
    print(f"Extended IO config deploy message: {response.message}")


def do_retrieve():
    with grpc.insecure_channel(iot2050_eio_api_server) as channel:
        stub = EIOManagerStub(channel)
        response = stub.Retrieve(RetrieveRequest(name="dummy"))
    print(f"Extended IO config retrieve result: {response.status}")
    print(f"Extended IO config retrieve message: {response.message}")

    return response.yaml_data


if __name__ == "__main__":
    description=textwrap.dedent('''\
        Extended IO command line tool

        Examples:
        1. %(prog)s config deploy config.yaml
            Deploy the config.yaml to Extended IO Controller
        2. %(prog)s config retrieve config.yaml
            Retrieve the config from Extended IO Controller and store into config.yaml

        Example Configuration File:

        Please check /usr/lib/iot2050/eio/config-template/sm-config-example.yaml for full config
        And check /usr/lib/iot2050/eio/config-template/mlfb-XXX.yaml for specific module

        ''')
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(help='sub-command help',
                                       title='sub-commands',
                                       dest="command")

    config_parser = subparsers.add_parser("config", help='config help')
    config_parser.add_argument('action', metavar='ACTION',
                        choices=['deploy', 'retrieve'],
                        help='Action, deploy or retrieve')
    config_parser.add_argument('config', metavar='CONFIG_YAML', type=str,
                        help='Config file in yaml format')

    args = parser.parse_args()

    if args.command == 'config':
        if args.action == "deploy":
            with open(args.config, 'r', encoding='ascii') as f_config:
                do_deploy(f_config.read())
        else:
            config_returned = do_retrieve()
            if config_returned == "":
                print("Unable to retrieve config!")
                sys.exit(1)

            with open(args.config, 'w', encoding='ascii') as f_config:
                f_config.write(config_returned)
    else:
        parser.print_help(sys.stderr)
        sys.exit(1)
