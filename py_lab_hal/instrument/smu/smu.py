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

"""Parent Abstract Module of Smu."""

import abc

from py_lab_hal.instrument import instrument


class Smu(instrument.Instrument, metaclass=abc.ABCMeta):
  """Parent Abstract Class of Smu."""

  @abc.abstractmethod
  def enable_output(self, channel: int, enable: bool):
    """Enables or disables the specified output channel.

    Args:
        channel (int): The specified output channel.
        enable (bool): The enabled state is ON (True); the disabled state is OFF
          (False).
    """
    pass

  @abc.abstractmethod
  def enable_remote_sense(self, channel: int, enable: bool):
    pass

  @abc.abstractmethod
  def enable_OCP(self, channel: int, enable: bool):
    """Enables or disables the over-current protection (OCP) function on the selected channel.

    If Enabled, the output will be disabled when OCP is tripped.
    If disabled, output will change to Constant Current mode.

    Args:
        channel (int): The number of the channel
        enable (bool): If true will enable the OCP of the channel
    """
    pass

  @abc.abstractmethod
  def set_OVP_value(self, channel: int, ovp_voltage: float):
    """Sets the selected channel over voltage protection level set by voltage.

    Args:
        channel (int): The number of the channel
        ovp_voltage (float): The voltage of the ovp config
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
  def set_range(self, channel: int, range_type, max_value):
    pass

  @abc.abstractmethod
  def measure_current(self, channel: int) -> float:
    """This query initiates and triggers a measurement.

    Args:
        channel (int): The specified channel.

    Returns:
        float: the average output current in amperes.T
    """
    pass

  @abc.abstractmethod
  def measure_voltage(self, channel: int) -> float:
    """This query initiates and triggers a measurement.

    Args:
        channel (int): The specified channel.

    Returns:
        float: The averageoutput voltage in volts.
    """
    pass

  @abc.abstractmethod
  def measure_power(self, channel: int) -> float:
    """This query initiates and triggers a measurement.

    Args:
        channel (int): The specified channel.

    Returns:
        float: The average output power in watts.
    """
    pass
