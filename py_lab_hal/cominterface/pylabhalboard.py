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

"""Child ComInterfaceClass Module of pylabhal board."""

from py_lab_hal.cominterface import cominterface
from py_lab_hal.py_lab_hal_board_client import client_agent


class Pylabhalboard(cominterface.ComInterfaceClass):
  """Child ComInterfaceClass Module of socket."""

  agent: client_agent.ClientAgent
  name: str

  def _open(self) -> None:
    # self.connect_config.interface_type = 'pylabhalboard'
    self.agent = client_agent.ClientAgent.get_instance()
    self.agent.set_connection(self.connect_config.py_lab_hal_board_ip)
    respond = self.agent.inst_init(self.connect_config)
    self.name = respond.name

  def _close(self) -> None:
    self.agent.close_connection(self.name)

  def _send(self, data: bytes) -> None:
    self.agent.send(self.name, data)

  def _recv(self) -> bytes:
    return self.agent.recv(self.name)

  def _query(self, data: bytes) -> bytes:
    return self.agent.query(self.name, data)

  def _set_timeout(self, seconds: int) -> None:
    pass

  def scan(self) -> None:
    respond = self.agent.basic_system('SYSTEM_SCAN')
    print(respond.scan_info)
