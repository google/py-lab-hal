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

"""Parent Abstract Module of Eload."""

from __future__ import annotations

import abc

from py_lab_hal.instrument import instrument


class Eload(instrument.Instrument, metaclass=abc.ABCMeta):
  """Parent Abstract Class of Eload."""

  @abc.abstractmethod
  def short_output(self, channel: int, enable: bool) -> None:
    """Shorts the Eload Channel.

    Note: This action occurs IMMEDIATELY when called!

    Args:
      channel (int): The specified output channel.
      enable (bool): To enable or disable the channel short
    """
    pass

  @abc.abstractmethod
  def set_slewrate(
      self, channel: int, edge: instrument.EdgeTriggerSlope, rate: float
  ) -> None:
    """Sets the slewrate in A/us for the assigned channel.

    Args:
      channel (int): The channel to set the slewrate
      edge: Rising or Falling edge to set the slewrate
      rate: The slewrate in A/us
    """
    pass

  @abc.abstractmethod
  def set_current_dynamic(
      self, channel: int, l1, t1, rise_rate, l2, t2, fall_rate, repeat
  ) -> None:
    pass

  @abc.abstractmethod
  def enable_output(self, channel: int, enable: bool) -> None:
    """Enable the channel output.

    Args:
        channel (int): The specified output channel.
        enable (bool): If true will enable the output of the channel
    """
    pass

  @abc.abstractmethod
  def set_mode(self, channel: int, mode: instrument.ChannelMode) -> None:
    """Sets the operation mode for the selected channel number.

    Select from the following operation modes: CC, CR, CP, or CV
    Note that not all modes are support by the ELoads! Check your model!

    Args:
      channel (int): The target channel
      mode (ChannelMode): The operation mode to set
    """
    pass

  @abc.abstractmethod
  def set_level(
      self,
      channel: int,
      mode: instrument.ChannelMode,
      value: float,
      curr_lim: float | None = None,
  ) -> None:
    """Sets the operation level of the selected channel.

    Units are:
      current, A
      voltage, V
      power, W
      resistance, ohm

    Args:
        channel (int): The specified output channel.
      mode (ChannelMode): The operation mode to set the level
      value (float): The operating level
      curr_lim (float): The optional current limit to set when op_mode = cv
    """
    pass

  @abc.abstractmethod
  def set_sequence(
      self,
      channel: int,
      voltage: list[float],
      current: list[float],
      delay: list[float],
  ) -> None:
    pass

  @abc.abstractmethod
  def set_range(
      self, channel: int, range_type: instrument.ChannelMode, value: float
  ) -> None:
    """Auto sets the operation range setting of the eload.

    Args:
        channel (int): The specified output channel.
        range_type (ChannelMode): The operation mode
        value (float): Expected max operation value in float
    """
    pass

  @abc.abstractmethod
  def set_NPLC(self, channel: int, power_line_freq: int, nplc: float) -> None:
    """Sets the nplc (Number of Power Line Cycles) based on power_line_freq.

    Increasing NPLC will increase measurement time, but increase accuracy.
    Decreasing NPLC will decrease measurement time, but increase noise.
    This only affects the measurement/sensing capabilities of the Eload.

    Args:
        channel (int): The specified output channel.
        power_line_freq (int): The power line freq
        nplc (float): The number of power line cycles
    """
    pass

  @abc.abstractmethod
  def measure_current(self, channel: int) -> float:
    """Measure the current on output channel.

    Args:
        channel (int): The specified output channel.

    Returns:
        (float): the measure result
    """
    pass

  @abc.abstractmethod
  def measure_voltage(self, channel: int) -> float:
    """Measure the voltage on output channel.

    Args:
        channel (int): The specified output channel.

    Returns:
        (float): the measure result
    """
    pass
