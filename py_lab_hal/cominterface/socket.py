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

"""Child ComInterfaceClass Module of socket."""

import logging
import socket

from py_lab_hal.cominterface import cominterface


BUFF_SIZE = 20480  # set it to be the same as pyvisa


class Socket(cominterface.ComInterfaceClass):
  """Child ComInterfaceClass Module of socket."""

  _socket: socket.socket

  def _open(self) -> None:
    self.connect_config.interface_type = 'socket'
    self._socket = socket.socket()
    logging.info(
        'Connecting to %s port %d',
        self.connect_config.network.host,
        self.connect_config.network.port,
    )
    self._socket.connect((
        self.connect_config.network.host,
        self.connect_config.network.port,
    ))

  def _close(self) -> None:
    self._socket.close()

  def _send(self, data: bytes) -> None:
    self._socket.send(data)

  def _recv(self, size) -> bytes:
    end_term = self.connect_config.terminator.read.encode()
    while True:
      if size > 0:
        if len(self.buf) >= size:
          return bytes(self.buf.get(size))
      else:
        ans = self.buf.search(end_term)
        if ans is not None:
          return bytes(ans)
      self.buf.put(self._socket.recv(BUFF_SIZE))

  def _query(self, data, size) -> bytes:
    self.send_raw(data)
    return self.recv_raw(size)

  def _set_timeout(self, seconds) -> None:
    self._socket.settimeout(seconds)
