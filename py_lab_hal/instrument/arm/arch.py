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

"""Child Arm Module of Arch.

Arch is a gantry like structure robot arm.
The coordinate system is the Cartesian coordinate system, and it has two
additional rotation axis "A", "B".
Position (X, Y, Z, A, B) = (0, 0, 0, 0, 0)  is set to be the origin position.
The origin is located at the top left corner.
"""

import enum
import logging
import os
import re

from py_lab_hal.cominterface import cominterface
from py_lab_hal.instrument import instrument
from py_lab_hal.instrument.arm import arm


class Arch(arm.Arm):
  """Child Arm Class of Arch."""

  class Commands(enum.Enum):
    """Arch commands."""

    MSG = '[MSG]'
    QUERY_POSITION = '[MSG]coord'
    QUERY_STATE = '[Qstate]'
    QUERY_RESULT = '[Qresult]'
    MOVE_TO = '[MSG]pos'
    MOVE_TO_ORIGIN = '[INI]'
    SEND_FILE = '[PP]'
    START = '[Start]'
    STOP = '[Stop]'
    PAUSE = '[Pause]'
    REPLY_YES = '[YES]'
    REPLY_NO = '[NO]'
    EMS = '[EMS]'

  def __init__(
      self,
      com: cominterface.ComInterfaceClass,
      inst_config: instrument.InstrumentConfig,
  ) -> None:
    super().__init__(com, inst_config)
    self.state = {
        'X': 0.0,
        'Y': 0.0,
        'Z': 0.0,
        'A': 0.0,
        'B': 0.0,
        'J': 0.0,
    }

  def get_state(self) -> dict[str, float]:
    """Return arm's current state."""
    logging.info(self.state)
    return self.state

  def update_state(self) -> None:
    cur_pos = self.get_current_position()
    for axis, value in cur_pos.items():
      self.state[axis] = round(value)

  def move_to_origin(self) -> None:
    cmd = self.Commands.MOVE_TO_ORIGIN.value
    recv_data = self.__query(cmd)
    self.update_state()
    logging.info(recv_data)

  def prepare_move_command(
      self,
      x: float | None,
      y: float | None,
      z: float | None,
      a: float | None,
      b: float | None,
  ) -> str:
    def axis_command(axis: str, pos: float | None) -> str:
      axis_lower = axis.lower()
      if pos is None:
        return f' {axis_lower} {self.state[axis]}'
      return f' {axis_lower} {round(pos)}'

    cmd = self.Commands.MOVE_TO.value
    cmd += axis_command('X', x)
    cmd += axis_command('Y', y)
    cmd += axis_command('Z', z)
    cmd += axis_command('A', a)
    cmd += axis_command('B', b)
    return cmd

  def abs_move_to(
      self,
      x: float | None = None,
      y: float | None = None,
      z: float | None = None,
      a: float | None = None,
      b: float | None = None,
  ) -> None:
    cmd = self.prepare_move_command(x, y, z, a, b)
    recv_data = self.__query(cmd)
    self.update_state()
    logging.info(recv_data)

  def rel_move_to(
      self,
      x: float = 0,
      y: float = 0,
      z: float = 0,
      a: float = 0,
      b: float = 0,
  ) -> None:
    cmd = self.prepare_move_command(
        x + self.state['X'],
        y + self.state['Y'],
        z + self.state['Z'],
        a + self.state['A'],
        b + self.state['B'],
    )
    recv_data = self.__query(cmd)
    self.update_state()
    logging.info(recv_data)

  def __query(self, cmd: str) -> str:
    """Query command."""
    return self.data_handler.query_raw(bytearray(cmd.encode('ascii'))).decode(
        'utf-8'
    )

  def get_current_position(self) -> dict[str, float]:
    """Get current position."""
    recv_data = self.__query(self.Commands.QUERY_POSITION.value)
    cur_pos = dict()
    pattern = r'(\w+)\s+(\d+\.?\d*)'
    for axis, value in re.findall(pattern, recv_data):
      cur_pos[axis] = float(value)
    return cur_pos

  def send_file(self, filepath: str) -> None:
    """Send route.json file."""
    if not os.path.exists(filepath):
      raise FileNotFoundError(f'{filepath} does not exit.')
    cmd = self.Commands.SEND_FILE.value
    with open(filepath, 'r') as file:
      cmd = f'{cmd}{file.read()}'
      resp_data = self.__query(cmd)
      logging.info(resp_data)

  def start(self) -> None:
    """Start to perform route.json file."""
    self.__query(self.Commands.START.value)

  def reply_yes(self) -> None:
    """Reply yes to Arch."""
    self.__query(self.Commands.REPLY_YES.value)

  def reply_no(self) -> None:
    """Reply no to Arch."""
    self.__query(self.Commands.REPLY_NO.value)
