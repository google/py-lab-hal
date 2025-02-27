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
The origin is located at (X, Y, Z) = (0, 300, 0).
Use G-Code control commands.
"""

from __future__ import annotations

import enum
import logging
import re

from py_lab_hal.cominterface import cominterface
from py_lab_hal.instrument import instrument
from py_lab_hal.instrument.arm import arm

DEXARM_READ_TIMEOUT = 30
DUMMY_RESPONSE_PREFIX = 'wait\n'
REAL_POSITION_REGEX = re.compile(
    r'Real position X:([-\d.]+) Y:([-\d.]+) Z:([-\d.]+) E:([-\d.]+)'
)
DEXARM_THETA_REGEX = re.compile(
    r'DEXARM Theta A:([-\d.]+)  Theta B:([-\d.]+)  Theta C:([-\d.]+)'
)


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
    com.connect_config.terminator.read = 'ok\n'
    super().__init__(com, inst_config)

  def wait(self) -> None:
    """Wait until previous operation finish."""
    self.query('M400')

  def move_to_origin(self) -> None:
    """Move to the original position."""
    self.query('M1112')

  def prepare_move_command(
      self,
      x: float | None,
      y: float | None,
      z: float | None,
      e: float | None,
      feedrate: float,
      mode: str,
  ) -> str:
    """Prepare move command.

    Args:
      x (float): x-axis coordinate. Unit: mm
      y (float): y-axis coordinate. Unit: mm
      z (float): z-axis coordinate. Unit: mm
      e (float): e-axis coordinate. Unit: mm
      feedrate (float): feedrate. Unit: mm/s
      mode (str): G1 or G0.

    Returns:
      str: move command.
    """

    def axis_command(axis: str, pos: float | None) -> str:
      return f'{axis}{round(pos)}' if pos is not None else ''

    cmd = f'{mode}F{feedrate}'
    cmd += axis_command('X', x)
    cmd += axis_command('Y', y)
    cmd += axis_command('Z', z)
    cmd += axis_command('E', e)
    return cmd

  def absolute_move_to(
      self,
      x: float | None = None,
      y: float | None = None,
      z: float | None = None,
      e: float | None = None,
      feedrate: int = 10_000,
      mode: str = Mode.G1.value,
  ) -> None:
    cmd = self.prepare_move_command(x, y, z, e, feedrate, mode)
    self.query(cmd)

  def relative_move_to(
      self,
      x: float = 0,
      y: float = 0,
      z: float = 0,
      e: float = 0,
      feedrate: int = 10_000,
      mode: str = Mode.G1.value,
  ) -> None:
    curren_pos = self.get_current_position()
    cmd = self.prepare_move_command(
        x + curren_pos['X'],
        y + curren_pos['Y'],
        z + curren_pos['Z'],
        e + curren_pos['E'],
        feedrate,
        mode,
    )
    self.query(cmd)

  def get_current_position(self) -> dict[str, float]:
    """Get current position."""
    resp = self.query('M114')
    result = {}
    if real_position_match := REAL_POSITION_REGEX.search(resp):
      x, y, z, e = real_position_match.groups()
      result.update(
          {'X': float(x), 'Y': float(y), 'Z': float(z), 'E': float(e)}
      )
    else:
      logging.warning('Get position failed.')
      return {}

    if dexarm_theta_match := DEXARM_THETA_REGEX.search(resp):
      a, b, c = dexarm_theta_match.groups()
      result.update({'A': float(a), 'B': float(b), 'C': float(c)})
    else:
      logging.warning('Get theta failed.')
      return {}
    return result

  def set_origin(self) -> None:
    """Set current position to be the origin."""
    self.query('G92 X0 Y0 Z0 E0')

  def delay(self, value: float, unit: str = 's') -> None:
    """Delay {value} {unit} to perform next movement."""
    if unit in ['s', 'ms']:
      cmd = f'G4 S{str(value)}' if unit == 's' else f'G4 P{str(value)}'
      self.query(cmd)
    else:
      logging.warning('Unit %s is not supported.', unit)

  def query(self, cmd: str) -> str:
    """Dexarm wrapper query function."""
    resp = self.data_handler.query(cmd, timeout=DEXARM_READ_TIMEOUT)
    return re.sub(f'^({DUMMY_RESPONSE_PREFIX})+', '', resp)
