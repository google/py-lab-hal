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

"""Parent abstract class for instrument communication interface."""

from __future__ import annotations

import abc
import dataclasses
import enum
import importlib
import logging
import platform
import re
from typing import Any, Literal, TypeVar

from py_lab_hal.datagram import datagram
from py_lab_hal.logger import logger
from py_lab_hal.util import json_dataclass
from typing_extensions import TypeAlias

T = TypeVar('T', bound=datagram.Datagram)


@dataclasses.dataclass
class ErrorCode:
  """Error Code holder for py-lab-hal communication interfaces."""

  error: str
  code: int | float
  description: str

  def __str__(self):
    return f'Error {self.code}: {self.error} - {self.description}'


class PyLabHalErrorCodes:
  """Py-Lab-Hal Error codes and utility methods."""

  def __init__(self, error_codes: dict[int | float, tuple[str, str]]) -> None:
    self.unknown_err = ErrorCode('UNKNOWN', float('inf'), 'U')
    self._error_codes = {
        code: ErrorCode(error, code, description)
        for code, (error, description) in error_codes.items()
    }

  def get_error(self, code) -> ErrorCode:
    """Get error code details from the error code number."""
    return self._error_codes.get(code, self.unknown_err)


STOPBITS_ONE = 1
STOPBITS_ONE_POINT_FIVE = 1.5
STOPBITS_TWO = 2

PARITY_NONE = 'N'
PARITY_EVEN = 'E'
PARITY_ODD = 'O'
PARITY_MARK = 'M'
PARITY_SPACE = 'S'

VI_ASRL_FLOW_NONE = 0
VI_ASRL_FLOW_XON_XOFF = 1
VI_ASRL_FLOW_RTS_CTS = 2
VI_ASRL_FLOW_DTR_DSR = 4

DEFAULT_CONNECTION_TIMEOUT = 30
DEFAULT_RECV_TIMEOUT = 15
DEFAULT_SEND_TIMEOUT = 15

DEFAULT_READ_TERMINATOR = '\n'
DEFAULT_WRITE_TERMINATOR = '\r\n'

DEFAULT_BAUD_RATE = 9600
DEFAULT_DATA_BITS = 8
DEFAULT_STOP_BITS = STOPBITS_ONE
DEFAULT_PARITY = PARITY_NONE
DEFAULT_FLOW_CONTROL = VI_ASRL_FLOW_NONE

SOCKET_PORT_MIN = 0
SOCKET_PORT_MAX = 65535

USB_REGEX = r'^USB'
SERIAL_REGEX = r'^(ASRL|\/dev\/)'
VXI11_REGEX = r'^TCPIP'

SUPPORT_INTERFACE = [
    'visa',
    'socket',
    'usbtmc',
    'serial',
    'vxi11',
    'debug',
    'dmx',
    'pylabhalboard',
    'http',
    'acute',
    'usb',
    'hislip',
]

TimeoutType: TypeAlias = Literal['connect', 'recv', 'send']


class StopBits(enum.Enum):
  ONE = STOPBITS_ONE
  ONE_POINT_FIVE = STOPBITS_ONE_POINT_FIVE
  TWO = STOPBITS_TWO


class Parity(enum.Enum):
  NONE = PARITY_NONE
  ODD = PARITY_ODD
  EVEN = PARITY_EVEN
  MARK = PARITY_MARK
  SPACE = PARITY_SPACE


class ControlFlow(enum.IntEnum):
  NONE = VI_ASRL_FLOW_NONE
  XON_XOFF = VI_ASRL_FLOW_XON_XOFF
  RST_CTS = VI_ASRL_FLOW_RTS_CTS
  DTR_DSR = VI_ASRL_FLOW_DTR_DSR


@dataclasses.dataclass
class HttpConfig(json_dataclass.DataClassJsonCamelMixIn):
  """The config for connect with http.

  Attributes:
      url (str): The endpoint to be connected
      auth_mode (str): The authentication mode
      login (str):  The login name for endpoint
      method (str): The HTTP methods such as delete, get, head, options, patch,
        post, put, request
      password (str): The password for endpoint
  """

  url: str = ''
  http_auth_mode: Literal['HTTPBasicAuth', 'HTTPDigestAuth', ''] = ''
  login: str = ''
  password: str = ''
  auth_url: str = ''
  auth_mode: Literal['get', 'post', ''] = ''
  auth_data: dict[str, str] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass
