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

"""Child Spectroradiometer Module of Konica CS-3000."""

import re
import time
from py_lab_hal.instrument.spectro_radio_meter import spectro_radio_meter


class KonicaCs3000(spectro_radio_meter.SpectroRadioMeter):
  """Child Spectroradiometer Class of Konica CS-3000."""

  def open_interface(self):
    super().open_interface()
    return self.data_handler.query('RMTS,01')

  def get_last_tristim(self):
    return self.data_handler.query('MEDR,2,0,1')

  def get_last_uv(self):
    return self.data_handler.query('MEDR,2,0,3')

  def get_last_xy(self):
    return self.data_handler.query('MEDR,2,0,2')

  def get_last_spectrum(self):
    return self.data_handler.query('STDR,0,1,0')

  def get_last_colortemp(self):
    return self.data_handler.query('MEDR,2,0,4')

  def get_light_frequency(self):
    return self.data_handler.query('MLSF')

  def measure(self):
    ret_msg = self.data_handler.query('MEAS,1')
    match = re.search(r'(?<=,)\d+', ret_msg)
    if not match:
      raise RuntimeError('Can not get the estimate measurement time.')
    time.sleep(int(match.group(0)))
    return self.data_handler.recv()
