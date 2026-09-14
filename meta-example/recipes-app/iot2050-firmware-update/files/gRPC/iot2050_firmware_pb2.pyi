from google.protobuf import empty_pb2 as _empty_pb2
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

class InspectRequest(_message.Message):
    __slots__ = ("package", "rollback")
    PACKAGE_FIELD_NUMBER: _ClassVar[int]
    ROLLBACK_FIELD_NUMBER: _ClassVar[int]
    package: PackageInspection
    rollback: RollbackInspection
    def __init__(self, package: _Optional[_Union[PackageInspection, _Mapping]] = ..., rollback: _Optional[_Union[RollbackInspection, _Mapping]] = ...) -> None: ...

class PackageInspection(_message.Message):
    __slots__ = ("firmware_path",)
    FIRMWARE_PATH_FIELD_NUMBER: _ClassVar[int]
    firmware_path: str
    def __init__(self, firmware_path: _Optional[str] = ...) -> None: ...

class RollbackInspection(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class InspectReply(_message.Message):
    __slots__ = ("package", "rollback")
    PACKAGE_FIELD_NUMBER: _ClassVar[int]
    ROLLBACK_FIELD_NUMBER: _ClassVar[int]
    package: FirmwareInspection
    rollback: RollbackInspectionResult
    def __init__(self, package: _Optional[_Union[FirmwareInspection, _Mapping]] = ..., rollback: _Optional[_Union[RollbackInspectionResult, _Mapping]] = ...) -> None: ...

class RollbackInspectionResult(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class FirmwareInspection(_message.Message):
    __slots__ = ("firmware_name", "target_version", "target_board")
    FIRMWARE_NAME_FIELD_NUMBER: _ClassVar[int]
    TARGET_VERSION_FIELD_NUMBER: _ClassVar[int]
    TARGET_BOARD_FIELD_NUMBER: _ClassVar[int]
    firmware_name: str
    target_version: str
    target_board: str
    def __init__(self, firmware_name: _Optional[str] = ..., target_version: _Optional[str] = ..., target_board: _Optional[str] = ...) -> None: ...

class UpdateRequest(_message.Message):
    __slots__ = ("package", "raw")
    PACKAGE_FIELD_NUMBER: _ClassVar[int]
    RAW_FIELD_NUMBER: _ClassVar[int]
    package: PackageUpdate
    raw: RawUpdate
    def __init__(self, package: _Optional[_Union[PackageUpdate, _Mapping]] = ..., raw: _Optional[_Union[RawUpdate, _Mapping]] = ...) -> None: ...

class PackageUpdate(_message.Message):
    __slots__ = ("firmware_path", "backup_dir", "preserve_list", "reset", "no_backup", "no_verify")
    FIRMWARE_PATH_FIELD_NUMBER: _ClassVar[int]
    BACKUP_DIR_FIELD_NUMBER: _ClassVar[int]
    PRESERVE_LIST_FIELD_NUMBER: _ClassVar[int]
    RESET_FIELD_NUMBER: _ClassVar[int]
    NO_BACKUP_FIELD_NUMBER: _ClassVar[int]
    NO_VERIFY_FIELD_NUMBER: _ClassVar[int]
    firmware_path: str
    backup_dir: str
    preserve_list: _containers.RepeatedScalarFieldContainer[str]
    reset: bool
    no_backup: bool
    no_verify: bool
    def __init__(self, firmware_path: _Optional[str] = ..., backup_dir: _Optional[str] = ..., preserve_list: _Optional[_Iterable[str]] = ..., reset: bool = ..., no_backup: bool = ..., no_verify: bool = ...) -> None: ...

class RawUpdate(_message.Message):
    __slots__ = ("firmware_path",)
    FIRMWARE_PATH_FIELD_NUMBER: _ClassVar[int]
    firmware_path: str
    def __init__(self, firmware_path: _Optional[str] = ...) -> None: ...

class UpdateReply(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetStatusReply(_message.Message):
    __slots__ = ("status", "code", "message")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    status: OperationStatus
    code: str
    message: str
    def __init__(self, status: _Optional[_Union[OperationStatus, str]] = ..., code: _Optional[str] = ..., message: _Optional[str] = ...) -> None: ...

class WatchLogsReply(_message.Message):
    __slots__ = ("message",)
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: str
    def __init__(self, message: _Optional[str] = ...) -> None: ...

class RollbackRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class RollbackReply(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
