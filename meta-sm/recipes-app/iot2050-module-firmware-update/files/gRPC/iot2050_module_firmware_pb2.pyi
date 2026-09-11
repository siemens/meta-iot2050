from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class OperationStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    OPERATION_STATUS_UNSPECIFIED: _ClassVar[OperationStatus]
    OPERATION_RUNNING: _ClassVar[OperationStatus]
    OPERATION_SUCCEEDED: _ClassVar[OperationStatus]
    OPERATION_FAILED: _ClassVar[OperationStatus]
    OPERATION_INTERRUPTED: _ClassVar[OperationStatus]
OPERATION_STATUS_UNSPECIFIED: OperationStatus
OPERATION_RUNNING: OperationStatus
OPERATION_SUCCEEDED: OperationStatus
OPERATION_FAILED: OperationStatus
OPERATION_INTERRUPTED: OperationStatus

class Empty(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CapabilitiesReply(_message.Message):
    __slots__ = ("supported", "max_slots", "chip_a_supported", "chip_b_supported")
    SUPPORTED_FIELD_NUMBER: _ClassVar[int]
    MAX_SLOTS_FIELD_NUMBER: _ClassVar[int]
    CHIP_A_SUPPORTED_FIELD_NUMBER: _ClassVar[int]
    CHIP_B_SUPPORTED_FIELD_NUMBER: _ClassVar[int]
    supported: bool
    max_slots: int
    chip_a_supported: bool
    chip_b_supported: bool
    def __init__(self, supported: bool = ..., max_slots: _Optional[int] = ..., chip_a_supported: bool = ..., chip_b_supported: bool = ...) -> None: ...

class InspectRequest(_message.Message):
    __slots__ = ("slot", "scan")
    SLOT_FIELD_NUMBER: _ClassVar[int]
    SCAN_FIELD_NUMBER: _ClassVar[int]
    slot: int
    scan: bool
    def __init__(self, slot: _Optional[int] = ..., scan: bool = ...) -> None: ...

class SlotInspection(_message.Message):
    __slots__ = ("slot", "available", "chip_a_node", "chip_b_node")
    SLOT_FIELD_NUMBER: _ClassVar[int]
    AVAILABLE_FIELD_NUMBER: _ClassVar[int]
    CHIP_A_NODE_FIELD_NUMBER: _ClassVar[int]
    CHIP_B_NODE_FIELD_NUMBER: _ClassVar[int]
    slot: int
    available: bool
    chip_a_node: bool
    chip_b_node: bool
    def __init__(self, slot: _Optional[int] = ..., available: bool = ..., chip_a_node: bool = ..., chip_b_node: bool = ...) -> None: ...

class InspectionReply(_message.Message):
    __slots__ = ("ok", "code", "message", "slots")
    OK_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    SLOTS_FIELD_NUMBER: _ClassVar[int]
    ok: bool
    code: str
    message: str
    slots: _containers.RepeatedCompositeFieldContainer[SlotInspection]
    def __init__(self, ok: bool = ..., code: _Optional[str] = ..., message: _Optional[str] = ..., slots: _Optional[_Iterable[_Union[SlotInspection, _Mapping]]] = ...) -> None: ...

class UpdateRequest(_message.Message):
    __slots__ = ("slot", "firmware_a", "firmware_b")
    SLOT_FIELD_NUMBER: _ClassVar[int]
    FIRMWARE_A_FIELD_NUMBER: _ClassVar[int]
    FIRMWARE_B_FIELD_NUMBER: _ClassVar[int]
    slot: int
    firmware_a: bytes
    firmware_b: bytes
    def __init__(self, slot: _Optional[int] = ..., firmware_a: _Optional[bytes] = ..., firmware_b: _Optional[bytes] = ...) -> None: ...

class ChipResult(_message.Message):
    __slots__ = ("attempted", "success", "error")
    ATTEMPTED_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    attempted: bool
    success: bool
    error: str
    def __init__(self, attempted: bool = ..., success: bool = ..., error: _Optional[str] = ...) -> None: ...

class UpdateReply(_message.Message):
    __slots__ = ("ok", "code", "message", "slot", "chip_a", "chip_b", "partial_failure", "reboot_required")
    OK_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    SLOT_FIELD_NUMBER: _ClassVar[int]
    CHIP_A_FIELD_NUMBER: _ClassVar[int]
    CHIP_B_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_FAILURE_FIELD_NUMBER: _ClassVar[int]
    REBOOT_REQUIRED_FIELD_NUMBER: _ClassVar[int]
    ok: bool
    code: str
    message: str
    slot: int
    chip_a: ChipResult
    chip_b: ChipResult
    partial_failure: bool
    reboot_required: bool
    def __init__(self, ok: bool = ..., code: _Optional[str] = ..., message: _Optional[str] = ..., slot: _Optional[int] = ..., chip_a: _Optional[_Union[ChipResult, _Mapping]] = ..., chip_b: _Optional[_Union[ChipResult, _Mapping]] = ..., partial_failure: bool = ..., reboot_required: bool = ...) -> None: ...

class OperationError(_message.Message):
    __slots__ = ("code", "message")
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    code: str
    message: str
    def __init__(self, code: _Optional[str] = ..., message: _Optional[str] = ...) -> None: ...

class ModuleUpdateResult(_message.Message):
    __slots__ = ("slot", "chip_a", "chip_b", "partial_failure", "reboot_required")
    SLOT_FIELD_NUMBER: _ClassVar[int]
    CHIP_A_FIELD_NUMBER: _ClassVar[int]
    CHIP_B_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_FAILURE_FIELD_NUMBER: _ClassVar[int]
    REBOOT_REQUIRED_FIELD_NUMBER: _ClassVar[int]
    slot: int
    chip_a: ChipResult
    chip_b: ChipResult
    partial_failure: bool
    reboot_required: bool
    def __init__(self, slot: _Optional[int] = ..., chip_a: _Optional[_Union[ChipResult, _Mapping]] = ..., chip_b: _Optional[_Union[ChipResult, _Mapping]] = ..., partial_failure: bool = ..., reboot_required: bool = ...) -> None: ...

class OperationRequest(_message.Message):
    __slots__ = ("operation_id",)
    OPERATION_ID_FIELD_NUMBER: _ClassVar[int]
    operation_id: str
    def __init__(self, operation_id: _Optional[str] = ...) -> None: ...

class OperationReply(_message.Message):
    __slots__ = ("operation_id", "status", "code", "message", "created_at", "updated_at", "finished_at", "last_message", "update_result", "operation_error")
    OPERATION_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    FINISHED_AT_FIELD_NUMBER: _ClassVar[int]
    LAST_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    UPDATE_RESULT_FIELD_NUMBER: _ClassVar[int]
    OPERATION_ERROR_FIELD_NUMBER: _ClassVar[int]
    operation_id: str
    status: OperationStatus
    code: str
    message: str
    created_at: str
    updated_at: str
    finished_at: str
    last_message: str
    update_result: ModuleUpdateResult
    operation_error: OperationError
    def __init__(self, operation_id: _Optional[str] = ..., status: _Optional[_Union[OperationStatus, str]] = ..., code: _Optional[str] = ..., message: _Optional[str] = ..., created_at: _Optional[str] = ..., updated_at: _Optional[str] = ..., finished_at: _Optional[str] = ..., last_message: _Optional[str] = ..., update_result: _Optional[_Union[ModuleUpdateResult, _Mapping]] = ..., operation_error: _Optional[_Union[OperationError, _Mapping]] = ...) -> None: ...

class StreamOperationLogsRequest(_message.Message):
    __slots__ = ("operation_id", "after_sequence")
    OPERATION_ID_FIELD_NUMBER: _ClassVar[int]
    AFTER_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    operation_id: str
    after_sequence: int
    def __init__(self, operation_id: _Optional[str] = ..., after_sequence: _Optional[int] = ...) -> None: ...

class OperationLog(_message.Message):
    __slots__ = ("sequence", "timestamp", "message")
    SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    sequence: int
    timestamp: str
    message: str
    def __init__(self, sequence: _Optional[int] = ..., timestamp: _Optional[str] = ..., message: _Optional[str] = ...) -> None: ...
