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

"""Child TempChamber Module of Pu3j."""

from py_lab_hal.instrument.temp_chamber import temp_chamber


class Pu3j(temp_chamber.TempChamber):
  """Child TempChamber Class of Pu3j."""

  def enable_ramp(self, mode):
    pass

  def read_actual_temp(self) -> float:
    return float(self.data_handler.query('TEMP?').split(', ')[0])

  def read_set_point(self) -> float:
    return float(self.data_handler.query('TEMP?').split(', ')[1])

  def set_ramp_rate(self, ramp_rate):
    pass

  def set_set_point(self, temper):
    self.data_handler.send(f'TEMP, S{temper:.2f}')

  def run_profile(self, num_profile, run):
    pass

  def delete_profile(self, num_porfile):
    pass

  def create_profile(self, name, number, step):
    pass

  def enable_power(self, mode):
    if mode:
      self.data_handler.send('POWER, ON')
    else:
      self.data_handler.send('POWER, OFF')
