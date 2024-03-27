from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class DeployRequest(_message.Message):
    __slots__ = ["yaml_data"]
    YAML_DATA_FIELD_NUMBER: _ClassVar[int]
    yaml_data: str
    def __init__(self, yaml_data: _Optional[str] = ...) -> None: ...

class DeployReply(_message.Message):
    __slots__ = ["status", "message"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    status: int
    message: str
    def __init__(self, status: _Optional[int] = ..., message: _Optional[str] = ...) -> None: ...

class RetrieveRequest(_message.Message):
    __slots__ = ["name"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class RetrieveReply(_message.Message):
    __slots__ = ["status", "message", "yaml_data"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    YAML_DATA_FIELD_NUMBER: _ClassVar[int]
    status: int
    message: str
    yaml_data: str
    def __init__(self, status: _Optional[int] = ..., message: _Optional[str] = ..., yaml_data: _Optional[str] = ...) -> None: ...

class SyncTimeRequest(_message.Message):
    __slots__ = ["time"]
    TIME_FIELD_NUMBER: _ClassVar[int]
    time: str
    def __init__(self, time: _Optional[str] = ...) -> None: ...

class SyncTimeReply(_message.Message):
    __slots__ = ["status", "message"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    status: int
    message: str
    def __init__(self, status: _Optional[int] = ..., message: _Optional[str] = ...) -> None: ...

class UpdateFirmwareRequest(_message.Message):
    __slots__ = ["entity", "firmware"]
    ENTITY_FIELD_NUMBER: _ClassVar[int]
    FIRMWARE_FIELD_NUMBER: _ClassVar[int]
    entity: int
    firmware: bytes
    def __init__(self, entity: _Optional[int] = ..., firmware: _Optional[bytes] = ...) -> None: ...

class UpdateFirmwareReply(_message.Message):
    __slots__ = ["status", "message"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    status: int
    message: str
    def __init__(self, status: _Optional[int] = ..., message: _Optional[str] = ...) -> None: ...

class CheckFWURequest(_message.Message):
    __slots__ = ["entity"]
    ENTITY_FIELD_NUMBER: _ClassVar[int]
    entity: int
    def __init__(self, entity: _Optional[int] = ...) -> None: ...

class CheckFWUReply(_message.Message):
    __slots__ = ["status", "message"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    status: int
    message: str
    def __init__(self, status: _Optional[int] = ..., message: _Optional[str] = ...) -> None: ...

class ReadEIOEventRequest(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class ReadEIOEventReply(_message.Message):
    __slots__ = ["status", "message", "event"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    EVENT_FIELD_NUMBER: _ClassVar[int]
    status: int
    message: str
    event: str
    def __init__(self, status: _Optional[int] = ..., message: _Optional[str] = ..., event: _Optional[str] = ...) -> None: ...
