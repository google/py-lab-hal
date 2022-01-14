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

"""Parent Abstract Module of stepper_motor."""

import abc

from py_lab_hal.instrument import instrument


class StepperMotor(instrument.Instrument, metaclass=abc.ABCMeta):
  """Parent Abstract Class of StepperMotor."""

  @abc.abstractmethod
  def home(self, channel: int) -> None:
    """Move motor back to home.

    Args:
        channel (int): The number of the channel
    """
    pass

  @abc.abstractmethod
  def stop(self, channel: int, stop_mode: str) -> None:
    """Stop the motor.

    Args:
        channel (int): The number of the channel
        stop_mode (str): Stop immediately(IMM), or by controller(CON)
    """
    pass

  @abc.abstractmethod
  def set_vel(self, acceleration: float, max_velocity: float) -> None:
    """Set the velocity parameters.

    Args:
        acceleration (float): The accelerate value from 0 to max_velocity in
          deg/s^2
        max_velocity (float): The max velocity in deg/s
    """
    pass

  @abc.abstractmethod
  def set_move_abs(self, channel: int, absolute_position: float) -> None:
    """Set the absolute move parameters.

    Args:
        channel (int): The number of the channel
        absolute_position (int): The position in deg
    """
    pass

  @abc.abstractmethod
  def move_absolute(self, channel: int) -> None:
    """Move absolute base on the set_move_abs.

    Args:
        channel (int): The number of the channel
    """
    pass

  @abc.abstractmethod
  def set_jog(
      self,
      channel: int,
      jog_mode: str,
      step_size: float,
      acceleration: float,
      max_velocity: float,
      stop_mode: str,
  ) -> None:
    """Set the velocity parameters.

    Args:
        channel (int): The number of the channel
        jog_mode (str): Continuous(CON) jogging or single-step(SIN) jogging
        step_size (float): The jog step size in deg.
        acceleration (float): The accelerate value from 0 to max_velocity in
          deg/s^2
        max_velocity (float): The max velocity in deg/s
        stop_mode (str): Stop immediately(IMM), or by controller(CON)
    """
    pass

  @abc.abstractmethod
  def move_jog(self, channel: int, direction: str) -> None:
    """Move jog base on the set_jog.

    Args:
        channel (int): The number of the channel
        direction (str): Jog forward(FOR), reverse(REV) direction.
    """
    pass
