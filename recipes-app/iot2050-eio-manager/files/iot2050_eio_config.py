#!/usr/bin/env python3
#
# Copyright (c) Siemens AG, 2023
#
# Authors:
#  Su Bao Cheng <baocheng.su@siemens.com>
#
# SPDX-License-Identifier: MIT
import struct
from abc import ABC, abstractmethod
from typing import List, Dict
import zlib
import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
import bitstruct
from jsonschema import RefResolver
from jsonschema.exceptions import ValidationError
from jsonschema import Draft202012Validator
from iot2050_eio_global import (
    EIO_FS_CONTROL,
    EIO_FS_CONFIG,
    eio_schema_top,
    eio_schema_refs
)


class ModuleSerDes(ABC):
    """Abstract class for module (de)/serializer"""
    @abstractmethod
    def __init__(self, mlfb):
        self.mlfb = mlfb

    @abstractmethod
    def serialize(self, config: Dict) -> bytes:
        """Serialize the configuration to data blob

        Args:
            config (Dict): configuration dict

        Returns:
            bytes: blob
        """

    @abstractmethod
    def deserialize(self, blob: bytes) -> Dict:
        """Deserialize the configuration from data blob

        Args:
            blob (bytes): data blob

        Returns:
            Dict: configuration
        """


class SM1223SerDes(ModuleSerDes):
    """SM1223 Configuration (de)/serializer"""
    def __init__(self, mlfb):
        super().__init__(mlfb)
        header_fmt = 'p8 u8'
        di_ch_fmt = 'p8 p4u4'
        dq_ch_fmt = 'p8 u1p1u2p1p3'
        self.serdesfmt = ''.join([header_fmt, di_ch_fmt * 8, header_fmt, dq_ch_fmt * 8])

    def serialize(self, config: Dict) -> bytes:
        parameters = [0x02]
        for i in range(0, 8):
            if i < 4:
                parameters.append(config['di']['ch0_3_delay_time'])
            else:
                parameters.append(config['di']['ch4_7_delay_time'])
        parameters.append(0x02)
        for i in range(0, 8):
            parameters.append(config['dq'][f'ch{i}']['substitute'])
            parameters.append(config['dq']['behavior_with_OD'])
        return bitstruct.pack(self.serdesfmt, *parameters)

    def deserialize(self, blob: bytes) -> Dict:
        config = {
            "description": "SM 1223 DI8 x 120VAC / DQ8 x relay",
            "mlfb": self.mlfb,
            "di": {
                "ch0_3_delay_time": "",
                "ch4_7_delay_time": ""
            },
            "dq": {
                "behavior_with_OD": "",
                "ch0": {"substitute": ""},
                "ch1": {"substitute": ""},
                "ch2": {"substitute": ""},
                "ch3": {"substitute": ""},
                "ch4": {"substitute": ""},
                "ch5": {"substitute": ""},
                "ch6": {"substitute": ""},
                "ch7": {"substitute": ""}
            }
        }

        _, \
        config['di']['ch0_3_delay_time'], _, _, _, \
        config['di']['ch4_7_delay_time'], _, _, _, \
        _, \
        config['dq']['ch0']['substitute'], config['dq']['behavior_with_OD'], \
        config['dq']['ch1']['substitute'], _, \
        config['dq']['ch2']['substitute'], _, \
        config['dq']['ch3']['substitute'], _, \
        config['dq']['ch4']['substitute'], _, \
        config['dq']['ch5']['substitute'], _, \
        config['dq']['ch6']['substitute'], _, \
        config['dq']['ch7']['substitute'], _ = bitstruct.unpack(self.serdesfmt, blob)
        return config


class SM1223AI8SerDes(ModuleSerDes):
    """SM1223 8AI Configuration (de)/serializer"""
    def __init__(self, mlfb):
        super().__init__(mlfb)
        header_fmt = 'p8 u8'
        ch_fmt = 'u8 u8 p8 u4u4 p8p8 b1b1p1b1p3b1 p8 p144'
        self.serdesfmt = ''.join([header_fmt, ch_fmt * 8])

    def serialize(self, config: Dict) -> bytes:
        parameters = [0x1A]
        for i in range(0, 8):
            parameters.extend([
                config[f'ch{i}']['type'],
                config[f'ch{i}']['range'],
                config['integ_time'],
                config[f'ch{i}']['smooth'],
                config[f'ch{i}']['overflow_alarm'],
                config[f'ch{i}']['underflow_alarm'],
                config[f'ch{i}']['open_wire_alarm'],
                config['power_alarm']
            ])

        return bitstruct.pack(self.serdesfmt, *parameters)

    def deserialize(self, blob: bytes) -> Dict:
        config = {
            "description": "Analog input module AI8 x 13 bits",
            "mlfb": self.mlfb
        }

        unpack_statement = '_'
        for i in range(0, 8):
            config[f'ch{i}'] = {}
            integ_time_ele = "config['integ_time']" if i == 0 else "_"
            power_alarm_ele = "config['power_alarm']" if i == 0 else "_"
            unpack_statement = ','.join([
                unpack_statement,
                f"config['ch{i}']['type']",
                f"config['ch{i}']['range']",
                integ_time_ele,
                f"config['ch{i}']['smooth']",
                f"config['ch{i}']['overflow_alarm']",
                f"config['ch{i}']['underflow_alarm']",
                f"config['ch{i}']['open_wire_alarm']",
                power_alarm_ele
                ])
        unpack_statement += ' = bitstruct.unpack(self.serdesfmt, blob)'
        exec(unpack_statement) # pylint: disable=exec-used
        return config


