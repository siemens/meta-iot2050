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
    __slots__ = ("supported", "details_json")
    SUPPORTED_FIELD_NUMBER: _ClassVar[int]
    DETAILS_JSON_FIELD_NUMBER: _ClassVar[int]
    supported: bool
    details_json: str
    def __init__(self, supported: bool = ..., details_json: _Optional[str] = ...) -> None: ...

class InspectRequest(_message.Message):
    __slots__ = ("firmware_path", "pg2_only")
    FIRMWARE_PATH_FIELD_NUMBER: _ClassVar[int]
    PG2_ONLY_FIELD_NUMBER: _ClassVar[int]
    firmware_path: str
    pg2_only: bool
    def __init__(self, firmware_path: _Optional[str] = ..., pg2_only: bool = ...) -> None: ...

class InspectionReply(_message.Message):
    __slots__ = ("ok", "code", "message", "details_json")
    OK_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    DETAILS_JSON_FIELD_NUMBER: _ClassVar[int]
    ok: bool
    code: str
    message: str
    details_json: str
    def __init__(self, ok: bool = ..., code: _Optional[str] = ..., message: _Optional[str] = ..., details_json: _Optional[str] = ...) -> None: ...

class UpdateRequest(_message.Message):
    __slots__ = ("firmware_path", "backup_dir", "preserve_list", "reset", "pg2_only", "no_backup", "force", "verify_signature", "legacy_cli")
    FIRMWARE_PATH_FIELD_NUMBER: _ClassVar[int]
    BACKUP_DIR_FIELD_NUMBER: _ClassVar[int]
    PRESERVE_LIST_FIELD_NUMBER: _ClassVar[int]
    RESET_FIELD_NUMBER: _ClassVar[int]
    PG2_ONLY_FIELD_NUMBER: _ClassVar[int]
    NO_BACKUP_FIELD_NUMBER: _ClassVar[int]
    FORCE_FIELD_NUMBER: _ClassVar[int]
    VERIFY_SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    LEGACY_CLI_FIELD_NUMBER: _ClassVar[int]
    firmware_path: str
    backup_dir: str
    preserve_list: _containers.RepeatedScalarFieldContainer[str]
    reset: bool
    pg2_only: bool
    no_backup: bool
    force: bool
    verify_signature: bool
    legacy_cli: bool
    def __init__(self, firmware_path: _Optional[str] = ..., backup_dir: _Optional[str] = ..., preserve_list: _Optional[_Iterable[str]] = ..., reset: bool = ..., pg2_only: bool = ..., no_backup: bool = ..., force: bool = ..., verify_signature: bool = ..., legacy_cli: bool = ...) -> None: ...

class RollbackRequest(_message.Message):
    __slots__ = ("backup_dir", "legacy_cli")
    BACKUP_DIR_FIELD_NUMBER: _ClassVar[int]
    LEGACY_CLI_FIELD_NUMBER: _ClassVar[int]
    backup_dir: str
    legacy_cli: bool
    def __init__(self, backup_dir: _Optional[str] = ..., legacy_cli: bool = ...) -> None: ...

class RollbackReply(_message.Message):
    __slots__ = ("ok", "code", "message", "details_json")
    OK_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    DETAILS_JSON_FIELD_NUMBER: _ClassVar[int]
    ok: bool
    code: str
    message: str
    details_json: str
    def __init__(self, ok: bool = ..., code: _Optional[str] = ..., message: _Optional[str] = ..., details_json: _Optional[str] = ...) -> None: ...

class OperationError(_message.Message):
    __slots__ = ("code", "message")
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    code: str
    message: str
    def __init__(self, code: _Optional[str] = ..., message: _Optional[str] = ...) -> None: ...

class UpdateResult(_message.Message):
    __slots__ = ("firmware_name", "target_version", "target_board", "firmware_sha256", "signature_verified", "backup_path", "mode", "reboot_required")
    FIRMWARE_NAME_FIELD_NUMBER: _ClassVar[int]
    TARGET_VERSION_FIELD_NUMBER: _ClassVar[int]
    TARGET_BOARD_FIELD_NUMBER: _ClassVar[int]
    FIRMWARE_SHA256_FIELD_NUMBER: _ClassVar[int]
    SIGNATURE_VERIFIED_FIELD_NUMBER: _ClassVar[int]
    BACKUP_PATH_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    REBOOT_REQUIRED_FIELD_NUMBER: _ClassVar[int]
    firmware_name: str
    target_version: str
    target_board: str
    firmware_sha256: str
    signature_verified: bool
    backup_path: str
    mode: str
    reboot_required: bool
    def __init__(self, firmware_name: _Optional[str] = ..., target_version: _Optional[str] = ..., target_board: _Optional[str] = ..., firmware_sha256: _Optional[str] = ..., signature_verified: bool = ..., backup_path: _Optional[str] = ..., mode: _Optional[str] = ..., reboot_required: bool = ...) -> None: ...

class RollbackResult(_message.Message):
    __slots__ = ("available", "size", "sha256", "created_at", "updater_version", "source", "mode", "reboot_required")
    AVAILABLE_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    SHA256_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATER_VERSION_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    REBOOT_REQUIRED_FIELD_NUMBER: _ClassVar[int]
    available: bool
    size: int
    sha256: str
    created_at: str
    updater_version: str
    source: str
    mode: str
    reboot_required: bool
    def __init__(self, available: bool = ..., size: _Optional[int] = ..., sha256: _Optional[str] = ..., created_at: _Optional[str] = ..., updater_version: _Optional[str] = ..., source: _Optional[str] = ..., mode: _Optional[str] = ..., reboot_required: bool = ...) -> None: ...

class OperationReply(_message.Message):
    __slots__ = ("operation_id", "operation", "status", "code", "message", "created_at", "updated_at", "finished_at", "last_message", "update_result", "rollback_result", "operation_error")
    OPERATION_ID_FIELD_NUMBER: _ClassVar[int]
    OPERATION_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    FINISHED_AT_FIELD_NUMBER: _ClassVar[int]
    LAST_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    UPDATE_RESULT_FIELD_NUMBER: _ClassVar[int]
    ROLLBACK_RESULT_FIELD_NUMBER: _ClassVar[int]
    OPERATION_ERROR_FIELD_NUMBER: _ClassVar[int]
    operation_id: str
    operation: str
    status: OperationStatus
    code: str
    message: str
    created_at: str
    updated_at: str
    finished_at: str
    last_message: str
    update_result: UpdateResult
    rollback_result: RollbackResult
    operation_error: OperationError
    def __init__(self, operation_id: _Optional[str] = ..., operation: _Optional[str] = ..., status: _Optional[_Union[OperationStatus, str]] = ..., code: _Optional[str] = ..., message: _Optional[str] = ..., created_at: _Optional[str] = ..., updated_at: _Optional[str] = ..., finished_at: _Optional[str] = ..., last_message: _Optional[str] = ..., update_result: _Optional[_Union[UpdateResult, _Mapping]] = ..., rollback_result: _Optional[_Union[RollbackResult, _Mapping]] = ..., operation_error: _Optional[_Union[OperationError, _Mapping]] = ...) -> None: ...

class OperationRequest(_message.Message):
    __slots__ = ("operation_id",)
    OPERATION_ID_FIELD_NUMBER: _ClassVar[int]
    operation_id: str
    def __init__(self, operation_id: _Optional[str] = ...) -> None: ...

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
