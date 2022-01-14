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

"""Child DCpsu Module of GwinPst3202."""

import logging
import time

from py_lab_hal.instrument.dcpsu import dcpsu


class GwinPst3202(dcpsu.DCpsu):
  """Child DCpsu Class of GwinPst3202."""

  def enable_OCP(self, channel, enable):
    self.data_handler.send(f'CHAN{channel}:PROTection:CURRent {int(enable)}')

  def enable_OVP(self, channel: int, enable: bool):
    logging.warning('The OVP is auto enable after set OVP value.')

  def set_OVP_value(self, channel, ovp_voltage):
    self.data_handler.send(
        f'CHAN{channel}:PROTection:VOLTage {ovp_voltage:.2f}'
    )
    logging.warning('The OVP is auto enable after set OVP value.')

  def set_sequence(self, channel, voltage, current, delay):
    if len(voltage) != len(current):
      logging.error('len error')
      raise RuntimeError
    if len(voltage) != len(delay):
      logging.error('delay len error')
      raise RuntimeError

    for v, c, t in zip(voltage, current, delay):
      time.sleep(t)
      self.set_output(channel, v, c)

  def set_range(self, channel, range_type, value):
    pass

  def enable_remote_sense(self, enable):
    pass

  def set_NPLC(self, channel, power_line_freq, nplc):
    pass

  def measure_current(self, channel) -> float:
    return float(self.data_handler.query(f'CHAN{channel}:MEAS:CURR?'))

  def measure_voltage(self, channel) -> float:
    return float(self.data_handler.query(f'CHAN{channel}:MEAS:VOLT?'))

  def enable_output(self, channel, enable):
    self.data_handler.send(f'OUTP:STATE {int(enable)}')

  def set_output_voltage(self, channel, voltage):
    self.data_handler.send(f'CHAN{channel}:VOLT {voltage:.2f}')

  def set_output_current(self, channel, current):
    self.data_handler.send(f'CHAN{channel}:CURR {current:.2f}')
