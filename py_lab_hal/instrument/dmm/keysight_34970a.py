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

"""Child DMM Module of Keysight34970a."""

from py_lab_hal.instrument.common.keysight import keysight_dmm
from py_lab_hal.util import util


class Keysight34970a(keysight_dmm.KeysightDMM):
  """Child DMM Class of Keysight34970a."""

  def read(self, channel=0, timeout=0):
    self.data_handler.send(f'ROUT:SCAN (@{channel})')
    self.data_handler.send('read?')
    return float(self.data_handler.recv())

  def _sense_command(self, channel, config_type, value):
    channel_mode = self._get_channel_mode(channel)
    self.data_handler.send(f'{channel_mode}:{config_type} {value},(@{channel})')

  def _config_channel_mode(self, channel, mode):
    channel_mode = util.get_from_dict(keysight_dmm.CHANNEL_MODE, mode)
    self.data_handler.send(f'CONF:{channel_mode},(@{channel})')
