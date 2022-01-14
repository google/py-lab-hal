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

"""Child eload Module of Keysight N6705C Chassis Eloads Series."""

from __future__ import annotations

from py_lab_hal.cominterface import cominterface
from py_lab_hal.instrument import instrument
from py_lab_hal.instrument.common.keysight import keysight_n6705c
from py_lab_hal.instrument.eload import eload


class KeysightN6705c(keysight_n6705c.KeysightN6705c, eload.Eload):
  """Child eload Class of Keysight N6705C."""

  def __init__(
      self,
      com: cominterface.ComInterfaceClass,
      inst_config: instrument.InstrumentConfig,
  ) -> None:
    keysight_n6705c.KeysightN6705c.__init__(self, com, inst_config)

  def set_current_dynamic(
      self, channel: int, l1, t1, rise_rate, l2, t2, fall_rate, repeat
  ):
    raise NotImplementedError(
        'This function is not currently implemented in the N6705C'
    )

  def set_mode(self, channel, mode):
    self.set_priority(channel, mode)

  def set_level(self, channel, mode, value, curr_lim=None):
    super().set_level(channel, mode, value)
    if curr_lim:
      self.set_output_current(channel, curr_lim)

  def set_sequence(self, channel, voltage, current, delay):
    raise NotImplementedError(
        'This function is not currently implemented in the N6705C'
    )

  def set_NPLC(self, channel, power_line_freq, nplc):
    # 50Hz = 3906pts, 60Hz = 3255pts per manual
    # default to 60Hz
    pts = 3255
    if power_line_freq == 50:
      pts = 3906
    self.data_handler.send(f'SENSe:SWEep:POINts {pts * nplc},(@{channel}')
