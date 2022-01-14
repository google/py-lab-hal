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

"""Child TempChamber Module of Giant."""

from py_lab_hal.instrument.temp_chamber import temp_chamber


class Giant(temp_chamber.TempChamber):
  """Child TempChamber Class of Giant."""

  def enable_ramp(self, mode):
    pass

  def read_actual_temp(self) -> float:
    return float(self.data_handler.query('TEMP?').split(', ')[0])

  def read_set_point(self) -> float:
    return float(self.data_handler.query('TEMP?').split(', ')[1])

  def set_ramp_rate(self, ramp_rate):
    pass

  def set_set_point(self, temper):
    pass

  def read(self):
    mesg = bytes.fromhex(f'{0:02X}3135')
    self.data_handler.send_raw(self._fsc(mesg))
    return self.data_handler.recv()

  def set_all(self, temper, rh, temp_r, rh_r):
    mesg = bytes.fromhex(f'{0:02X}3135')
    mesg += f'{temper*100:04X}'.encode('utf-8')
    mesg += f'{rh*100:04X}'.encode('utf-8')
    mesg += f'{temp_r*100:04X}'.encode('utf-8')
    mesg += f'{rh_r*100:04X}'.encode('utf-8')
    mesg += f'{999959:06X}'.encode('utf-8')
    mesg += f'{0:01X}'.encode('utf-8')
    mesg += f'{1:01X}'.encode('utf-8')
    mesg += f'{1:03X}'.encode('utf-8')
    self.data_handler.send_raw(self._fsc(mesg))

  def run_profile(self, num_profile, run):
    pass

  def delete_profile(self, num_porfile):
    pass

  def create_profile(self, name, number, step):
    pass

  def enable_power(self, mode):
    if mode:
      mesg = bytes.fromhex(f'{0:02X}3533011')
      self.data_handler.send_raw(self._fsc(mesg))
    else:
      mesg = bytes.fromhex(f'{0:02X}3533021')
      self.data_handler.send_raw(self._fsc(mesg))

  def _fsc(self, data_in):
    ans = 64
    for byte in data_in:
      ans = ans ^ byte
    print(ans)
    ans = f'{ans:02X}'.encode('utf-8').hex()
    return bytes.fromhex(f'40{data_in.hex()}{ans}2A0D')