class SerialConfig(json_dataclass.DataClassJsonCamelMixIn):
  """The config for connect with serial.

  Attributes:
      baud_rate (int): The baud_rate
      data_bits (int): The data_bits
      stop_bits (StopBits): The stop_bits
      parity (Parity): The baud_rate
      flow_control (ControlFlow): The flow_control
  """

  baud_rate: int = DEFAULT_BAUD_RATE
  data_bits: int = DEFAULT_DATA_BITS
  stop_bits: StopBits = StopBits(DEFAULT_STOP_BITS)
  parity: Parity = Parity(DEFAULT_PARITY)
  flow_control: ControlFlow = ControlFlow(DEFAULT_FLOW_CONTROL)

  def __post_init__(self) -> None:
    if isinstance(self.stop_bits, str):
      self.stop_bits = StopBits(self.stop_bits)

    if isinstance(self.parity, str):
      self.parity = Parity(self.parity)

    if isinstance(self.flow_control, str):
      self.flow_control = ControlFlow(self.flow_control)


@dataclasses.dataclass
class TerminatorConfig(json_dataclass.DataClassJsonCamelMixIn):
  """The config for Terminator.

  Attributes:
      read (str): The read terminator
      write (str): The write terminator
  """

  read: str = DEFAULT_READ_TERMINATOR
  write: str = DEFAULT_WRITE_TERMINATOR


@dataclasses.dataclass
class TimeoutConfig(json_dataclass.DataClassJsonCamelMixIn):
  """The config for timeout.

  Attributes:
      connect (int): The connection timeout in seconds
      recv (int): The recv timeout in seconds
      send (int): The send timeout in seconds
  """

  connect: int = DEFAULT_CONNECTION_TIMEOUT
  recv: int = DEFAULT_RECV_TIMEOUT
  send: int = DEFAULT_SEND_TIMEOUT

  def __getitem__(self, item) -> int:
    return getattr(self, item)


@dataclasses.dataclass
class NetworkConfig(json_dataclass.DataClassJsonCamelMixIn):
  """The config for network.

  Attributes:
      host (str): The IP of the instrument
      port (int): The port for socket
  """

  host: str = ''
  port: int = -1

  def __post_init__(self) -> None:
    if self.host:
      logging.debug('Socket Host Detected checking socket port %d', self.port)
      if self.port < SOCKET_PORT_MIN or self.port > SOCKET_PORT_MAX:
        raise ValueError(f'Port: {self.port} is invalid')

  @property
  def address(self) -> str:
    return f'{self.host}:{self.port}'


@dataclasses.dataclass
class UsbConfig(json_dataclass.DataClassJsonCamelMixIn):
  """Configuration parameters for devices attached over USB.

  Attributes:
      protocol (Any): protocol selected for the communication.
      device_type (Any): Type of the device.
      serial_id (Any): usb serial number of the device.
  """

  protocol: Any = None
  device_type: Any = None
  serial_id: Any = None

  def __post_init__(self) -> None:
    if self.protocol:
      logging.debug('Usb Configuration selected, protocol %s', self.protocol)


@dataclasses.dataclass
class HiSlipConfig(json_dataclass.DataClassJsonCamelMixIn):
  """Configuration parameters for devices attached over HiSlip.

  Attributes:
      vendor_id (str): vendor id code in hislip.
      sub_address (str): sub address in hislip.
  """

  vendor_id: str = 'xx'
  sub_address: str = 'hislip0'


