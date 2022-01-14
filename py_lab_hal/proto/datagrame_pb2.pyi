from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class StringDatagrame(_message.Message):
    __slots__ = ("sendTerm", "recvTerm", "strData", "bytesData")
    SENDTERM_FIELD_NUMBER: _ClassVar[int]
    RECVTERM_FIELD_NUMBER: _ClassVar[int]
    STRDATA_FIELD_NUMBER: _ClassVar[int]
    BYTESDATA_FIELD_NUMBER: _ClassVar[int]
    sendTerm: str
    recvTerm: str
    strData: str
    bytesData: bytes
    def __init__(self, sendTerm: _Optional[str] = ..., recvTerm: _Optional[str] = ..., strData: _Optional[str] = ..., bytesData: _Optional[bytes] = ...) -> None: ...
