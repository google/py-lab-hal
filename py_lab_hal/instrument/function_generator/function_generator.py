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
  def configure_trigger(self, channel, delay, timer, trigger_source, slope):
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
  def enable_output(
      self, channel, output_impedance, voltage_limit, enable: bool
  ):
    """Configure output impedance, voltage limitation, and enable for specified channel.

    Args:
        channel (int): The specified output channel.
        output_impedance (float):
        voltage_limit (float):
        enable (bool):
    """
    pass

  @abc.abstractmethod
  def set_duty_cycle(self, channel, waveform, freq, amp, dc_offset, duty_cycle):
    """Sets duty cycle parameters for square waveform.

    Args:
        channel (int): The specified output channel.
        waveform (TYPE):
        freq (float):
        amp (float):
        dc_offset (float):
        duty_cycle (float):
    """
    pass

  @abc.abstractmethod
  def set_STD_waveform(
      self, channel, waveform, freq, amp, dc_offset, duty_cycle
  ):
    """Summary.

    Args:
        channel (int): The specified output channel.
        waveform (TYPE):
        freq (float):
        amp (float):
        dc_offset (float):
        duty_cycle (float):
    """
    pass

  @abc.abstractmethod
  def configure_output(
      self, channel, function, frequency, amplitude, offset, phase
  ):
    pass
