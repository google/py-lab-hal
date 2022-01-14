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

"""Parent Abstract Module of Arm."""

import abc

from py_lab_hal.cominterface import cominterface
from py_lab_hal.instrument import instrument


class Arm(instrument.Instrument, metaclass=abc.ABCMeta):
  """Parent Abstract Class of Arm."""

  def __init__(
      self,
      com: cominterface.ComInterfaceClass,
      inst_config: instrument.InstrumentConfig,
  ) -> None:
    super().__init__(com, inst_config)
    self.state = {}

  def open_instrument(self):
    super().open_instrument()
    self.reset_state()
    self.move_to_origin()
    self.update_state()

  @abc.abstractmethod
  def update_state(self):
    """Get current position and update state."""
    pass

  @abc.abstractmethod
  def reset_state(self):
    """Reset arm's state."""
    pass

  @abc.abstractmethod
  def move_to_origin(self):
    """Move to the origin position."""
    pass

  @abc.abstractmethod
  def absolute_move_to(self, x: float, y: float, z: float, *args, **kwargs):
    """Move to absolute position (x, y, z).

    Only define x, y, z argument here.
    You can implement this abstract method with more arguments.
    Args:
      x (float): x-axis coordinate. Unit: mm.
      y (float): y-axis coordinate. Unit: mm.
      z (float): z-axis coordinate. Unit: mm.
      *args: non-keyword arguments
      **kwargs: keyword arguments
    """
    pass

  @abc.abstractmethod
  def relative_move_to(self, x: float, y: float, z: float, *args, **kwargs):
    """Relative move x y, z.

    Only define x, y, z argument here.
    You can implement this abstract method with more arguments.
    Args:
      x (float): x-axis coordinate. Unit: mm.
      y (float): y-axis coordinate. Unit: mm.
      z (float): z-axis coordinate. Unit: mm.
      *args: non-keyword arguments
      **kwargs: keyword arguments
    """
    pass

  @abc.abstractmethod
  def get_state(self):
    """Return arm's current state."""

  @abc.abstractmethod
  def get_current_position(self) -> dict[str, float]:
    """Get current position."""
