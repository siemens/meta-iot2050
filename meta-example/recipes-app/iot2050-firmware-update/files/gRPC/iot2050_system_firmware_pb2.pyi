from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class OperationState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    OPERATION_STATE_UNSPECIFIED: _ClassVar[OperationState]
    OPERATION_RUNNING: _ClassVar[OperationState]
    OPERATION_SUCCEEDED: _ClassVar[OperationState]
    OPERATION_FAILED: _ClassVar[OperationState]
    OPERATION_INTERRUPTED: _ClassVar[OperationState]

class OperationStage(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    OPERATION_STAGE_UNSPECIFIED: _ClassVar[OperationStage]
    OPERATION_STAGE_STARTING: _ClassVar[OperationStage]
    OPERATION_STAGE_CHECKING_COMPATIBILITY: _ClassVar[OperationStage]
    OPERATION_STAGE_PREPARING_BACKUP: _ClassVar[OperationStage]
    OPERATION_STAGE_BACKING_UP: _ClassVar[OperationStage]
    OPERATION_STAGE_FLASHING_SYSTEM: _ClassVar[OperationStage]
    OPERATION_STAGE_VERIFYING_SIGNATURE: _ClassVar[OperationStage]
    OPERATION_STAGE_SIGNATURE_VERIFIED: _ClassVar[OperationStage]
    OPERATION_STAGE_UPDATING_UBOOT: _ClassVar[OperationStage]
    OPERATION_STAGE_UPDATING_ENV: _ClassVar[OperationStage]
    OPERATION_STAGE_RETRYING_FLASH: _ClassVar[OperationStage]
    OPERATION_STAGE_PREPARING_ROLLBACK: _ClassVar[OperationStage]
    OPERATION_STAGE_COMPLETED: _ClassVar[OperationStage]
    OPERATION_STAGE_FAILED: _ClassVar[OperationStage]
    OPERATION_STAGE_INTERRUPTED: _ClassVar[OperationStage]
OPERATION_STATE_UNSPECIFIED: OperationState
OPERATION_RUNNING: OperationState
OPERATION_SUCCEEDED: OperationState
OPERATION_FAILED: OperationState
OPERATION_INTERRUPTED: OperationState
OPERATION_STAGE_UNSPECIFIED: OperationStage
OPERATION_STAGE_STARTING: OperationStage
OPERATION_STAGE_CHECKING_COMPATIBILITY: OperationStage
OPERATION_STAGE_PREPARING_BACKUP: OperationStage
OPERATION_STAGE_BACKING_UP: OperationStage
OPERATION_STAGE_FLASHING_SYSTEM: OperationStage
OPERATION_STAGE_VERIFYING_SIGNATURE: OperationStage
OPERATION_STAGE_SIGNATURE_VERIFIED: OperationStage
OPERATION_STAGE_UPDATING_UBOOT: OperationStage
OPERATION_STAGE_UPDATING_ENV: OperationStage
OPERATION_STAGE_RETRYING_FLASH: OperationStage
OPERATION_STAGE_PREPARING_ROLLBACK: OperationStage
OPERATION_STAGE_COMPLETED: OperationStage
OPERATION_STAGE_FAILED: OperationStage
OPERATION_STAGE_INTERRUPTED: OperationStage

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

class ProgressEvent(_message.Message):
    __slots__ = ("sequence", "stage", "message")
    SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    STAGE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    sequence: int
    stage: OperationStage
    message: str
    def __init__(self, sequence: _Optional[int] = ..., stage: _Optional[_Union[OperationStage, str]] = ..., message: _Optional[str] = ...) -> None: ...

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
    __slots__ = ("ok", "code", "message", "details_json", "operation_id", "state", "stage", "operation_state", "operation_stage", "recent_events", "update_result", "rollback_result", "operation_error")
    OK_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    DETAILS_JSON_FIELD_NUMBER: _ClassVar[int]
    OPERATION_ID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    STAGE_FIELD_NUMBER: _ClassVar[int]
    OPERATION_STATE_FIELD_NUMBER: _ClassVar[int]
    OPERATION_STAGE_FIELD_NUMBER: _ClassVar[int]
    RECENT_EVENTS_FIELD_NUMBER: _ClassVar[int]
    UPDATE_RESULT_FIELD_NUMBER: _ClassVar[int]
    ROLLBACK_RESULT_FIELD_NUMBER: _ClassVar[int]
    OPERATION_ERROR_FIELD_NUMBER: _ClassVar[int]
    ok: bool
    code: str
    message: str
    details_json: str
    operation_id: str
    state: str
    stage: str
    operation_state: OperationState
    operation_stage: OperationStage
    recent_events: _containers.RepeatedCompositeFieldContainer[ProgressEvent]
    update_result: UpdateResult
    rollback_result: RollbackResult
    operation_error: OperationError
    def __init__(self, ok: bool = ..., code: _Optional[str] = ..., message: _Optional[str] = ..., details_json: _Optional[str] = ..., operation_id: _Optional[str] = ..., state: _Optional[str] = ..., stage: _Optional[str] = ..., operation_state: _Optional[_Union[OperationState, str]] = ..., operation_stage: _Optional[_Union[OperationStage, str]] = ..., recent_events: _Optional[_Iterable[_Union[ProgressEvent, _Mapping]]] = ..., update_result: _Optional[_Union[UpdateResult, _Mapping]] = ..., rollback_result: _Optional[_Union[RollbackResult, _Mapping]] = ..., operation_error: _Optional[_Union[OperationError, _Mapping]] = ...) -> None: ...

class OperationRequest(_message.Message):
    __slots__ = ("operation_id",)
    OPERATION_ID_FIELD_NUMBER: _ClassVar[int]
    operation_id: str
    def __init__(self, operation_id: _Optional[str] = ...) -> None: ...
