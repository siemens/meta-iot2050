from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ChipUpdateStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CHIP_UPDATE_STATUS_UNSPECIFIED: _ClassVar[ChipUpdateStatus]
    CHIP_UPDATE_NOT_ATTEMPTED: _ClassVar[ChipUpdateStatus]
    CHIP_UPDATE_SUCCEEDED: _ClassVar[ChipUpdateStatus]
    CHIP_UPDATE_FAILED: _ClassVar[ChipUpdateStatus]

class OperationStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    OPERATION_STATUS_UNSPECIFIED: _ClassVar[OperationStatus]
    OPERATION_RUNNING: _ClassVar[OperationStatus]
    OPERATION_SUCCEEDED: _ClassVar[OperationStatus]
    OPERATION_FAILED: _ClassVar[OperationStatus]
    OPERATION_INTERRUPTED: _ClassVar[OperationStatus]
CHIP_UPDATE_STATUS_UNSPECIFIED: ChipUpdateStatus
CHIP_UPDATE_NOT_ATTEMPTED: ChipUpdateStatus
CHIP_UPDATE_SUCCEEDED: ChipUpdateStatus
CHIP_UPDATE_FAILED: ChipUpdateStatus
OPERATION_STATUS_UNSPECIFIED: OperationStatus
OPERATION_RUNNING: OperationStatus
OPERATION_SUCCEEDED: OperationStatus
OPERATION_FAILED: OperationStatus
OPERATION_INTERRUPTED: OperationStatus

class ModuleInspectionRequest(_message.Message):
    __slots__ = ("slot",)
    SLOT_FIELD_NUMBER: _ClassVar[int]
    slot: int
    def __init__(self, slot: _Optional[int] = ...) -> None: ...

class SlotInspection(_message.Message):
    __slots__ = ("slot", "chip_a_node", "chip_b_node")
    SLOT_FIELD_NUMBER: _ClassVar[int]
    CHIP_A_NODE_FIELD_NUMBER: _ClassVar[int]
    CHIP_B_NODE_FIELD_NUMBER: _ClassVar[int]
    slot: int
    chip_a_node: bool
    chip_b_node: bool
    def __init__(self, slot: _Optional[int] = ..., chip_a_node: bool = ..., chip_b_node: bool = ...) -> None: ...

class ModuleInspection(_message.Message):
    __slots__ = ("slots",)
    SLOTS_FIELD_NUMBER: _ClassVar[int]
    slots: _containers.RepeatedCompositeFieldContainer[SlotInspection]
    def __init__(self, slots: _Optional[_Iterable[_Union[SlotInspection, _Mapping]]] = ...) -> None: ...

class UpdateRequest(_message.Message):
    __slots__ = ("slot", "firmware_a", "firmware_b")
    SLOT_FIELD_NUMBER: _ClassVar[int]
    FIRMWARE_A_FIELD_NUMBER: _ClassVar[int]
    FIRMWARE_B_FIELD_NUMBER: _ClassVar[int]
    slot: int
    firmware_a: bytes
    firmware_b: bytes
    def __init__(self, slot: _Optional[int] = ..., firmware_a: _Optional[bytes] = ..., firmware_b: _Optional[bytes] = ...) -> None: ...

class UpdateReply(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetStatusReply(_message.Message):
    __slots__ = ("status", "code", "message", "outcome")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    OUTCOME_FIELD_NUMBER: _ClassVar[int]
    status: OperationStatus
    code: str
    message: str
    outcome: ModuleFirmwareOutcome
    def __init__(self, status: _Optional[_Union[OperationStatus, str]] = ..., code: _Optional[str] = ..., message: _Optional[str] = ..., outcome: _Optional[_Union[ModuleFirmwareOutcome, _Mapping]] = ...) -> None: ...

class WatchLogsReply(_message.Message):
    __slots__ = ("message",)
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: str
    def __init__(self, message: _Optional[str] = ...) -> None: ...

class ChipUpdateOutcome(_message.Message):
    __slots__ = ("status", "message")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    status: ChipUpdateStatus
    message: str
    def __init__(self, status: _Optional[_Union[ChipUpdateStatus, str]] = ..., message: _Optional[str] = ...) -> None: ...

class ModuleFirmwareOutcome(_message.Message):
    __slots__ = ("slot", "chip_a", "chip_b")
    SLOT_FIELD_NUMBER: _ClassVar[int]
    CHIP_A_FIELD_NUMBER: _ClassVar[int]
    CHIP_B_FIELD_NUMBER: _ClassVar[int]
    slot: int
    chip_a: ChipUpdateOutcome
    chip_b: ChipUpdateOutcome
    def __init__(self, slot: _Optional[int] = ..., chip_a: _Optional[_Union[ChipUpdateOutcome, _Mapping]] = ..., chip_b: _Optional[_Union[ChipUpdateOutcome, _Mapping]] = ...) -> None: ...