@dataclasses.dataclass
class ConnectConfig(json_dataclass.DataClassJsonCamelMixIn):
  """The config data class for connection.

  For non-windows user, will use the self rewrite backend to handle
  For Windows user, will use the NI-VISA as the backend
  For using socket, will use the python socket as the backend

  If you are using the socket, fill out socket_host, socket_port
  If using visa and it's non Serial, fill out visa_resource
  If using visa and it's Serial, fill out visa_resource, serial_config

  Attributes:
      visa_resource (str): The visa resource that you can find vai sacn.py
      serial_config (SerialConfig): The config for connect with serial
      interface_type (str): The cominterface type to select
      terminator (TerminatorConfig): The terminator config
      timeout (TimeoutConfig): The timeout config
      network (NetworkConfig): The network config
      http_config (HttpConfig): The config for connect with http
      py_lab_hal_board_ip (str): The IP of the py-lab-hal board
      py_lab_hal_board_interface_type (str): The interface_type that
        py_labhal_board will use
  """

  visa_resource: str = ''
  serial_config: SerialConfig = dataclasses.field(default_factory=SerialConfig)
  interface_type: str = ''
  terminator: TerminatorConfig = dataclasses.field(
      default_factory=TerminatorConfig
  )
  timeout: TimeoutConfig = dataclasses.field(default_factory=TimeoutConfig)
  network: NetworkConfig = dataclasses.field(default_factory=NetworkConfig)
  py_lab_hal_board_ip: str = ''
  http_config: HttpConfig = dataclasses.field(default_factory=HttpConfig)
  usb_config: UsbConfig = dataclasses.field(default_factory=UsbConfig)
  hislip_config: HiSlipConfig = dataclasses.field(default_factory=HiSlipConfig)

  py_lab_hal_board_interface_type: str = dataclasses.field(init=False)

  @property
  def name(self) -> str:
    """The name of the ConnectConfig."""
    if self.network.host:
      return self.network.address

    return self.visa_resource

  def __post_init__(self) -> None:
    logger.setup_pylabhal_logger()
    self._auto_select_interface_type()
    self._check_interface_type()

  def _auto_select_interface_type(self) -> None:
    """Auto select the interface type and check the data input."""

    if self.interface_type:
      logging.info('User override the interface_type: %s', self.interface_type)

    else:
      self._check_input()

      if self.network.host:
        self.interface_type = 'socket'
      else:
        self._check_visa()

    if self.py_lab_hal_board_ip:
      self.py_lab_hal_board_interface_type = self.interface_type
      self.interface_type = 'pylabhalboard'

    logging.info('Interface type: %s', self.interface_type)

  def _check_input(self) -> None:
    """Check the user input information.

    User can only input socket_host or visa_resource
    """
    if not bool(self.network.host) ^ bool(self.visa_resource):
      raise ValueError(
          'You can only choose socket_host or visa_resource.\n'
          f'Input socket_host: {self.network.host}\n'
          f'Input visa_resource: {self.visa_resource}\n'
          f'Input name: {self.name}'
      )

  def _check_visa(self) -> None:
    """Check the visa resource."""

    logging.info('Checking VISA resource: %s', self.visa_resource)
    if platform.system() == 'Windows':
      logging.debug('Windows System Detected Using Visa')
      self.interface_type = 'visa'
    elif re.match(USB_REGEX, self.visa_resource):
      logging.debug('USB resource Detected Using USB')
      self.interface_type = 'usbtmc'
    elif re.match(SERIAL_REGEX, self.visa_resource):
      logging.debug('Serial resource Detected Using Serial')
      self.interface_type = 'serial'
    elif re.match(VXI11_REGEX, self.visa_resource):
      logging.debug('VXI11 resource Detected Using VXI11')
      self.interface_type = 'vxi11'
    else:
      raise ValueError(f'Visa_resource: {self.visa_resource} is invalid')

  def _check_interface_type(self) -> None:
    """Check the interface type is supported."""

    if self.py_lab_hal_board_ip:
      self.interface_type = 'pylabhalboard'

    if self.interface_type not in SUPPORT_INTERFACE:
      error_mesg = f'{self.interface_type} is not a valid hw interface!'
      logging.exception(error_mesg)
      raise ValueError(error_mesg)


class ComInterfaceClassBase(metaclass=abc.ABCMeta):
  """The interface for the ComInterface."""

  @abc.abstractmethod
  def _open(self) -> None:
    """Open the interface in child."""
    pass

  @abc.abstractmethod
  def _close(self) -> None:
    """Close the interface in child."""
    pass

  @abc.abstractmethod
  def _send(self, data: bytes) -> None:
    """Send the binary data to the interface.

    Args:
        data (bytes): The binary data send to the interface.
    """
    pass

  @abc.abstractmethod
  def _recv(self, size: int = -1) -> bytes:
    """Recv the binary data with size from the interface.

    Args:
        size (int): The size bytes data to read back. If the size is set to -1
          means read all. Default to -1.

    Returns:
        (bytes): The binary data read back from the interface.
    """
    pass

  @abc.abstractmethod
  def _query(self, data: bytes, size: int = -1) -> bytes:
    """Query the binary data with size to the interface.

    Args:
        data (bytes): The binary data send to the interface.
        size (int): The size bytes data to read back. If the size is set to -1
          means read all. Default to -1.

    Returns:
        (bytes): The binary data read back from the interface.
    """
    pass

  @abc.abstractmethod
  def _set_timeout(self, seconds: int) -> None:
    """Set the timeout to the interface in child.

    Args:
        seconds (int): The timeout setting in seconds.
    """
    pass


