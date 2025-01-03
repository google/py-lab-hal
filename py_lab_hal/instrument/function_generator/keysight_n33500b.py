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

"""Child FunctionGenerator Module of Keysightn33500b."""

from py_lab_hal.instrument import instrument
from py_lab_hal.instrument.function_generator import function_generator


class KeysightN33500b(function_generator.FunctionGenerator):
  """Child FunctionGenerator Class of Keysightn33500b."""

  def configure_trigger_output(self, channel, trigger, enable):
    pass

  def configure_trigger(self, channel, delay, timer, trigger_source, slope):
    pass

  def configure_output(
      self, channel, function, frequency, amplitude, offset, phase
  ):
    self.data_handler.send(
        f'SOUR{channel}:APPL:{function.value} {frequency},{amplitude},{offset}'
    )
    if function != instrument.FunctionType.DC:
      self.set_output_phase(channel, phase)

  def enable_output(self, channel, enable):
    self.data_handler.send(f'OUTP{channel} {int(enable)}')

  def set_STD_waveform(
      self, channel, waveform, freq, amp, dc_offset, duty_cycle
  ):
    pass

  def set_output_function(self, channel, function):
    self.data_handler.send(f'SOUR{channel}:FUNCtion {function.value}')

  def set_output_voltage(self, channel, amplitude, offset):
    self.data_handler.send(f'SOUR{channel}:VOLTage {amplitude}')
    self.data_handler.send(f'SOUR{channel}:VOLTage:OFFSet {offset}')

  def set_output_frequency(self, channel, frequency):
    self.data_handler.send(f'SOUR{channel}:FREQuency {frequency}')

  def set_output_phase(self, channel, degree):
    self.data_handler.send(f'SOUR{channel}:PHASe {degree}')

  def set_output_impedance(self, channel, impedance):
    self.data_handler.send(f'SOUR{channel}:LOAD {impedance}')

  def set_output_duty_cycle(self, channel, function, percent):
    self.data_handler.send(f'SOUR{channel}:FUNCtion:{function.value} {percent}')
