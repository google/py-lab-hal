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

"""Child TempChamber Module of Testequity107."""

import time

from py_lab_hal.instrument.temp_chamber import temp_chamber


class Testequity107(temp_chamber.TempChamber):
  """Child TempChamber Class of Testequity107."""

  def enable_ramp(self, mode):
    if mode:
      self.data_handler.send(':SOURCE:CLOOP1:RACTION BOTH')
    else:
      self.data_handler.send(':SOURCE:CLOOP1:RACTION OFF')
    time.sleep(1)

  def read_actual_temp(self) -> float:
    return float(self.data_handler.query(':SOURCE:CLOOP1:PVALUE?'))

  def read_set_point(self) -> float:
    return float(self.data_handler.query(':SOURCE:CLOOP1:SPOINT?'))

  def set_ramp_rate(self, ramp_rate):
    self.data_handler.send(f':SOURCE:CLOOP1:RRATE {ramp_rate:.2f}')
    time.sleep(1)

  def set_set_point(self, temper):
    self.data_handler.send(f':SOURCE:CLOOP1:SPOINT {temper:.2f}')
    time.sleep(1)

  def run_profile(self, num_profile, run):
    self.data_handler.send(f':PROGRAM:NUMBER {num_profile}')
    time.sleep(1)
    if run:
      self.data_handler.send(':PROGRAM:SELECTED:STATE START')
    else:
      self.data_handler.send(':PROGRAM:SELECTED:STATE STOP')
    time.sleep(1)

  def delete_profile(self, num_porfile):
    pass

  def create_profile(self, name, number, step):
    pass

  def enable_power(self, mode):
    if mode:
      self.data_handler.send('OUTPUT1:STATE ON')
    else:
      self.data_handler.send('OUTPUT1:STATE OFF')
    time.sleep(1)
