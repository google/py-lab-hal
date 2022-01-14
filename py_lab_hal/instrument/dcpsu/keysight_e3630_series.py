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

"""Child DCpsu Module of KeysightE3630Series."""

from py_lab_hal.instrument.dcpsu import dcpsu


class KeysightE3630Series(dcpsu.DCpsu):
  """Child DCpsu Class of KeysightE3630Series."""

  def open_interface(self):
    super().open_interface()
    self.data_handler.send('SYSTem:REMote')

  def enable_OCP(self, channel, enable):
    self.data_handler.send(f'voltage:protection:state {int(enable)}')

  def set_OCP_value(self, channel, ocp_current) -> None:
    self.data_handler.send(f'current:protection {ocp_current}')

  def enable_OVP(self, channel, enable):
    self.data_handler.send(f'voltage:protection:state {int(enable)}')

  def set_OVP_value(self, channel, ovp_voltage) -> None:
    self.data_handler.send(f'voltage:protection {ovp_voltage}')

  def set_sequence(self, channel, voltage, current, delay):
    pass

  def set_range(self, channel, range_type, value):
    pass

  def enable_remote_sense(self, enable):
    pass

  def set_NPLC(self, channel, power_line_freq, nplc):
    pass

  def measure_current(self, channel) -> float:
    self.data_handler.send('measure:current?')
    return float(self.data_handler.recv())

  def measure_voltage(self, channel) -> float:
    self.data_handler.send('measure:voltage?')
    return float(self.data_handler.recv())

  def enable_output(self, channel, enable) -> None:
    if enable:
      self.data_handler.send('OUTP ON')
    else:
      self.data_handler.send('OUTP OFF')

  def set_output_voltage(self, channel, voltage):
    self.data_handler.send(f'VOLT {voltage}')

  def set_output_current(self, channel, current):
    self.data_handler.send(f'CURR {current}')
