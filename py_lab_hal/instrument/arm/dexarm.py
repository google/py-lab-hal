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

"""Child Arm Module of Dexarm.

Dexarm is an articulated robot arm.
The coordinate system is the Cartesian coordinate system.
The origin is located at (X, Y, Z) = (0, 0, 0).
Use G-Code control commands.
"""

import enum
import logging
import re
import time

from py_lab_hal.cominterface import cominterface
from py_lab_hal.instrument import instrument
from py_lab_hal.instrument.arm import arm

Y_OFFSET = 300.0


class Dexarm(arm.Arm):
  """Child Arm Class of Dexarm."""

  class Mode(enum.Enum):
    G0 = 'G0'  # Rapid movement
    G1 = 'G1'  # Linear movement

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
        'E': 0.0,
        'A': 0.0,
        'B': 0.0,
        'C': 0.0,
    }
    self.time_out = 10

  def __send(self, cmd: str, wait: bool = True):
    """Send command to arm.

    Args:
        cmd (str): command to send.
        wait (bool): if wait is true, then wait until arm response ok.
    """
    self.data_handler.send(cmd)
    if not wait:
      return
    cur_time = time.time()
    while time.time() < cur_time + self.time_out:
      recv_data = self.data_handler.recv()
      if recv_data and recv_data.find('ok') >= 0:
        return
    logging.warning('Wait for response ok time out.')

  def wait(self) -> None:
    """Wait until previous operation finish."""
    self.__send('M400')

  def get_state(self) -> dict[str, float]:
    """Return arm's current state."""
    logging.info('The status of arm is %s', self.state)
    return self.state

  def update_state(self) -> None:
    """Get current position and update state."""
    cur_pos = self.get_current_position()
    if not cur_pos:
      logging.warning('Fail to update state.')
      return
    for i in self.state:
      self.state[i] = cur_pos[i]

  def move_to_origin(self) -> None:
    """Move to the original position."""
    self.__send('M1112')
    self.update_state()

  def prepare_move_command(
      self,
      x: float | None,
      y: float | None,
      z: float | None,
      e: float | None,
      feedrate: float,
      mode: str,
  ) -> str:
    def axis_command(axis: str, pos: float | None) -> str:
      if pos is None:
        return f'{axis}{self.state[axis]+(0.0 if axis != "Y" else Y_OFFSET)}'
      return f'{axis}{round(pos)+(0.0 if axis != "Y" else Y_OFFSET)}'

    cmd = f'{mode}F{feedrate}'
    cmd += axis_command('X', x)
    cmd += axis_command('Y', y)
    cmd += axis_command('Z', z)
    cmd += axis_command('E', e)
    return cmd

  def abs_move_to(
      self,
      x: float | None = None,
      y: float | None = None,
      z: float | None = None,
      e: float | None = None,
      feedrate: int = 10_000,
      mode: str = Mode.G1.value,
  ) -> None:
    cmd = self.prepare_move_command(x, y, z, e, feedrate, mode)
    self.__send(cmd)
    self.update_state()

  def rel_move_to(
      self,
      x: float = 0,
      y: float = 0,
      z: float = 0,
      e: float = 0,
      feedrate: int = 10_000,
      mode: str = Mode.G1.value,
  ) -> None:
    cmd = self.prepare_move_command(
        x + self.state['X'],
        y + self.state['Y'],
        z + self.state['Z'],
        e + self.state['E'],
        feedrate,
        mode,
    )
    self.__send(cmd)
    self.update_state()

  def get_current_position(self) -> dict[str, float]:
    """Get current position."""
    self.__send('M114', wait=False)
    coor = [i for i in self.state]
    cur_pos = {i: 0.0 for i in coor}
    cur_time = time.time()
    while time.time() < cur_time + self.time_out:
      recv_data = self.data_handler.recv()
      if recv_data.find('X:') > -1:
        val = re.findall(r'[-+]?\d*\.\d+|\d+', recv_data)
        for i, value in enumerate(val):
          cur_pos[coor[i]] = float(value) - (0.0 if i != 'Y' else Y_OFFSET)
      if recv_data.find('DEXARM Theta') > -1:
        val = re.findall(r'[-+]?\d*\.\d+|\d+', recv_data)
        for i, value in enumerate(val):
          cur_pos[coor[i + coor.index('A')]] = float(value)
      if recv_data.find('ok') > -1:
        return cur_pos
    logging.warning('Get current position time out.')
    return {}

  def set_origin(self) -> None:
    """Set current position to be the origin."""
    self.__send('G92 X0 Y0 Z0 E0')
    self.update_state()

  def delay(self, value: float, unit: str = 's') -> None:
    """Delay {value} {unit} to perform next movement."""
    if unit in ['s', 'ms']:
      cmd = f'G4 S{str(value)}' if unit == 's' else f'G4 P{str(value)}'
      self.__send(cmd)
    else:
      logging.warning('Unit %s is not supported.', unit)
