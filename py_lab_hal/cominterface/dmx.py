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

"""Child ComInterfaceClass Module of DMX."""

import struct

from py_lab_hal.cominterface import serial

DMX_SIZE = 0x200

START_MESSAGE = 0x7E
END_MESSAGE = 0xE7


class Dmx(serial.Serial):
  """DMX instrument interface client.

  Attributes:
    data: DMX data to be sent.
  """

  SET_DMX_LABEL = 4
  SEND_DMX_LABEL = 6

  def _open(self) -> None:
    super()._open()
    self.connect_config.interface_type = 'dmx'

    self.data = [0] * DMX_SIZE
    self.set_dmx_parameters()

  def format_data(self, label: int, data: bytes) -> bytes:
    """Format data to be sent to the DMX device.

    Args:
      label (int): Label of the data.
      data (bytes): Data to be sent.

    Returns:
      bytes: Formatted data.
    """
    header = struct.pack('<BBH', START_MESSAGE, label, len(data))
    tail = struct.pack('<B', END_MESSAGE)
    return header + data + tail

  def send_raw(self, data: bytes) -> None:
    """Send raw data to the DMX device.

    Args:
      data (bytes): Data to be sent.
    """
    self._send(data)

  def set_dmx_parameters(
      self,
      output_break_time: int = 9,
      mab_time: int = 1,
      output_rate: int = 40,
      user_defined_bytes: bytes = b'',
  ) -> None:
    """Set timing aspects of the DMX signal.

    Args:
        output_break_time (int, optional): Sets the Break time interval for the
          DMX packets. Integers between 9 and 127. A base unit of 10.67
          microseconds is used,. Defaults to 9.
        mab_time (int, optional): Sets the MAB (Mark After Break) time interval
          for the DMX packets. Integers between 1 and 127. A base unit of 10.67
          microseconds is used. Defaults to 1.
        output_rate (int, optional): Set the rate of DMX Packet sending.
          Integers between 0 and 40 are accepted. 1 through 40 will set the rate
          in Hz. 0 means sent as fast as possible. Defaults to 40.
        user_defined_bytes (bytes, optional): User defined configuration data.
          Defaults to b''.

    Raises:
        ValueError: Length of user_defined_bytes must not be greater than 512.
        ValueError: output_break_time must be between 9 and 127.
        ValueError: mab_time must be between 1 and 127.
        ValueError: output_rate must be between 0 and 40.
    """

    if len(user_defined_bytes) > 512:
      raise ValueError(
          'Length of user_defined_bytes must not be greater than 512'
      )
    if not 9 <= output_break_time <= 127:
      raise ValueError('output_break_time must be between 9 and 127')
    if not 1 <= mab_time <= 127:
      raise ValueError('mab_time must be between 1 and 127')
    if not 0 <= output_rate <= 40:
      raise ValueError('output_rate must be between 0 and 40')

    data = struct.pack(
        '<HIII',
        len(user_defined_bytes),
        output_break_time,
        mab_time,
        output_rate,
    )
    msg = self.format_data(self.SET_DMX_LABEL, data + user_defined_bytes)

    self.send_raw(msg)

  def submit(self) -> None:
    """Submit the channel state to the DMX Device over serial.

    Raises:
        ValueError: Length of data must be 512.
    """
    if len(self.data) != DMX_SIZE:
      raise ValueError('Length of data must be 512')
    msg = self.format_data(self.SEND_DMX_LABEL, bytes(self.data))
    self.send_raw(msg)

  def clear(self) -> None:
    """Sets all channels to 0."""
    self.set_all(0)

  def set_all(self, value: int) -> None:
    """Set all channels with value.

    Args:
      value (int): Integer from 1 to 512
    """
    self.data = [value] * DMX_SIZE

  def set_value(self, channel: int, value: int) -> None:
    """Set a channel value.

    Args:
      channel (int): Integer from 1 to 512
      value (int): Integer from
    """
    self.data[channel - 1] = value

  def _query(self, data, size) -> bytes:
    raise NotImplementedError('DMX did not support read and query.')

  def _recv(self, data, size) -> bytes:
    raise NotImplementedError('DMX did not support read and query.')
