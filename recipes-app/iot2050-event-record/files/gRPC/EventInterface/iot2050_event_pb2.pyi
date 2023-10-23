from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class WriteRequest(_message.Message):
    __slots__ = ["event_type", "event"]
    EVENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    EVENT_FIELD_NUMBER: _ClassVar[int]
    event_type: str
    event: str
    def __init__(self, event_type: _Optional[str] = ..., event: _Optional[str] = ...) -> None: ...

class WriteReply(_message.Message):
    __slots__ = ["status", "message"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    status: int
    message: str
    def __init__(self, status: _Optional[int] = ..., message: _Optional[str] = ...) -> None: ...

class ReadRequest(_message.Message):
    __slots__ = ["event_type"]
    EVENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    event_type: str
    def __init__(self, event_type: _Optional[str] = ...) -> None: ...

class ReadReply(_message.Message):
    __slots__ = ["status", "message", "event"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    EVENT_FIELD_NUMBER: _ClassVar[int]
    status: int
    message: str
    event: str
    def __init__(self, status: _Optional[int] = ..., message: _Optional[str] = ..., event: _Optional[str] = ...) -> None: ...
