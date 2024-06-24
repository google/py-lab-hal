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

"""Datagrame for the py_lab_hal cominterface."""

from __future__ import annotations

import abc
import dataclasses

from py_lab_hal.util import json_dataclass


@dataclasses.dataclass
class BaseDatagrame(
    json_dataclass.DataClassJsonCamelMixIn, metaclass=abc.ABCMeta
):  # pylint: disable=missing-class-docstring
  # TODO: b/332626341 - Add the class-docstring.
  send_term: str | bytes = ''
  recv_term: str | bytes = ''

  _send_term_bytes: bytes = dataclasses.field(init=False)
  _recv_term_bytes: bytes = dataclasses.field(init=False)

  def __post_init__(self) -> None:
    if isinstance(self.send_term, str):
      self._send_term_bytes = self.send_term.encode()
    elif isinstance(self.send_term, bytes):
      self._send_term_bytes = self.send_term
    else:
      raise RuntimeError

    if isinstance(self.recv_term, str):
      self._recv_term_bytes = self.recv_term.encode()
    elif isinstance(self.recv_term, bytes):
      self._recv_term_bytes = self.recv_term
    else:
      raise RuntimeError

  @property
  def send_term_bytes(self) -> bytes:
    return self._send_term_bytes

  @property
  def recv_term_bytes(self) -> bytes:
    return self._recv_term_bytes

  @abc.abstractmethod
  def pack_data(self) -> None:
    pass

  @abc.abstractmethod
  def unpack_data(self) -> None:
    pass


@dataclasses.dataclass
class StringDatagrame(BaseDatagrame):  # pylint: disable=missing-class-docstring.
  # TODO: b/332626341 - Add the class-docstring.

  str_data: str = ''
  bytes_data: bytes = b''

  def __post_init__(self) -> None:
    super().__post_init__()
    if not bool(self.str_data) ^ bool(self.bytes_data):
      raise RuntimeError

    if self.str_data:
      self.pack_data()

  def str2bytes(self) -> bytes:
    self.bytes_data = self.str_data.encode()
    return self.bytes_data

  def bytes2str(self) -> str:
    self.str_data = self.bytes_data.decode()
    return self.str_data

  def pack_data(self) -> None:
    data = self.str_data.encode()
    data += self._send_term_bytes
    self.bytes_data = data
    self.bytes2str()

  def unpack_data(self) -> None:
    self.str_data = self.bytes_data.rstrip(self._recv_term_bytes).decode()
    self.str2bytes()
