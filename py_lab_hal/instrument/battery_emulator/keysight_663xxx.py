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

"""Child BatteryEmulator Module of Keysight66300Series."""

from py_lab_hal.instrument.battery_emulator import battery_emulator


class Keysight66300Series(battery_emulator.BatteryEmulator):
  """Child BatteryEmulator Class of Keysight66300Series."""

  def enable_output(self, channel, enable):
    self.data_handler.send(f'OUTP{channel} {int(enable)}')

  def enable_remote_sense(self, channel, enable):
    if enable:
      self.data_handler.send('OUTP:COMP:MODE HREMOTE')
    else:
      self.data_handler.send('OUTP:COMP:MODE HLOCAL')

  def enable_OCP(self, channel, enable):
    self.data_handler.send(f'CURR:PROT:STAT {int(enable)}')

  def set_output_voltage(self, channel, voltage):
    self.data_handler.send(f'VOLT{channel} {voltage}')

  def set_output_current(self, channel, current):
    self.data_handler.send(f'CURR{channel} {current}')

  def set_OVP_value(self, channel, ovp_voltage):
    self.data_handler.send(f'VOLT:PROT {ovp_voltage}')

  def enable_OVP(self, channel: int, enable: bool):
    self.data_handler.send(f'VOLT:PROT:STAT {int(enable)}')

  def set_range(self, channel, range_type, max_value):
    pass

  def measure_current(self, channel) -> float:
    self.data_handler.send(f'MEAS:SCAL:CURR{channel}?')
    return float(self.data_handler.recv())

  def measure_voltage(self, channel) -> float:
    self.data_handler.send(f'MEAS:SCAL:VOLT{channel}?')
    return float(self.data_handler.recv())

  def measure_power(self, channel) -> float:
    v = self.measure_voltage(channel)
    i = self.measure_current(channel)
    return i * v