class NoModSerDes(ModuleSerDes):
    """No module configuration (de)/serializer"""
    def __init__(self, mlfb):
        super().__init__(mlfb)

    def serialize(self, config: Dict) -> bytes:
        return bytearray()

    def deserialize(self, blob: bytes) -> Dict:
        return {
            "description": "No module for this slot",
            "mlfb": self.mlfb
        }


class ModSerDesFactory(object):
    @classmethod
    def produce(cls, mlfb='NA') -> ModuleSerDes:
        mlfb = mlfb.rstrip('\0')
        if mlfb == '6ES7223-1QH32-0XB0':
            return SM1223SerDes(mlfb)
        elif mlfb == '6ES7231-4HF32-0XB0':
            return SM1223AI8SerDes(mlfb)
        else:
            return NoModSerDes(mlfb)


class EIOConfigSerDes():
    """Extended IO configuration serializer and deserializer
    
    The data struct of the binary format of the configuration data:

    struct config_data {
        char magic[4];      // must be 0x02, 0x00, 0x05, 0x00
        uint32_t version;   // configuration data version
        uint32_t blob_len;  // slots data blob length, in bytes
        uint32_t checksum;  // crc32 checksum, use 0x0 as placeholder when calculating.
        struct slot_blob blob[6];     // slots data blob
    };

    struct slot_blob {
        uint32_t slot_blob_len;  // length of this slot blob, in bytes
        char mlfb[20];           // ascii string of the mlfb
        uint32_t version;        // slot configuration data version
        uint8_t data[];          // real configuration data, module specific.
    };

    all the members of both structs are in big-endian.
    """

    @staticmethod
    def _calc_checksum(blob: bytes) -> int:
        new_blob = bytearray(blob)
        struct.pack_into('>I', new_blob, 12, 0)
        checksum = zlib.crc32(new_blob)
        return checksum

    @classmethod
    def convert2blob(cls, config: Dict) -> bytes:
        """Convert dict config data to blob format

        Then the blob data could be deployed into the external IO controller.

        Args:
            config (Dict): Config data, which is normally read from yaml file or
            passed in from webUI.

        Returns:
            bytes: Config data blob
        """
        pack_fmt_head = '> 4B 3I'
        pack_fmt = pack_fmt_head
        slot_pack_fmt_head = '> I 20s I'
        slot_blobs = []
        for i in range(1, 7):
            slot_pack_fmt = slot_pack_fmt_head
            slot_config = config[f"slot{i}"]
            serdes = ModSerDesFactory.produce(slot_config['mlfb'])
            slot_blob = serdes.serialize(slot_config)
            slot_pack_fmt += f' {len(slot_blob)}s'

            slot_blob = struct.pack(slot_pack_fmt,
                len(slot_blob) + struct.calcsize(slot_pack_fmt_head),
                bytes(slot_config['mlfb'], 'ascii'),
                0x01,
                slot_blob)
            slot_blobs.append(slot_blob)
            pack_fmt += f' {len(slot_blob)}s'

        total_len = struct.calcsize(pack_fmt) - struct.calcsize(pack_fmt_head)

        blob = bytearray(struct.pack(pack_fmt,
            0x02, 0x00, 0x05, 0x00,
            0x01,
            total_len,
            0, # Checksum placeholder
            *slot_blobs))

        # Updates the checksum
        checksum = cls._calc_checksum(blob)
        struct.pack_into('>I', blob, 12, checksum)
        return bytes(blob)

    @staticmethod
    def _get_next_slot_blob(blob: bytes) -> List:
        """Expand slots blob.
        
        Extract metadata such as blob length, mlfb, version, and slot
        blob data of all slots.

        Args:
            blob (bytes): Blob data that contains zero or more slots.

        Raises:
            ValueError: The blob data is in bad integrity

        Returns:
            List: Each is a slot metadata tuple (length, mlfb, version,
            slot_blob), the last element is an empty tuple ()
        """
        if len(blob) == 0:
            return [()]
        if len(blob) < (4 + 20 + 4):
            raise ValueError('Blob size does not match, slot data corrupted!')
        length, _ = struct.unpack(f'> I {len(blob) - 4}s', blob)
        length, mlfb, version, slot_blob, blob_rest = struct.unpack(
            f'> I 20s I {length - 20 - 8}s {len(blob) - length}s', blob)

        return [(length, mlfb, version, slot_blob), *EIOConfigSerDes._get_next_slot_blob(blob_rest)]

    @classmethod
    def convert2config(cls, blob: bytes) -> Dict:
        """Convert configration blob data to dict

        Args:
            blob (bytes): Configuration data in blob format

        Raises:
            ValueError: Blob size does not match, data corrupted

        Returns:
            Dict: Configration data in dict format, which could be
            easily dumpped into yaml or json.
        """
        pack_fmt_head = '> 4B 3I'
        slots_size = len(blob) - struct.calcsize(pack_fmt_head)
        unpack_fmt = pack_fmt_head + f' {slots_size}s'
        _, _, _, _, _, slots_size_unpacked, checksum, slots = struct.unpack(unpack_fmt, blob)
        if slots_size_unpacked != slots_size:
            raise ValueError('Blob size does not match, data corrupted!')
        if checksum != cls._calc_checksum(blob):
            raise ValueError('Checksum does not match, data corrupted!')

        slot_blobs = cls._get_next_slot_blob(slots)
        slot_blobs.pop() # Remove the last empty tuple

        slot_configs = [ModSerDesFactory.produce(str(mlfb, 'ascii')).deserialize(blob)
            for _, mlfb, _, blob in slot_blobs]
        config = {}
        for i in range(0, len(slot_configs)):
            index = i + 1
            config[f'slot{index}'] = slot_configs[i]

        return config


