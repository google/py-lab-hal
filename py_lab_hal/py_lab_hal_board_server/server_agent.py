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

"""Module of Server Side Agent."""

from __future__ import annotations

from py_lab_hal import scan
from py_lab_hal.cominterface import cominterface


class ServerAgent(object):
  """Handle the communication between gRPC and board."""

  _instance = None

  def __init__(self) -> None:
    ServerAgent._instance = self
    self.interface_dict: dict[str, cominterface.ComInterfaceClass] = {}
    self.is_busy = False

  @staticmethod
  def get_instance() -> ServerAgent:
    if not ServerAgent._instance:
      return ServerAgent()
    return ServerAgent._instance

  def scan(self) -> str:
    return scan.main()

  def reg_sys(self) -> None:
    self.is_busy = True

  def del_sys(self) -> None:
    self.is_busy = False

  def reg_device(self, name: str, com_con: cominterface.ConnectConfig) -> bool:
    if name in self.interface_dict:
      return False
    self.interface_dict[name] = cominterface.select(connect_config=com_con)
    return True

  def close(self, name: str):
    inst = self.interface_dict.pop(name)
    inst.__del__()
    return True

  def send(self, name: str, data: bytes) -> None:
    """Send the binary command to the interface.

    Args:
        name (str): The name of the interface
        data (bytes): The binary command send to the interface
    """
    self.interface_dict[name].send_raw(data)

  def read(self, name: str) -> bytes:
    """Recv the binary command from the interface.

    Args:
        name (str): The name of the interface

    Returns:
        (bytes): The binary information from the interface.
    """
    return self.interface_dict[name].recv_raw()
