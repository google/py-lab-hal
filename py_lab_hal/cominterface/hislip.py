# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Child ComInterfaceClass Module of HiSlip."""

import enum
import struct

from py_lab_hal.cominterface import cominterface
from py_lab_hal.cominterface import socket

PROTOCOL_VERSION_MAX = 256
MAXIMUM_DATA_SIZE = 256
HEADER_SIZE = 16
MAXIMUM_MESSAGE_SIZE = MAXIMUM_DATA_SIZE + HEADER_SIZE


DEFAULT_MESSAGE_ID = 0xFFFFFF00
DEFAULT_MAX_MSG_SIZE = 1 << 20

PROLOGUE = b'HS'

MESSAGE_TYPE_OFFSET = 2
CONTROL_CODE_OFFSET = 3
MESSAGE_PARAMETER_OFFSET = 4
PAYLOAD_LENGTH_OFFSET = 8
DATA_OFFSET = 16


class MessageType(enum.IntEnum):
  """Message type."""

  # Minimum HiSLIP 1.0
  INITIALIZE = 0
  INITIALIZE_RESPONSE = 1
  FATAL_ERROR = 2
  ERROR = 3
  ASYNC_LOCK = 4
  ASYNC_LOCK_RESPONSE = 5
  DATA = 6
  DATA_END = 7
  DEVICE_CLEAR_COMPLETE = 8
  DEVICE_CLEAR_ACKNOWLEDGE = 9
  ASYNC_REMOTE_LOCAL_CONTROL = 10
  ASYNC_REMOTE_LOCAL_RESPONSE = 11
  TRIGGER = 12
  INTERRUPTED = 13
  ASYNC_INTERRUPTED = 14
  ASYNC_MAXIMUM_MESSAGE_SIZE = 15
  ASYNC_MAXIMUM_MESSAGE_SIZERESPONSE = 16
  ASYNC_INITIALIZE = 17
  ASYNC_INITIALIZE_RESPONSE = 18
  ASYNC_DEVICE_CLEAR = 19
  ASYNC_SERVICE_REQUEST = 20
  ASYNC_STATUS_QUERY = 21
  ASYNC_STATUS_RESPONSE = 22
  ASYNC_DEVICE_CLEAR_ACKNOWLEDGE = 23
  ASYNC_LOCK_INFO = 24
  ASYNC_LOCK_INFO_RESPONSE = 25

  # Minimum HiSLIP 2.0
  GET_DESCRIPTORS = 26
  GET_DESCRIPTORS_RESPONSE = 27
  START_TLS = 28
  ASYNC_START_TLS = 29
  ASYNC_START_TLS_RESPONSE = 30
  END_TLS = 31
  ASYNC_END_TLS = 32
  ASYNC_END_TLS_RESPONSE = 33
  GET_SAS_MECHANISM_LIST = 34
  GET_SAS_MECHANISM_LIST_RESPONSE = 35
  AUTHENTICATION_START = 36
  AUTHENTICATION_EXCHANGE = 37
  AUTHENTICATION_RESULT = 38


class FatalErrorCode(enum.IntEnum):
  """Fatal error code."""

  UNIDENTIFIED_ERROR = 0
  POORLY_FORMED_MESSAGE_HEADER = 1
  ATTEMPT_TO_USE_CONNECTION_WITHOUT_BOTH_CHANNELS_ESTABLISHED = 2
  INVALID_INITIALIZATION_SEQUENCE = 3
  SERVER_REFUSED_CONNECTION_DUE_TO_MAXIMUM_NUMBER_OF_CLIENTS_EXCEEDED = 4
  SECURE_CONNECTION_FAILED = 5


class ErrorCode(enum.IntEnum):
  """Error code."""

  UNIDENTIFIED_ERROR = 0
  UNRECOGNIZED_MESSAGE_TYPE = 1
  UNRECOGNIZED_CONTROL_CODE = 2
  UNRECOGNIZED_VENDOR_DEFINED_MESSAGE = 3
  MESSAGE_TOO_LARGE = 4
  AUTHENTICATION_FAILED = 5


HEADER_FORMAT = '!2sBBIQ'


def is_message_delivered(message_type: MessageType, data: bytes) -> bool:
  """Check if the message is delivered.

  Args:
    message_type (MessageType): The message type.
    data (bytes): The data.

  Returns:
    bool: True if the message is delivered.
  """

  if not data:
    return False
  return message_type == MessageType.DATA_END and data.endswith(b'\n')


