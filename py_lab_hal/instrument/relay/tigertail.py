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

"""Child Relay Module of Tigertail."""

import logging
from typing import Literal

from py_lab_hal.cominterface import cominterface
from py_lab_hal.instrument import instrument
from py_lab_hal.instrument.relay import relay


class Tigertail(relay.Relay):
  """Child relay Class of Tigertail."""

  def __init__(
      self,
      com: cominterface.ComInterfaceClass,
      inst_config: instrument.InstrumentConfig,
  ) -> None:
    super().__init__(com, inst_config)
    self._channel_status = 0

  def enable(self, channel, enable) -> None:
    if enable:
      if channel == 0:
        logging.warning('Can not enable the channel 0 on Tigertail')
      else:
        self._channel_on(channel)

    else:
      if channel == self._channel_status or channel == 0:
        self.reset()

  def reset(self) -> None:
    self.data_handler.send('mux off')
    self._channel_status = 0

  def _channel_on(self, channel: Literal[1, 2]) -> None:
    channel_mapping = {
        1: 'A',
        2: 'B',
    }
    self.data_handler.send(f'mux {channel_mapping[channel]}')
    self._channel_status = channel
