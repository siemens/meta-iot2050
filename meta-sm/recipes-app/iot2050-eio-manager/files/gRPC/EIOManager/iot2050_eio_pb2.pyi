from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CheckFWUReply(_message.Message):
    __slots__ = ["inspection", "message", "status"]
    INSPECTION_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    inspection: FirmwareInspection
    message: str
    status: int
    def __init__(self, status: _Optional[int] = ..., message: _Optional[str] = ..., inspection: _Optional[_Union[FirmwareInspection, _Mapping]] = ...) -> None: ...

class CheckFWURequest(_message.Message):
    __slots__ = ["entity"]
    ENTITY_FIELD_NUMBER: _ClassVar[int]
    entity: int
    def __init__(self, entity: _Optional[int] = ...) -> None: ...

class DeployReply(_message.Message):
    __slots__ = ["message", "status"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    message: str
    status: int
    def __init__(self, status: _Optional[int] = ..., message: _Optional[str] = ...) -> None: ...

class DeployRequest(_message.Message):
    __slots__ = ["yaml_data"]
    YAML_DATA_FIELD_NUMBER: _ClassVar[int]
    yaml_data: str
    def __init__(self, yaml_data: _Optional[str] = ...) -> None: ...

class FirmwareInspection(_message.Message):
    __slots__ = ["actual_sha256", "bundled_version", "current_version", "detail_message", "integrity", "metadata_sha1", "status", "status_code", "supported", "update_needed"]
    ACTUAL_SHA256_FIELD_NUMBER: _ClassVar[int]
    BUNDLED_VERSION_FIELD_NUMBER: _ClassVar[int]
    CURRENT_VERSION_FIELD_NUMBER: _ClassVar[int]
    DETAIL_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    INTEGRITY_FIELD_NUMBER: _ClassVar[int]
    METADATA_SHA1_FIELD_NUMBER: _ClassVar[int]
    STATUS_CODE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SUPPORTED_FIELD_NUMBER: _ClassVar[int]
    UPDATE_NEEDED_FIELD_NUMBER: _ClassVar[int]
    actual_sha256: str
    bundled_version: str
    current_version: str
    detail_message: str
    integrity: bool
    metadata_sha1: str
    status: str
    status_code: int
    supported: bool
    update_needed: bool
    def __init__(self, supported: bool = ..., current_version: _Optional[str] = ..., bundled_version: _Optional[str] = ..., metadata_sha1: _Optional[str] = ..., actual_sha256: _Optional[str] = ..., integrity: bool = ..., update_needed: bool = ..., status: _Optional[str] = ..., status_code: _Optional[int] = ..., detail_message: _Optional[str] = ...) -> None: ...

class ReadEIOEventReply(_message.Message):
    __slots__ = ["event", "message", "status"]
    EVENT_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    event: str
    message: str
    status: int
    def __init__(self, status: _Optional[int] = ..., message: _Optional[str] = ..., event: _Optional[str] = ...) -> None: ...

class ReadEIOEventRequest(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class RetrieveReply(_message.Message):
    __slots__ = ["message", "status", "yaml_data"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    YAML_DATA_FIELD_NUMBER: _ClassVar[int]
    message: str
    status: int
    yaml_data: str
    def __init__(self, status: _Optional[int] = ..., message: _Optional[str] = ..., yaml_data: _Optional[str] = ...) -> None: ...

class RetrieveRequest(_message.Message):
    __slots__ = ["name"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class SyncTimeReply(_message.Message):
    __slots__ = ["message", "status"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    message: str
    status: int
    def __init__(self, status: _Optional[int] = ..., message: _Optional[str] = ...) -> None: ...

class SyncTimeRequest(_message.Message):
    __slots__ = ["time"]
    TIME_FIELD_NUMBER: _ClassVar[int]
    time: str
    def __init__(self, time: _Optional[str] = ...) -> None: ...

class UpdateFirmwareReply(_message.Message):
    __slots__ = ["message", "status"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    message: str
    status: int
    def __init__(self, status: _Optional[int] = ..., message: _Optional[str] = ...) -> None: ...

class UpdateFirmwareRequest(_message.Message):
    __slots__ = ["entity", "firmware"]
    ENTITY_FIELD_NUMBER: _ClassVar[int]
    FIRMWARE_FIELD_NUMBER: _ClassVar[int]
    entity: int
    firmware: bytes
    def __init__(self, entity: _Optional[int] = ..., firmware: _Optional[bytes] = ...) -> None: ...