class ConfigError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class EIOConfigValidator(object):
    def __init__(self) -> None:
        with open(eio_schema_top, 'r', encoding='ascii') as f:
            schema_top = yaml.load(f.read(), Loader=Loader)

        ref_store = {}
        for ref in eio_schema_refs:
            with open(ref, 'r', encoding='ascii') as f:
                ref_schema = yaml.load(f.read(), Loader=Loader)
                ref_store[ref_schema["$id"]] = ref_schema

        self._schema_validator = Draft202012Validator(
            schema = schema_top,
            resolver = RefResolver(schema_top["$id"], schema_top, store=ref_store)
        )

    def validate_schema(self, instance):
        try:
            self._schema_validator.validate(instance)
        except ValidationError as e:
            msg = f"{e.message} @ {e.schema_path}"
            print(msg)
            raise ConfigError(f"Invalid config data: {msg}") from e

    def validate_semantic(self, config):
        # Check holes in slot chain
        last_mod = 0
        for i in range(1, 7):
            if f"slot{i}" in config:
                if last_mod > 0 and config[f"slot{i}"]["mlfb"] != "NA":
                    raise ConfigError(f"Invalid config: slot {i} is after an empty slot!")
                elif config[f"slot{i}"]["mlfb"] != "NA":
                    continue
                else:
                    last_mod = i

        # For 6ES7231-4HF32-0XB0 (or SM 1231-8AI), channels should be paired to
        # be the same measurement type
        for i in range(1, 7):
            slot_conf = config[f"slot{i}"]
            if slot_conf["mlfb"] != "6ES7231-4HF32-0XB0":
                continue
            for j in range(0, 8, 2):
                ch_prev_type = slot_conf[f"ch{j}"]["type"]
                ch_next_type = slot_conf[f"ch{j+1}"]["type"]
                if ch_prev_type != ch_next_type:
                    raise ConfigError(
                        f"Invalid config: slot{i}: ch{j}.type != ch{j+1}.type")


class EIOConfigParser(object):
    def __init__(self, config_yaml: str) -> None:
        self._config: dict = yaml.load(config_yaml, Loader=Loader)
        self._validator = EIOConfigValidator()

    def validate(self):
        self._validator.validate_schema(self._config)
        self._validator.validate_semantic(self._config)

    def transform(self) -> bytes:
        return EIOConfigSerDes.convert2blob(self._config)


def deploy_config(config_yaml: str) -> bytes:
    config_parser = EIOConfigParser(config_yaml)
    config_parser.validate()
    config_bin = config_parser.transform()

    try:
        with open(EIO_FS_CONTROL, 'w', encoding='ascii') as f:
            f.write("config")

        with open(EIO_FS_CONFIG, "wb") as f:
            result = f.write(config_bin)

        if result != len(config_bin):
            raise ConfigError("Failed to write config to Extended IO controller!")

        with open(EIO_FS_CONTROL, 'w', encoding='ascii') as f:
            f.write("done")
    except OSError as e:
        print(e)
        raise ConfigError(f"OSError: {e}") from e


class EIOConfigDumper(object):
    def __init__(self, config_bin: bytearray) -> None:
        self._blob = config_bin

    def transform(self) -> str:
        config = EIOConfigSerDes.convert2config(self._blob)
        config_yaml = yaml.dump(config, Dumper=Dumper, indent=2, sort_keys=False)

        return config_yaml


def retrieve_config() -> str:
    try:
        with open(EIO_FS_CONFIG, "rb") as f:
            config_bin = f.read()
    except OSError as e:
        raise ConfigError(f"OSError: {e}") from e

    dumper = EIOConfigDumper(config_bin)
    return dumper.transform()
