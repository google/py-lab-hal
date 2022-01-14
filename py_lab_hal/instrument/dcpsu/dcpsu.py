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

"""Parent Abstract Module of DCpsu."""

import abc

from py_lab_hal.instrument import instrument


class DCpsu(instrument.Instrument, metaclass=abc.ABCMeta):
  """Parent Abstract Class of DCpsu."""

  def set_output(self, channel: int, voltage: float, current: float):
    """Configures the output voltage and current level baesd on selected channel.

    Args:
        channel (int): The specified output channel.
        voltage (float): The voltage of the config
        current (float): The current of the config
    """
    self.set_output_current(channel, current)
    self.set_output_voltage(channel, voltage)

  @abc.abstractmethod
  def set_output_voltage(self, channel: int, voltage: float):
    """Configures the output voltage level baesd on selected channel.

    Args:
        channel (int): The specified output channel
        voltage (float): The voltage of the config
    """
    pass

  @abc.abstractmethod
  def set_output_current(self, channel: int, current: float):
    """Configures the output current level baesd on selected channel.

    Args:
        channel (int): The specified output channel
        current (float): The current of the config
    """
    pass

  @abc.abstractmethod
  def enable_OCP(self, channel: int, enable: bool):
    """Enable or Disable the over current protection on the selected channel.

    If Enabled, the output will be disabled when OCP is tripped.
    If disabled, output will change to Constant Current mode.

    Args:
        channel (int): The specified output channel.
        enable (bool): If true will enable the OCP of the channel
    """
    pass

  @abc.abstractmethod
  def set_OVP_value(self, channel: int, ovp_voltage: float):
    """Sets the over-voltage protection (OVP) level on the selected channel.

    Args:
        channel (int): The specified channel.
        ovp_voltage (float): The values are programmed in volts.
    """
    pass

  @abc.abstractmethod
  def enable_OVP(self, channel: int, enable: bool):
    """Enable or Disable the over voltage protection on the selected channel.

    Args:
        channel (int): The number of the channel
        enable (bool): If true will enable the CVP of the channel
    """
    pass

  @abc.abstractmethod
  def set_sequence(
      self, channel: int, voltage: float, current: float, delay: float
  ):
    """Sets the sequence mode voltage per channel.

    Args:
        channel (int): The specified output channel.
        voltage (list of float): The list of the voltage in sequence
        current (list of float): The list of the current in sequence
        delay (list of float): The list of the time delay before voltage and
          current in sequence
    """
    pass

  @abc.abstractmethod
  def enable_output(self, channel: int, enable: bool):
    """Use enable to turn on/off the power supply output of the selected channel.

    Args:
        channel (int): The specified output channel.
        enable (bool): If true will enable the output of the channel
    """
    pass

  @abc.abstractmethod
  def set_range(self, channel: int, range_type: instrument.ChannelMode, value):
    """Sets the voltage range setting of the power supply.

    Args:
        channel (int): The specified output channel.
        range_type (TYPE): Description
        value (TYPE): Description
    """
    pass

  @abc.abstractmethod
  def enable_remote_sense(self, enable: bool):
    """Selects whether or not to enable 4wire remote sense on the power supply.

    Args:
        enable (bool): If true will enable the remote sense
    """
    pass

  @abc.abstractmethod
  def set_NPLC(self, channel: int, power_line_freq: int, nplc: float):
    """Sets the nplc (Number of Power Line Cycles) based on power_line_freq (60/50 Hz).

    Increasing NPLC will increase measurement time, but increase accuracy.
    Decreasing NPLC will decrease measurement time, but increase noise.
    This only affects the measurement/sensing capabilities of the DCPSU.

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

  def measure_power(self, channel: int) -> float:
    """Measure the power on output channel.

    Args:
        channel (int): The specified output channel.

    Returns:
        (float): the measure result
    """
    return self.measure_current(channel) * self.measure_voltage(channel)