class BytesBuffer:
  """byte FIFO buffer."""

  def __init__(self) -> None:
    self._buf = bytearray()
    self.search_index = 0
    self.target_index = 0

  def put(self, data: bytes) -> None:
    """Add data in the end of the buffer.

    Args:
        data (bytes): The new data.
    """
    self._buf.extend(data)

  def get(self, size: int) -> bytearray:
    """Get the data in the buffer with size.

    Args:
        size (int): The size of the data.

    Returns:
        bytearray: The searched data.
    """
    data = self._buf[:size]
    self._buf[:size] = b''
    self.reset_index()
    return data

  def peek(self, size: int) -> bytearray:
    """Peek the data in the front of the buffer.

    Args:
        size (int): The size of the data.

    Returns:
        bytearray: The selected length of the data.
    """
    return self._buf[:size]

  def reset_index(self):
    """Reset the search index in buffer."""
    self.search_index = 0
    self.target_index = 0

  def reset(self) -> None:
    """Reset the buffer."""
    self._buf = bytearray()
    self.reset_index()

  def __len__(self) -> int:
    return len(self._buf)

  def search(self, key: bytes) -> bytearray | None:
    """Search the pattern in the buffer.

    Args:
        key (bytes): The pattern that wanted to search.

    Returns:
        bool: The result if the pattern is in the buffer.
    """
    while self.search_index < len(self._buf):
      if self._buf[self.search_index] == key[self.target_index]:
        self.target_index += 1
      else:
        self.target_index = 0

      self.search_index += 1

      if self.target_index == len(key):
        return self.get(self.search_index)

    return None


class DataHandler:
  """The data handler for interface and datagram."""

  def __init__(self, interface: ComInterfaceClass):
    self.interface = interface

  def _build_bytes_datagram(
      self, data: bytes = b'', size: int = -1
  ) -> datagram.BytesDatagram:
    return datagram.BytesDatagram(
        send_term=self.interface.connect_config.terminator.write.encode(),
        recv_term=self.interface.connect_config.terminator.read.encode(),
        data=data,
        size=size,
    )

  def send(self, command: str, timeout: int = -1) -> None:
    """Send command to the interface.

    Args:
        command (str): The command to send.
        timeout (int, optional): Timeout in seconds. Defaults to -1.
    """
    self.send_raw(command.encode(), timeout=timeout)

  def send_raw(self, data: bytes, timeout: int = -1) -> None:
    """Send raw data to the interface.

    Args:
        data (bytes): The raw data to send.
        timeout (int, optional): Timeout in seconds. Defaults to -1.
    """
    self.send_dataram(self._build_bytes_datagram(data), timeout=timeout)

  def send_dataram(self, dg: datagram.Datagram, timeout: int = -1):
    """Send datagram to the interface.

    Args:
        dg (datagram.Datagram): The datagram to send.
        timeout (int, optional): Timeout in seconds. Defaults to -1.
    """
    self.interface.set_timeout(timeout)
    dg.send(self.interface)

  def recv(self, timeout: int = -1, size: int = -1) -> str:
    """Receive data from the interface.

    Args:
        timeout (int, optional): Timeout in seconds. Defaults to -1.
        size (int, optional): The size to read back. Defaults to -1.

    Returns:
        str: The data from the interface.
    """
    return self.recv_raw(timeout=timeout, size=size).decode()

  def recv_raw(self, timeout: int = -1, size: int = -1) -> bytes:
    """Receive raw data from the interface.

    Args:
        timeout (int, optional): Timeout in seconds. Defaults to -1.
        size (int, optional): The size to read back. Defaults to -1.

    Returns:
        bytes: The raw data from the interface.
    """
    return self.recv_dataram(
        self._build_bytes_datagram(size=size), timeout=timeout
    ).data

  def recv_dataram(self, dg: T, timeout: int = -1) -> T:
    """Receive datagram from the interface.

    Args:
        dg (T): The datagram to receive.
        timeout (int, optional): Timeout in seconds. Defaults to -1.

    Returns:
        T: The datagram from the interface.
    """
    self.interface.set_timeout(timeout)
    dg.recv(self.interface)
    return dg

  def query(self, command: str, timeout: int = -1, size: int = -1) -> str:
    recv = self.query_raw(command.encode(), timeout=timeout, size=size)
    return recv.strip(
        self.interface.connect_config.terminator.read.encode()
    ).decode()

  def query_raw(self, data: bytes, timeout: int = -1, size: int = -1) -> bytes:
    return self.query_datagram(
        self._build_bytes_datagram(data),
        self._build_bytes_datagram(size=size),
        timeout=timeout,
    ).data

  def query_datagram(
      self, send_dg: datagram.Datagram, recv_dg: T, timeout: int = -1
  ) -> T:
    self.interface.set_timeout(timeout)
    self.send_dataram(send_dg)
    return self.recv_dataram(recv_dg)


