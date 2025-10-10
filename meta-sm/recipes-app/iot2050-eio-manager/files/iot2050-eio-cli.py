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
import time
from concurrent.futures import ThreadPoolExecutor
from progress.bar import Bar
import grpc
from gRPC.EIOManager.iot2050_eio_pb2 import (
    DeployRequest,
    RetrieveRequest,
    UpdateFirmwareRequest
)
from gRPC.EIOManager.iot2050_eio_pb2_grpc import EIOManagerStub
from iot2050_eio_global import (
    iot2050_eio_api_server,
    EIO_FWU_MAP3_FW_BIN
)
from iot2050_eio_fwu_monitor import (
    do_fwu_check
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


def show_progress_bar(task, interval):
    with Bar('Updating'.ljust(15), fill='.', bar_prefix='',
             bar_suffix='', suffix='') as bar:
        while True:
            bar.next()
            if task.done():
                break
            time.sleep(interval)


def do_update_firmware(firmwares):
    with grpc.insecure_channel(iot2050_eio_api_server) as channel:
        stub = EIOManagerStub(channel)
        print("===================================================")
        print("EIO firmware update started - DO NOT INTERRUPT!")
        print("===================================================")
        for entity in firmwares:
            with ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(
                    stub.UpdateFirmware,
                    UpdateFirmwareRequest(firmware=firmwares[entity],
                                          entity=entity)
                )
                show_progress_bar(future, 0.3)
            print()

    response = future.result()
    print(f"Extended IO firmware update result: {response.status}")
    print(f"Extended IO firmware update message: {response.message}")
    return response


if __name__ == "__main__":
    description=textwrap.dedent('''\
        Extended IO command line tool

        Examples:
        1. %(prog)s config deploy config.yaml
            Deploy the config.yaml to Extended IO Controller
        2. %(prog)s config retrieve config.yaml
            Retrieve the config from Extended IO Controller and store into config.yaml
        3. %(prog)s fwu controller [firmware.bin]
            Update firmware for Extended IO Controller, using firmware.bin if provided,
            otherwise using the stock firmware file.

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

    fwu_parser = subparsers.add_parser("fwu", help='firmware update help')
    fwu_subparsers = fwu_parser.add_subparsers(help='sub-command help',
                                       title='fwu-commands',
                                       dest="fwu_command")
    controller_parser = fwu_subparsers.add_parser("controller", help='controller help')
    controller_parser.add_argument('firmware', nargs='?', metavar='FIRMWARE',
                                   type=argparse.FileType('rb'),
                                   help='Firmware file')

    args = parser.parse_args()

    if args.command == 'config':
        status, message = do_fwu_check()
        if status != 0:
            print(message)
            continue_op = input(
                "\nWarning: Please fix above issue before continue. Continue? (y/N) "
            )
            if continue_op != "y":
                sys.exit(0)

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
    elif args.command == 'fwu':
        if args.fwu_command == 'controller':
            firmwares = {}
            # Map3 firmware
            if args.firmware:
                firmwares[0] = args.firmware.read()
            else:
                firmwares[0] = open(EIO_FWU_MAP3_FW_BIN, "rb").read()
                status, message = do_fwu_check()
                if status == 0:
                    # no need to update!
                    print(message)
                    sys.exit(0)

            response = do_update_firmware(firmwares)
            if response.status:
                print(f"ERROR: {response.message}")
                print("EIO firmware update failed, please try again!")
                sys.exit(1)

        print("EIO firmware update completed. Please reboot the device.")
    else:
        parser.print_help(sys.stderr)
        sys.exit(1)
