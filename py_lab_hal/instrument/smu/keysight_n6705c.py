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

"""Child Smu Module of Keysightn6705c."""

from py_lab_hal.cominterface import cominterface
from py_lab_hal.instrument import instrument
from py_lab_hal.instrument.common.keysight import keysight_n6705c
from py_lab_hal.instrument.smu import smu

RESISTANCE_MODE = [
    instrument.ChannelMode.RESISTANCE,
    instrument.ChannelMode.RESISTANCE_4WIRE,
]


class KeysightN6705c(keysight_n6705c.KeysightN6705c, smu.Smu):
  """Child Smu Class of Keysightn6705c."""

  def __init__(
      self,
      com: cominterface.ComInterfaceClass,
      inst_config: instrument.InstrumentConfig,
  ) -> None:
    keysight_n6705c.KeysightN6705c.__init__(self, com, inst_config)

  def open_instrument(self):
    super().open_instrument()
    super().select_mode(
        self.inst_config.channel, instrument.SmuEmulationMode.PS2Q
    )

  def set_range(self, channel, range_type, max_value):
    if range_type in RESISTANCE_MODE:
      raise NotImplementedError(
          'This function is not currently implemented in the N6705C eload'
      )
    return super().set_range(channel, range_type, max_value)