class ComInterfaceClass(ComInterfaceClassBase):
  """Parent abstract class for ComInterface."""

  def __init__(self, connect_config: ConnectConfig) -> None:
    """The constructor for the class.

    Args:
        connect_config (ConnectConfig): The config for connection
    """
    logging.debug('Init ComInterfaceClass')
    self.connect_config = connect_config
    self.timeout = -1
    self.enable = False
    self.buf = BytesBuffer()

  def __del__(self) -> None:
    self.close()

  def open(self):
    """Open the interface."""
    if self.enable:
      logging.debug('Interface %s is already opened.', self.connect_config.name)
      return

    logging.info('Opening interface %s', self.connect_config.name)
    try:
      self._open()
      self.apply_timeout('connect')
    except:
      logging.exception(
          'Got Error when opening interface %s', self.connect_config.name
      )
      raise
    logging.debug('Finished opening interface %s', self.connect_config.name)
    self.enable = True

  def close(self) -> None:
    """Close the interface when deleting the object."""
    if not self.enable:
      logging.debug('Interface %s is already closed.', self.connect_config.name)
      return

    logging.info('Closing interface %s', self.connect_config.name)
    self._close()
    self.enable = False

  def apply_timeout(
      self,
      timeout_type: TimeoutType,
      timeout: int | None = None,
  ) -> None:
    """The helper function for apply the timeout.

    Args:
        timeout_type (TimeoutType): The type of timeout
        timeout (int | None, optional): Timeout in seconds. Defaults to None.
    """
    if not timeout:
      timeout = self.connect_config.timeout[timeout_type]

    self.set_timeout(timeout)

  def set_timeout(self, seconds: int) -> None:
    """Set the timeout to the interface.

    Args:
        seconds (int): The timeout setting in seconds
    """
    if seconds < 0:
      return

    if self.timeout != seconds:
      self._set_timeout(seconds=seconds)
      logging.debug('Set timeout %d', seconds)
      self.timeout = seconds

  def send_raw(self, data: bytes) -> None:
    """Send RAW command to the interface.

    Args:
        data (bytes): The bytes command
    """
    logging.debug('Send RAW %s', data)
    try:
      self._send(data)
    except:
      logging.exception('Send Raw Error')
      raise

  def recv_raw(self, size: int = -1) -> bytes:
    """Receive RAW command from the interface.

    Args:
        size (int): The size to read back

    Returns:
        (bytes): The RAW reply from the instrument.
    """
    try:
      mesg = self._recv(size)
    except:
      logging.exception('Recv RAW ERROR')
      raise
    logging.debug('Recv RAW %s', mesg)
    return mesg

  def query_raw(self, data: bytes, size: int = -1) -> bytes:
    """Query RAW command to the interface.

    Args:
        data (bytes): The bytes command.
        size (int): The size to read back

    Returns:
        (str): The reply from the instrument.
    """
    logging.debug('Query Send RAW %s', data)
    try:
      mesg = self._query(data, size)
    except:
      logging.exception('Query Raw Error')
      raise
    logging.debug('Query Recv RAW %s', mesg)
    return mesg


def select(connect_config: ConnectConfig) -> ComInterfaceClass:
  """The select function for cominterface.

  This function will auto select the right backend for
  user base on the input information.

  Args:
      connect_config (ConnectConfig): The config for connection

  Returns:
    (ComInterfaceClass): The builded ComInterfaceClass
  """
  logging.debug('Init cominterface select')

  try:
    module_name = connect_config.interface_type
    test_name_list = [item.capitalize() for item in module_name.split('_')]
    class_name = ''.join(test_name_list)

    interface_module = importlib.import_module(
        '.' + module_name, package='py_lab_hal.cominterface'
    )
    logging.info('Selecting %s %s', interface_module, class_name)
    interface_class = getattr(interface_module, class_name)

    instance = interface_class(connect_config=connect_config)

  except (AttributeError, ModuleNotFoundError):
    raise ImportError(
        f'{connect_config.interface_type} is not a valid hw interface!'
    ) from None
  else:
    if not issubclass(interface_class, ComInterfaceClass):
      raise ImportError(f'{interface_class} is not part of the class !')

  logging.debug('Finish cominterface select')
  return instance
