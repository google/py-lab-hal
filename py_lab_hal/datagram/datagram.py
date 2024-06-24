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

"""Datagram for the py-lab-hal cominterface."""

from __future__ import annotations

import abc
from typing import Any, Optional

from py_lab_hal.cominterface import cominterface


class Datagram(metaclass=abc.ABCMeta):
  """The base datagram.

  The datagram is the base class for the communication protocol.
  """

  @abc.abstractmethod
  def send(self, interface: cominterface.ComInterfaceClass) -> None:
    """Sends the datagram to the interface."""
    pass

  @abc.abstractmethod
  def recv(self, interface: cominterface.ComInterfaceClass) -> None:
    """Receives the datagram from the interface."""
    pass


class BytesDatagram(Datagram):
  """The datagram for sending bytes.

  Properties:
    send_term (bytes) : The term to send.
    recv_term (bytes): The term to receive.
    data (bytes): The data to send.
    size (int) : The size of the data to send.
  """

  def __init__(
      self,
      send_term: bytes,
      recv_term: bytes,
      data: bytes = b'',
      size: int = -1,
  ):
    self.send_term = send_term
    self.recv_term = recv_term
    self.data = data
    self.size = size

  def send(self, interface) -> None:
    """Sends the datagram to the interface.

    Args:
      interface: The interface to send the datagram to.
    """
    interface.send_raw(self.pack_data())

  def recv(self, interface) -> None:
    """Receives the datagram from the interface.

    Args:
      interface: The interface to receive the datagram from.
    """
    self.data = interface.recv_raw(self.size)

  def pack_data(self) -> bytes:
    """Packs the data into a byte string.

    Returns:
      The packed data.
    """
    return self.data + self.send_term

  def unpack_data(self) -> bytes:
    """Unpacks the data from a byte string.

    Returns:
      The unpacked data.
    """
    return self.data.rstrip(self.recv_term)


class OneByOneBytesDatagram(BytesDatagram):
  """The datagram for sending one bytes at a time."""

  def send(self, interface) -> None:
    """Sends the datagram to the interface.

    Args:
      interface: The interface to send the datagram to.
    """
    for letter in self.pack_data():
      interface.send_raw(bytes([letter]))


class PngDatagram(Datagram):
  """The datagram for the png image.

  Properties:
    data (bytes): The data of the png image.
    saw_iend (bool): Whether the IEND is received.
  """

  def __init__(self, data: bytes = b''):
    self.data = data
    self.saw_iend = False

  def send(self, interface) -> None:
    """Sends the datagram to the interface.

    Args:
      interface: The interface to send the datagram to.
    """
    pass

  def recv(self, interface) -> None:
    """Receives the datagram from the interface.

    Args:
      interface: The interface to receive the datagram from.
    """
    png_file_signature_size = 8
    self.data = interface.recv_raw(png_file_signature_size)
    while not self.saw_iend:
      self.data += self._read_chunk(interface)

  def _read_chunk(self, interface: cominterface.ComInterfaceClass):
    """Reads a chunk from the interface.

    Args:
      interface: The interface to read the chunk from.

    Returns:
      The chunk data in bytes.
    """
    length_block_size = 4
    chunk_type_block_size = 4
    crc_block_size = 4
    chunk_size = interface.recv_raw(length_block_size)
    chunk_data = interface.recv_raw(
        chunk_type_block_size
        + int.from_bytes(chunk_size, byteorder='big')
        + crc_block_size
    )
    self.saw_iend = b'IEND' in chunk_data
    return chunk_size + chunk_data


class HttpDatagram(Datagram):
  """The datagram for the http protocol.

  Properties:
    url (str): The url to send.
    method (str): The http method to use.
    data (bytes): The data to send.
    headers_dict (dict[str, Any]): The headers to send.
  """

  def __init__(
      self,
      url: str,
      method: str = 'get',
      data: Optional[dict[str, Any]] = None,
      headers_dict: Optional[dict[str, Any]] = None,
  ):
    self.url = url
    self.method = method
    self.data = data
    self.headers_dict = headers_dict

  def config_interface(self, interface):
    """Configures the interface.

    Args:
      interface: The interface to configure.
    """
    for config in ['method', 'data', 'headers_dict']:
      if getattr(self, config) is not None:
        setattr(interface, config, getattr(self, config))

  def send(self, interface) -> None:
    """Sends the datagram to the interface.

    Args:
      interface: The interface to send the datagram to.
    """
    self.config_interface(interface)
    interface.send_raw(self.url.encode())

  def recv(self, interface) -> None:
    pass
