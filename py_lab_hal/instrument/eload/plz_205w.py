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

"""Child eload Module of PLZ205W PLZ405W PLZ1205W."""

from __future__ import annotations

import logging
import re

from py_lab_hal.cominterface import cominterface
from py_lab_hal.instrument import instrument
from py_lab_hal.instrument.eload import eload
from py_lab_hal.util import util


CHANNEL_MODE = {
    instrument.ChannelMode.CURRENT_DC: 'cc',
    instrument.ChannelMode.VOLTAGE_DC: 'cv',
    instrument.ChannelMode.RESISTANCE: 'cr',
    instrument.ChannelMode.POWER: 'cp',
}


class MatchError(ValueError):
  pass


class Plz205w(eload.Eload):
  """Child eload Class of PLZ205w."""


class Bk8500b(eload.Eload):
  """Child eload Class of Bk8500b."""

  mode_cmd = {
      instrument.ChannelMode.CURRENT_DC: 'CURRent',
      instrument.ChannelMode.VOLTAGE_DC: 'VOLTage',
      instrument.ChannelMode.RESISTANCE: 'CONDuctance',
      instrument.ChannelMode.POWER: 'POWer',
  }
  mode_range = {
      'PLZ205W': {
          instrument.ChannelMode.CURRENT_DC: [0.42, 4.2, 42.0],
          instrument.ChannelMode.VOLTAGE_DC: [15.75, 15.75, 157.5],
          instrument.ChannelMode.RESISTANCE: [1 / 42, 1 / 4.2, 1 / 0.42],
          instrument.ChannelMode.POWER: [2.1, 21.0, 210.0],
      },
      'PLZ405W': {
          instrument.ChannelMode.CURRENT_DC: [0.84, 8.4, 84.0],
          instrument.ChannelMode.VOLTAGE_DC: [15.75, 15.75, 157.5],
          instrument.ChannelMode.RESISTANCE: [1 / 84.0, 1 / 8.4, 1 / 0.84],
          instrument.ChannelMode.POWER: [4.2, 42.0, 420.0],
      },
      'PLZ1205W': {
          instrument.ChannelMode.CURRENT_DC: [2.52, 25.2, 252.0],
          instrument.ChannelMode.VOLTAGE_DC: [15.75, 15.75, 157.5],
          instrument.ChannelMode.RESISTANCE: [1 / 252.0, 1 / 25.2, 1 / 2.52],
          instrument.ChannelMode.POWER: [12.6, 126.0, 1260.0],
      },
  }

  def __init__(
      self,
      com: cominterface.ComInterfaceClass,
      inst_config: instrument.InstrumentConfig,
  ) -> None:
    super().__init__(com, inst_config)

    result = re.search(r'(?P<model>PLZ.+W)', self.idn)
    if not result:
      raise RuntimeError
    self.device_name = result['model']

  def short_output(self, channel, enable) -> None:
    self.data_handler.send(f'INPut:SHORt {int(enable)}')
    self.enable_output(channel, enable)

  def set_slewrate(self, channel, edge, rate) -> None:
    logging.warning('PLZ series does not have individual edge controls')
    self.data_handler.send(f'CURRent:SLEW {rate}')

  def set_current_dynamic(
      self, channel, l1, t1, rise_rate, l2, t2, fall_rate, repeat
  ) -> None:
    raise NotImplementedError(
        'This function is not currently implemented in the PLZ205W'
    )

  def enable_output(self, channel, enable) -> None:
    self.data_handler.send(f'INPut {int(enable)}')

  def set_mode(self, channel, mode) -> None:
    mode = util.get_from_dict(CHANNEL_MODE, mode)
    self.data_handler.send(f'FUNCtion {mode}')

  def set_level(self, channel, mode, value, curr_lim=None) -> None:

    if mode == instrument.ChannelMode.RESISTANCE:
      if value == 0:
        raise RuntimeError('Can not set resistance to zero')
      value = 1 / value
    self.data_handler.send(f'{self.mode_cmd[mode]} {value}')

  def set_sequence(self, channel, voltage, current, delay) -> None:
    raise NotImplementedError(
        'This function is not currently implemented in the PLZ205W'
    )

  def set_range(self, channel, range_type, value) -> None:
    def get_range():
      value_range = self.mode_range[self.device_name][range_type]

      if value > value_range[2]:
        raise RuntimeError
      if value > value_range[1]:
        return 'HIGH'
      if value > value_range[0]:
        return 'MEDium'
      if value > 0:
        return 'LOW'

      raise RuntimeError

    self.data_handler.send(f'{self.mode_cmd[range_type]}:RANGe {get_range()}')

  def set_NPLC(self, channel, power_line_freq, nplc) -> None:
    raise NotImplementedError(
        'This function is not currently implemented in the PLZ205W'
    )

  def measure_current(self, channel) -> float:
    return float(self.data_handler.query('MEASure:CURRent?'))

  def measure_voltage(self, channel) -> float:
    return float(self.data_handler.query('MEASure:VOLTage?'))
