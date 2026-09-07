from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CapabilitiesReply(_message.Message):
    __slots__ = ["chip_a_supported", "chip_b_supported", "max_slots", "supported"]
    CHIP_A_SUPPORTED_FIELD_NUMBER: _ClassVar[int]
    CHIP_B_SUPPORTED_FIELD_NUMBER: _ClassVar[int]
    MAX_SLOTS_FIELD_NUMBER: _ClassVar[int]
    SUPPORTED_FIELD_NUMBER: _ClassVar[int]
    chip_a_supported: bool
    chip_b_supported: bool
    max_slots: int
    supported: bool
    def __init__(self, supported: bool = ..., max_slots: _Optional[int] = ..., chip_a_supported: bool = ..., chip_b_supported: bool = ...) -> None: ...

class ChipResult(_message.Message):
    __slots__ = ["attempted", "error", "success"]
    ATTEMPTED_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    attempted: bool
    error: str
    success: bool
    def __init__(self, attempted: bool = ..., success: bool = ..., error: _Optional[str] = ...) -> None: ...

class Empty(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class InspectRequest(_message.Message):
    __slots__ = ["scan", "slot"]
    SCAN_FIELD_NUMBER: _ClassVar[int]
    SLOT_FIELD_NUMBER: _ClassVar[int]
    scan: bool
    slot: int
    def __init__(self, slot: _Optional[int] = ..., scan: bool = ...) -> None: ...

class InspectionReply(_message.Message):
    __slots__ = ["code", "message", "ok", "slots"]
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    OK_FIELD_NUMBER: _ClassVar[int]
    SLOTS_FIELD_NUMBER: _ClassVar[int]
    code: str
    message: str
    ok: bool
    slots: _containers.RepeatedCompositeFieldContainer[SlotInspection]
    def __init__(self, ok: bool = ..., code: _Optional[str] = ..., message: _Optional[str] = ..., slots: _Optional[_Iterable[_Union[SlotInspection, _Mapping]]] = ...) -> None: ...

class OperationReply(_message.Message):
    __slots__ = ["code", "details_json", "message", "ok", "operation_id", "state"]
    CODE_FIELD_NUMBER: _ClassVar[int]
    DETAILS_JSON_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    OK_FIELD_NUMBER: _ClassVar[int]
    OPERATION_ID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    code: str
    details_json: str
    message: str
    ok: bool
    operation_id: str
    state: str
    def __init__(self, ok: bool = ..., code: _Optional[str] = ..., message: _Optional[str] = ..., details_json: _Optional[str] = ..., operation_id: _Optional[str] = ..., state: _Optional[str] = ...) -> None: ...

class OperationRequest(_message.Message):
    __slots__ = ["operation_id"]
    OPERATION_ID_FIELD_NUMBER: _ClassVar[int]
    operation_id: str
    def __init__(self, operation_id: _Optional[str] = ...) -> None: ...

class SlotInspection(_message.Message):
    __slots__ = ["available", "chip_a_node", "chip_b_node", "slot"]
    AVAILABLE_FIELD_NUMBER: _ClassVar[int]
    CHIP_A_NODE_FIELD_NUMBER: _ClassVar[int]
    CHIP_B_NODE_FIELD_NUMBER: _ClassVar[int]
    SLOT_FIELD_NUMBER: _ClassVar[int]
    available: bool
    chip_a_node: bool
    chip_b_node: bool
    slot: int
    def __init__(self, slot: _Optional[int] = ..., available: bool = ..., chip_a_node: bool = ..., chip_b_node: bool = ...) -> None: ...

class UpdateReply(_message.Message):
    __slots__ = ["chip_a", "chip_b", "code", "message", "ok", "partial_failure", "reboot_required", "slot"]
    CHIP_A_FIELD_NUMBER: _ClassVar[int]
    CHIP_B_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    OK_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_FAILURE_FIELD_NUMBER: _ClassVar[int]
    REBOOT_REQUIRED_FIELD_NUMBER: _ClassVar[int]
    SLOT_FIELD_NUMBER: _ClassVar[int]
    chip_a: ChipResult
    chip_b: ChipResult
    code: str
    message: str
    ok: bool
    partial_failure: bool
    reboot_required: bool
    slot: int
    def __init__(self, ok: bool = ..., code: _Optional[str] = ..., message: _Optional[str] = ..., slot: _Optional[int] = ..., chip_a: _Optional[_Union[ChipResult, _Mapping]] = ..., chip_b: _Optional[_Union[ChipResult, _Mapping]] = ..., partial_failure: bool = ..., reboot_required: bool = ...) -> None: ...

class UpdateRequest(_message.Message):
    __slots__ = ["firmware_a", "firmware_b", "slot"]
    FIRMWARE_A_FIELD_NUMBER: _ClassVar[int]
    FIRMWARE_B_FIELD_NUMBER: _ClassVar[int]
    SLOT_FIELD_NUMBER: _ClassVar[int]
    firmware_a: bytes
    firmware_b: bytes
    slot: int
    def __init__(self, slot: _Optional[int] = ..., firmware_a: _Optional[bytes] = ..., firmware_b: _Optional[bytes] = ...) -> None: ...