def build_mesg_para(message_parameter):
  """Build the message parameter."""

  def _to_bytes(data) -> bytes:
    if isinstance(data, str):
      return data.encode()
    if len(message_parameter) == 1:
      return struct.pack('>I', data)

    return struct.pack('>H', data)

  pro = [message_parameter]
  if isinstance(message_parameter, list):
    pro = message_parameter

  return struct.unpack('!I', b''.join([_to_bytes(data) for data in pro]))[0]


# Will be add in the python 3.12
def batch(iterable, n=1):
  l = len(iterable)
  return [iterable[ndx : min(ndx + n, l)] for ndx in range(0, l, n)]


def get_message_parameter(
    raw_message_parameter: bytes, message_type: MessageType
):
  """Decode message parameter.

  Args:
    raw_message_parameter (bytes): The raw message parameter.
    message_type (MessageType): The message type.

  Returns:
    message_parameter (bytes): The message parameter.
  """
  if message_type == MessageType.INITIALIZE_RESPONSE:
    return struct.unpack('!4xHH8x', raw_message_parameter)
  elif message_type == MessageType.ASYNC_INITIALIZE_RESPONSE:
    return struct.unpack('!4x4s8x', raw_message_parameter)
  return raw_message_parameter


class HiSlipData:
  """HiSlipData Class.

  Properties:
    header (bytes): The header.
    message_type (MessageType): The message type.
    control_code (int): The control code.
    message_parameter (bytes): The message parameter.
    payload_length (int): The payload length.
    data (bytes): The data.
    full_message (bytes): The full message.
  """

  def __init__(
      self,
      message_type: MessageType = MessageType.INITIALIZE,
      control_code: int = 0,
      message_parameter=0,
      data=b'',
      header=b'',
  ):
    self.header = header

    self.message_type = message_type
    self.control_code = control_code
    self.message_parameter = message_parameter
    self.payload_length = 0
    self.data = data

    self.full_message = b''

    if self.header:
      self.split_header()
    else:
      self.build_herder()
      self.build_message()

  def build_message(self):
    """Build the message."""
    self.full_message = self.header + self.data

  def build_herder(self):
    self.header = struct.pack(
        HEADER_FORMAT,
        PROLOGUE,
        self.message_type,
        self.control_code,
        self.message_parameter,
        len(self.data),
    )

  def split_header(self):
    """Split the header."""
    (
        _,
        message_type_raw,
        self.control_code,
        _,
        self.payload_length,
    ) = struct.unpack(HEADER_FORMAT, self.header)

    self.message_type = MessageType(message_type_raw)

    self.message_parameter = get_message_parameter(
        self.header, self.message_type
    )


def send_hislip_data(
    socket_channel: socket.Socket, hs_data: HiSlipData
) -> None:
  socket_channel.send_raw(hs_data.full_message)


def recv_hislip_header(socket_channel: socket.Socket) -> HiSlipData:
  return HiSlipData(header=socket_channel.recv_raw(HEADER_SIZE))


