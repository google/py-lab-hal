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

"""Child Spectroradiometer Class of JadakPr670."""

from py_lab_hal.datagram import datagram
from py_lab_hal.instrument.spectro_radio_meter import spectro_radio_meter


class JadakPr670(spectro_radio_meter.SpectroRadioMeter):
  """Child Spectroradiometer Class of JadakPr670."""

  def _build_bytes_datagram(
      self, data: bytes = b'', size: int = -1
  ) -> datagram.OneByOneBytesDatagram:
    return datagram.OneByOneBytesDatagram(
        self.inst.connect_config.terminator.read.encode(),
        self.inst.connect_config.terminator.write.encode(),
        data,
        size,
    )

  def _send_command(self, command: bytes):
    self.data_handler.send_dataram(self._build_bytes_datagram(command))

  def open_interface(self):
    super().open_interface()
    self._send_command(b'PHOTO')
    self.data_handler.recv()

  def get_last_tristim(self):
    self._send_command(b'D2')
    return self.data_handler.recv()

  def get_last_uv(self):
    self._send_command(b'D3')
    return self.data_handler.recv()

  def get_last_xy(self):
    self._send_command(b'D1')
    return self.data_handler.recv()

  def get_last_spectrum(self):
    self._send_command(b'D5')
    return self.data_handler.recv()

  def get_last_colortemp(self):
    self._send_command(b'D4')
    return self.data_handler.recv()

  def measure(self):
    self._send_command(b'M0')

  def get_light_frequency(self):
    self._send_command(b'F')
    return self.data_handler.recv()
