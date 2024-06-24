from google.protobuf import empty_pb2 as _empty_pb2
from py_lab_hal.proto import datagrame_pb2 as _datagrame_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SystemCommand(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SYSTEM_QUER: _ClassVar[SystemCommand]
    SYSTEM_CONN: _ClassVar[SystemCommand]
    SYSTEM_FCON: _ClassVar[SystemCommand]
    SYSTEM_DISC: _ClassVar[SystemCommand]
    SYSTEM_SUCC: _ClassVar[SystemCommand]
    SYSTEM_FAIL: _ClassVar[SystemCommand]
    SYSTEM_IDLE: _ClassVar[SystemCommand]
    SYSTEM_BUSY: _ClassVar[SystemCommand]
    SYSTEM_SCAN: _ClassVar[SystemCommand]
SYSTEM_QUER: SystemCommand
SYSTEM_CONN: SystemCommand
SYSTEM_FCON: SystemCommand
SYSTEM_DISC: SystemCommand
SYSTEM_SUCC: SystemCommand
SYSTEM_FAIL: SystemCommand
SYSTEM_IDLE: SystemCommand
SYSTEM_BUSY: SystemCommand
SYSTEM_SCAN: SystemCommand

class SystemRequest(_message.Message):
    __slots__ = ("action",)
    ACTION_FIELD_NUMBER: _ClassVar[int]
    action: SystemCommand
    def __init__(self, action: _Optional[_Union[SystemCommand, str]] = ...) -> None: ...

class SystemResponse(_message.Message):
    __slots__ = ("response_status", "response_command", "scan_info")
    RESPONSE_STATUS_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_COMMAND_FIELD_NUMBER: _ClassVar[int]
    SCAN_INFO_FIELD_NUMBER: _ClassVar[int]
    response_status: SystemCommand
    response_command: SystemCommand
    scan_info: str
    def __init__(self, response_status: _Optional[_Union[SystemCommand, str]] = ..., response_command: _Optional[_Union[SystemCommand, str]] = ..., scan_info: _Optional[str] = ...) -> None: ...

class SerialConfig(_message.Message):
    __slots__ = ("baud_rate", "data_bits", "stop_bits", "parity", "flow_control")
    BAUD_RATE_FIELD_NUMBER: _ClassVar[int]
    DATA_BITS_FIELD_NUMBER: _ClassVar[int]
    STOP_BITS_FIELD_NUMBER: _ClassVar[int]
    PARITY_FIELD_NUMBER: _ClassVar[int]
    FLOW_CONTROL_FIELD_NUMBER: _ClassVar[int]
    baud_rate: int
    data_bits: int
    stop_bits: float
    parity: str
    flow_control: int
    def __init__(self, baud_rate: _Optional[int] = ..., data_bits: _Optional[int] = ..., stop_bits: _Optional[float] = ..., parity: _Optional[str] = ..., flow_control: _Optional[int] = ...) -> None: ...

class InstRequest(_message.Message):
    __slots__ = ("socket_host", "socket_port", "visa_resource", "serial_config", "interface_type", "read_terminator", "write_terminator", "connect_timeout", "recv_timeout", "send_timeout", "name", "py_lab_hal_board_interface_type")
    SOCKET_HOST_FIELD_NUMBER: _ClassVar[int]
    SOCKET_PORT_FIELD_NUMBER: _ClassVar[int]
    VISA_RESOURCE_FIELD_NUMBER: _ClassVar[int]
    SERIAL_CONFIG_FIELD_NUMBER: _ClassVar[int]
    INTERFACE_TYPE_FIELD_NUMBER: _ClassVar[int]
    READ_TERMINATOR_FIELD_NUMBER: _ClassVar[int]
    WRITE_TERMINATOR_FIELD_NUMBER: _ClassVar[int]
    CONNECT_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    RECV_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    SEND_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PY_LAB_HAL_BOARD_INTERFACE_TYPE_FIELD_NUMBER: _ClassVar[int]
    socket_host: str
    socket_port: int
    visa_resource: str
    serial_config: SerialConfig
    interface_type: str
    read_terminator: str
    write_terminator: str
    connect_timeout: int
    recv_timeout: int
    send_timeout: int
    name: str
    py_lab_hal_board_interface_type: str
    def __init__(self, socket_host: _Optional[str] = ..., socket_port: _Optional[int] = ..., visa_resource: _Optional[str] = ..., serial_config: _Optional[_Union[SerialConfig, _Mapping]] = ..., interface_type: _Optional[str] = ..., read_terminator: _Optional[str] = ..., write_terminator: _Optional[str] = ..., connect_timeout: _Optional[int] = ..., recv_timeout: _Optional[int] = ..., send_timeout: _Optional[int] = ..., name: _Optional[str] = ..., py_lab_hal_board_interface_type: _Optional[str] = ...) -> None: ...

class InstResponse(_message.Message):
    __slots__ = ("result", "name")
    RESULT_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    result: bool
    name: str
    def __init__(self, result: bool = ..., name: _Optional[str] = ...) -> None: ...

class RecvRequest(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class SendRequest(_message.Message):
    __slots__ = ("name", "send")
    NAME_FIELD_NUMBER: _ClassVar[int]
    SEND_FIELD_NUMBER: _ClassVar[int]
    name: str
    send: bytes
    def __init__(self, name: _Optional[str] = ..., send: _Optional[bytes] = ...) -> None: ...

class RecvResponse(_message.Message):
    __slots__ = ("read",)
    READ_FIELD_NUMBER: _ClassVar[int]
    read: bytes
    def __init__(self, read: _Optional[bytes] = ...) -> None: ...

class CloseRequest(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class CloseResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: bool
    def __init__(self, status: bool = ...) -> None: ...

class SendDataRequest(_message.Message):
    __slots__ = ("name", "stringData")
    NAME_FIELD_NUMBER: _ClassVar[int]
    STRINGDATA_FIELD_NUMBER: _ClassVar[int]
    name: str
    stringData: _datagrame_pb2.StringDatagrame
    def __init__(self, name: _Optional[str] = ..., stringData: _Optional[_Union[_datagrame_pb2.StringDatagrame, _Mapping]] = ...) -> None: ...

class RecvDataResponse(_message.Message):
    __slots__ = ("stringData",)
    STRINGDATA_FIELD_NUMBER: _ClassVar[int]
    stringData: _datagrame_pb2.StringDatagrame
    def __init__(self, stringData: _Optional[_Union[_datagrame_pb2.StringDatagrame, _Mapping]] = ...) -> None: ...