class Hislip(cominterface.ComInterfaceClass):
  """Child ComInterfaceClass Module of socket."""

  message_id: int
  session_id: int
  last_message_id: int
  rmt_delivered: bool
  sync_channel: socket.Socket
  async_channel: socket.Socket

  def _update_message_id(self, new_message_id: int):
    """Update the message id.

    Args:
      new_message_id (int): The new message id.
    """
    self.last_message_id = self.message_id
    self.message_id = new_message_id

  def _open(self) -> None:
    self._sync_channel_init()
    self._async_channel_init()
    self.connect_config.interface_type = 'hislip'

    self.message_id = DEFAULT_MESSAGE_ID
    self.last_message_id = DEFAULT_MESSAGE_ID
    self.rmt_delivered = False

  def _close(self) -> None:
    self.sync_channel.close()
    self.async_channel.close()

  def _set_timeout(self, seconds: int) -> None:
    self.sync_channel.set_timeout(seconds)
    self.async_channel.set_timeout(seconds)

  def _sync_channel_init(self):
    """Initialize the sync channel."""

    self.sync_channel = socket.Socket(connect_config=self.connect_config)
    self.sync_channel.open()
    mesg_para = build_mesg_para([
        PROTOCOL_VERSION_MAX,
        self.connect_config.hislip_config.vendor_id,
    ])
    send_hislip_data(
        self.sync_channel,
        HiSlipData(
            message_type=MessageType.INITIALIZE,
            message_parameter=mesg_para,
            data=self.connect_config.hislip_config.sub_address.encode(),
        ),
    )
    init_response = recv_hislip_header(self.sync_channel)
    self.overlap_mode = init_response.control_code
    # Get SessionID
    assert isinstance(init_response.message_parameter, tuple)
    _, self.session_id = init_response.message_parameter

  def _async_channel_init(self):
    """Initialize the async channel."""

    self.async_channel = socket.Socket(connect_config=self.connect_config)
    self.async_channel.open()
    send_hislip_data(
        self.async_channel,
        HiSlipData(
            message_type=MessageType.ASYNC_INITIALIZE,
            message_parameter=self.session_id,
        ),
    )
    recv_hislip_header(self.async_channel)
    send_hislip_data(
        self.async_channel,
        HiSlipData(
            message_type=MessageType.ASYNC_MAXIMUM_MESSAGE_SIZE,
            data=struct.pack('!Q', DEFAULT_MAX_MSG_SIZE),
        ),
    )
    recv_hislip_header(self.async_channel)

  def _build_data_message(
      self, last_data: bool, data_chunk: bytes
  ) -> HiSlipData:
    """Build the data message.

    Args:
      last_data (bool): True if it is the last data.
      data_chunk (bytes): The data chunk.

    Returns:
      HiSlipData: The message.
    """

    if last_data:
      mesg_type = MessageType.DATA_END
    else:
      mesg_type = MessageType.DATA

    return HiSlipData(
        mesg_type,
        self.rmt_delivered,
        self.message_id,
        data_chunk,
    )

  def _send(self, data: bytes) -> None:
    split_data = batch(data, MAXIMUM_DATA_SIZE)
    len_data = len(split_data)
    for i, data_chunk in enumerate(split_data, 1):
      send_hislip_data(
          self.sync_channel, self._build_data_message(i == len_data, data_chunk)
      )
      self._update_message_id(self.message_id + 2)

  def _raise_error(self, error_code: ErrorCode, client_raise: bool):
    """Raise error.

    Args:
      error_code (ErrorCode): The error code.
      client_raise (bool): True if the client raise the error.

    Raises:
        RuntimeError: Raise error.
    """
    if client_raise:
      self._send_error_to_server(error_code)
    raise RuntimeError(f'ERROR with {error_code.name}')

  def _raise_fatal_error(self, error_code: FatalErrorCode, client_raise: bool):
    """Raise fatal error.

    Args:
      error_code (FatalErrorCode): The error code.
      client_raise (bool): True if the client raise the error.

    Raises:
        RuntimeError: Raise error.
    """
    if client_raise:
      self._send_fatal_error_to_server(error_code)
    raise RuntimeError(f'FATALERROR with {error_code.name}')

  def _send_error_to_server(self, error_code: ErrorCode):
    """Send error to server.

    Args:
      error_code (ErrorCode): The error code.
    """
    send_hislip_data(
        self.sync_channel, HiSlipData(MessageType.ERROR, error_code)
    )
    self.close()

  def _send_fatal_error_to_server(self, error_code: FatalErrorCode):
    """Send fatal error to server.

    Args:
      error_code (ErrorCode): The error code.
    """
    send_hislip_data(
        self.sync_channel, HiSlipData(MessageType.FATAL_ERROR, error_code)
    )
    self.close()

  def _recv(self, size=0) -> bytes:
    full_data = b''
    recv_data_type = [MessageType.DATA, MessageType.DATA_END]
    while True:
      recv_hs_header = recv_hislip_header(self.sync_channel)
      mesg_id_mismatch = (
          recv_hs_header.message_parameter != self.last_message_id
      )

      if mesg_id_mismatch and self.overlap_mode:
        self._raise_error(ErrorCode.UNRECOGNIZED_MESSAGE_TYPE, True)

      if recv_hs_header.message_type not in recv_data_type:
        self._raise_error(ErrorCode.UNRECOGNIZED_MESSAGE_TYPE, True)

      if recv_hs_header.payload_length > 0:
        data = self.sync_channel.recv_raw(recv_hs_header.payload_length)
      else:
        data = b''

      self.rmt_delivered = is_message_delivered(
          recv_hs_header.message_type, data
      )

      full_data = full_data + data
      if recv_hs_header.message_type == MessageType.DATA_END:
        return full_data

  def _query(self, data, size) -> bytes:
    self.send_raw(data)
    return self.recv_raw(size)
