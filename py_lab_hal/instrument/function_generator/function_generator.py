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

"""Parent Abstract Module of FunctionGenerator."""

import abc

from py_lab_hal.instrument import instrument


class FunctionGenerator(instrument.Instrument, metaclass=abc.ABCMeta):
  """Parent Abstract Class of FunctionGenerator."""

  @abc.abstractmethod
  def configure_trigger_output(self, channel: int, trigger, enable: bool):
    """Configures the Output signal Sync out with Channel and Selected which Type of Trigger Slpoe.

    Args:
      channel (int): The specified output channel.
      trigger (str):
      enable (bool):
    """
    pass

  @abc.abstractmethod
  def configure_trigger(
      self, channel: int, delay, timer, trigger_source, slope
  ):
    """Configures the trigger source.

    Count, delay and slop for triggering arbitrary sequence,
    sweep, list, or burst.

    Args:
        channel (int): The specified output channel.
      delay (float):
      timer (float):
      trigger_source (int):
      slope (str):
    """
    pass

  @abc.abstractmethod
  def enable_output(self, channel: int, enable: bool):
    """Configure enable for specified channel.

    Args:
        channel (int): The specified output channel.
        enable (bool):
    """
    pass

  def configure_duty_cycle(
      self,
      channel: int,
      function,
      frequency: float,
      amplitude: float,
      offset: float,
      duty_cycle: float,
  ):
    """configure function with duty cycle parameters.

    Args:
        channel (int): The specified output channel.
        function (TYPE):
        frequency (float):
        amplitude (float):
        offset (float):
        duty_cycle (float):
    """
    self.set_output_function(channel, function)
    self.set_output_frequency(channel, frequency)
    self.set_output_voltage(channel, amplitude, offset)
    self.set_output_duty_cycle(channel, function, duty_cycle)

  @abc.abstractmethod
  def set_STD_waveform(
      self,
      channel: int,
      function,
      frequency: float,
      amplitude: float,
      offset: float,
      duty_cycle: float,
  ):
    """Summary.

    Args:
        channel (int): The specified output channel.
        function (TYPE):
        frequency (float):
        amplitude (float):
        offset (float):
        duty_cycle (float):
    """
    pass

  @abc.abstractmethod
  def configure_output(
      self,
      channel: int,
      function: instrument.FunctionType,
      frequency: float,
      amplitude: float,
      offset: float,
      phase: float,
  ):
    pass

  @abc.abstractmethod
  def set_output_function(self, channel, function: instrument.FunctionType):
    pass

  @abc.abstractmethod
  def set_output_voltage(self, channel: int, amplitude: float, offset: float):
    pass

  @abc.abstractmethod
  def set_output_frequency(self, channel: int, frequency: float):
    pass

  @abc.abstractmethod
  def set_output_phase(self, channel: int, degree: float):
    pass

  @abc.abstractmethod
  def set_output_impedance(self, channel: int, impedance: float):
    pass

  @abc.abstractmethod
  def set_output_duty_cycle(
      self,
      channel: int,
      function,
      percent: float,
  ):
    pass
