from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AQVI_STATUS(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    AQVI_NO_ERROR: _ClassVar[AQVI_STATUS]
    AQVI_APPLICATION_NOT_STARTED: _ClassVar[AQVI_STATUS]
    AQVI_NO_RETURN_DATA: _ClassVar[AQVI_STATUS]
    AQVI_DATA_BUFFER_TOO_SMALL: _ClassVar[AQVI_STATUS]
    AQVI_PREVIOUS_CMD_PROCESSING: _ClassVar[AQVI_STATUS]
    AQVI_INPUT_PARAMETER_UNKNOWN: _ClassVar[AQVI_STATUS]
    AQVI_INPUT_PARAMETER_INCOMPLETED: _ClassVar[AQVI_STATUS]
    AQVI_NOT_SUPPORTED: _ClassVar[AQVI_STATUS]
    AQVI_INCOMPLETE_COMMAND: _ClassVar[AQVI_STATUS]
    AQVI_SUBWND_INVALID: _ClassVar[AQVI_STATUS]
    AQVI_SUBWND_CNT_EXCEED: _ClassVar[AQVI_STATUS]
    AQVI_SW_BUSY: _ClassVar[AQVI_STATUS]
    AQVI_LASUBWND_INVALID: _ClassVar[AQVI_STATUS]
    AQVI_PASUBWND_INVALID: _ClassVar[AQVI_STATUS]
    AQVI_DECODE_REPORT_INVALID: _ClassVar[AQVI_STATUS]
    AQVI_TIMING_REPORT_INVALID: _ClassVar[AQVI_STATUS]
    AQVI_COMMAND_FORMAT_ERROR: _ClassVar[AQVI_STATUS]
    AQVI_INPUT_FILE_DIR_INVALID: _ClassVar[AQVI_STATUS]
    AQVI_CAPTURE_ALREADY_RUNNING: _ClassVar[AQVI_STATUS]
    AQVI_CAPTURE_NOT_RUNNING: _ClassVar[AQVI_STATUS]
    AQVI_ROW_COL_INDEX_INVALID: _ClassVar[AQVI_STATUS]
    AQVI_SELECT_INDEX_INVALID: _ClassVar[AQVI_STATUS]
    AQVI_INPUT_PARAMETER_INVALID: _ClassVar[AQVI_STATUS]
    AQVI_INPUT_SETTING_FILE_FORMAT_ERROR: _ClassVar[AQVI_STATUS]
    AQVI_FILE_ACCESS_ERROR: _ClassVar[AQVI_STATUS]
    AQVI_TRANSITION_REPORT_INVALID: _ClassVar[AQVI_STATUS]
    AQVI_MEASUREMENT_REPORT_INVALID: _ClassVar[AQVI_STATUS]
    AQVI_SELECT_LABEL_INVALID: _ClassVar[AQVI_STATUS]
    AQVI_SELECT_RANGE_ERROR: _ClassVar[AQVI_STATUS]
    AQVI_SELECT_CHANNEL_NAME_INVALID: _ClassVar[AQVI_STATUS]
    AQVI_CURSOR_SEARCH_FAILED: _ClassVar[AQVI_STATUS]
    AQVI_WAVEFORM_NOT_READY: _ClassVar[AQVI_STATUS]
    AQVI_NOT_IN_EV_MODE: _ClassVar[AQVI_STATUS]
    AQVI_NO_EV_ANALYSIS_RESULT: _ClassVar[AQVI_STATUS]
    AQVI_UNSUPPORT_FEATURE: _ClassVar[AQVI_STATUS]
    AQVI_UNFINISHED_FEATURE: _ClassVar[AQVI_STATUS]
    AQVI_UNKNOWN_COMMAND_ERROR: _ClassVar[AQVI_STATUS]
    AQVI_UNKNOWN_ERROR: _ClassVar[AQVI_STATUS]
AQVI_NO_ERROR: AQVI_STATUS
AQVI_APPLICATION_NOT_STARTED: AQVI_STATUS
AQVI_NO_RETURN_DATA: AQVI_STATUS
AQVI_DATA_BUFFER_TOO_SMALL: AQVI_STATUS
AQVI_PREVIOUS_CMD_PROCESSING: AQVI_STATUS
AQVI_INPUT_PARAMETER_UNKNOWN: AQVI_STATUS
AQVI_INPUT_PARAMETER_INCOMPLETED: AQVI_STATUS
AQVI_NOT_SUPPORTED: AQVI_STATUS
AQVI_INCOMPLETE_COMMAND: AQVI_STATUS
AQVI_SUBWND_INVALID: AQVI_STATUS
AQVI_SUBWND_CNT_EXCEED: AQVI_STATUS
AQVI_SW_BUSY: AQVI_STATUS
AQVI_LASUBWND_INVALID: AQVI_STATUS
AQVI_PASUBWND_INVALID: AQVI_STATUS
AQVI_DECODE_REPORT_INVALID: AQVI_STATUS
AQVI_TIMING_REPORT_INVALID: AQVI_STATUS
AQVI_COMMAND_FORMAT_ERROR: AQVI_STATUS
AQVI_INPUT_FILE_DIR_INVALID: AQVI_STATUS
AQVI_CAPTURE_ALREADY_RUNNING: AQVI_STATUS
AQVI_CAPTURE_NOT_RUNNING: AQVI_STATUS
AQVI_ROW_COL_INDEX_INVALID: AQVI_STATUS
AQVI_SELECT_INDEX_INVALID: AQVI_STATUS
AQVI_INPUT_PARAMETER_INVALID: AQVI_STATUS
AQVI_INPUT_SETTING_FILE_FORMAT_ERROR: AQVI_STATUS
AQVI_FILE_ACCESS_ERROR: AQVI_STATUS
AQVI_TRANSITION_REPORT_INVALID: AQVI_STATUS
AQVI_MEASUREMENT_REPORT_INVALID: AQVI_STATUS
AQVI_SELECT_LABEL_INVALID: AQVI_STATUS
AQVI_SELECT_RANGE_ERROR: AQVI_STATUS
AQVI_SELECT_CHANNEL_NAME_INVALID: AQVI_STATUS
AQVI_CURSOR_SEARCH_FAILED: AQVI_STATUS
AQVI_WAVEFORM_NOT_READY: AQVI_STATUS
AQVI_NOT_IN_EV_MODE: AQVI_STATUS
AQVI_NO_EV_ANALYSIS_RESULT: AQVI_STATUS
AQVI_UNSUPPORT_FEATURE: AQVI_STATUS
AQVI_UNFINISHED_FEATURE: AQVI_STATUS
AQVI_UNKNOWN_COMMAND_ERROR: AQVI_STATUS
AQVI_UNKNOWN_ERROR: AQVI_STATUS

class ViWriteRequest(_message.Message):
    __slots__ = ("command",)
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    command: bytes
    def __init__(self, command: _Optional[bytes] = ...) -> None: ...

class ViWriteResponse(_message.Message):
    __slots__ = ("job_id", "status_code")
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_CODE_FIELD_NUMBER: _ClassVar[int]
    job_id: bytes
    status_code: AQVI_STATUS
    def __init__(self, job_id: _Optional[bytes] = ..., status_code: _Optional[_Union[AQVI_STATUS, str]] = ...) -> None: ...

class ViGetCommandResultRequest(_message.Message):
    __slots__ = ("job_id",)
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    job_id: bytes
    def __init__(self, job_id: _Optional[bytes] = ...) -> None: ...

class ViGetCommandResultResponse(_message.Message):
    __slots__ = ("status_code",)
    STATUS_CODE_FIELD_NUMBER: _ClassVar[int]
    status_code: AQVI_STATUS
    def __init__(self, status_code: _Optional[_Union[AQVI_STATUS, str]] = ...) -> None: ...

class ViReadRequest(_message.Message):
    __slots__ = ("job_id", "count")
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    job_id: bytes
    count: int
    def __init__(self, job_id: _Optional[bytes] = ..., count: _Optional[int] = ...) -> None: ...

class ViReadResponse(_message.Message):
    __slots__ = ("status_code", "command_response", "ret_count")
    STATUS_CODE_FIELD_NUMBER: _ClassVar[int]
    COMMAND_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    RET_COUNT_FIELD_NUMBER: _ClassVar[int]
    status_code: AQVI_STATUS
    command_response: bytes
    ret_count: int
    def __init__(self, status_code: _Optional[_Union[AQVI_STATUS, str]] = ..., command_response: _Optional[bytes] = ..., ret_count: _Optional[int] = ...) -> None: ...
