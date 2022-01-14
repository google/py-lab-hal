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

"""Child ComInterfaceClass Module of Debug."""

import queue
from py_lab_hal.cominterface import cominterface


class Debug(cominterface.ComInterfaceClass):
  """Child ComInterfaceClass Module of debug."""

  _send_queue: queue.SimpleQueue[bytes]
  _recv_queue: queue.SimpleQueue[bytes]

  def _open(self) -> None:
    self.connect_config.interface_type = 'serial'
    self.connect_config.terminator.read = ''
    self.connect_config.terminator.write = ''
    self._send_queue = queue.SimpleQueue()
    self._recv_queue = queue.SimpleQueue()

  def _close(self) -> None:
    pass

  def _send(self, data) -> None:
    self._send_queue.put_nowait(data)

  def _recv(self, size=0) -> bytes:
    return self._recv_queue.get_nowait()

  def _query(self, data) -> bytes:
    self._send(data)
    return self._recv()

  def _set_timeout(self, seconds) -> None:
    pass

  def get_send_queue(self) -> bytes:
    return self._send_queue.get_nowait()

  def clean_send_queue(self) -> None:
    while not self._send_queue.empty():
      _ = self._send_queue.get_nowait()

  def push_recv_queue(self, data) -> None:
    self._recv_queue.put_nowait(data)
