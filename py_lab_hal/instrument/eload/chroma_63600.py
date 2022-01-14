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

"""Child eload Module of Chroma63600.

The Chroma 63600 Programmable DC Electronic Load System consists of model
63600-1,
63600-2,
63600-5,
63601-5 mainframes, and
63630-80-60,
63610-80-20,
63640-80-80,
63630-600-15 and
63640-150-60 Electronic Load modules.
"""

from __future__ import annotations

import dataclasses
import re

from py_lab_hal.cominterface import cominterface
from py_lab_hal.instrument import instrument
from py_lab_hal.instrument.eload import eload
from py_lab_hal.util import util


class MatchError(ValueError):
  pass


CHANNEL_MODE = {
    instrument.ChannelMode.CURRENT_DC: 'CCH',
    instrument.ChannelMode.VOLTAGE_DC: 'CVH',
    instrument.ChannelMode.RESISTANCE: 'CRH',
    instrument.ChannelMode.POWER: 'CPH',
}

EDGE_SLOPE = {
    instrument.EdgeTriggerSlope.RISE: 'rise',
    instrument.EdgeTriggerSlope.FALL: 'fall',
}


class Chroma63600(eload.Eload):
  """Child eload Class of Chroma63600."""

  @dataclasses.dataclass
  class ModelRange:
    # Make floats for now, unsure if future models will have floating pt ranges
    cc: list[float]
    cv: list[float]
    cr: list[float]
    cp: list[float]

  model_63610_80_20 = ModelRange(
      cc=[0.2, 2, 20], cv=[6, 16, 80], cr=[80, 2900, 12000], cp=[2, 10, 100]
  )

  model_63630_80_60 = ModelRange(
      cc=[0.6, 6, 60], cv=[6, 16, 80], cr=[30, 600, 3000], cp=[6, 30, 300]
  )

  model_63630_600_15 = ModelRange(
      cc=[0.15, 1.5, 15],
      cv=[80, 150, 600],
      cr=[270, 4000, 200000],
      cp=[6, 30, 300],
  )

  model_63640_80_80 = ModelRange(
      cc=[0.8, 8, 80], cv=[6, 16, 80], cr=[20, 720, 2900], cp=[8, 40, 400]
  )

  model_63640_150_60 = ModelRange(
      cc=[1, 6, 60], cv=[16, 80, 150], cr=[60, 800, 1500], cp=[8, 40, 400]
  )

  RANGE = {
      '63610-80-20': model_63610_80_20,
      '63630-80-60': model_63630_80_60,
      '63630-600-15': model_63630_600_15,
      '63640-80-80': model_63640_80_80,
      '63640-150-60': model_63640_150_60,
  }

  def __init__(
      self,
      com: cominterface.ComInterfaceClass,
      inst_config: instrument.InstrumentConfig,
  ) -> None:
    self.ch_ids: dict[int, str] = {}
    super().__init__(com, inst_config)
    # Too many op modes in Chroma, will set default to high range
    # The set_range command will further auto select the correct range

  def open_instrument(self):
    super().open_instrument()
    self._check_channel_number()

  def open_interface(self):
    super().open_interface()
    # We need to set to remote mode first, so don't run init options here
    self.inst.send_raw(b'SYSTem:REMote')

  def _check_channel_number(self):
    # Find the max number of channels
    max_ch = int(self.data_handler.query('CHAN MAX;CHAN?'))
    # Get Channel module model
    for ch in range(max_ch):
      self.data_handler.send(f'CHAN {ch + 1}')
      _, channel_id, _ = self.data_handler.query('CHAN:ID?').split(',', 2)
      match = re.search(r'[0-9]*-[0-9]*-[0-9]*', channel_id)
      if not match:
        raise MatchError('Channel ID cannot be found, please check your model!')
      channel_id = match.group(0)
      self.ch_ids[ch + 1] = channel_id

  def _find_next_level(self, data: list[float], point: float) -> int:
    """Finds the first higher index in a list given a point.

    For example with [0, 1, 2, 3], if point = 1.5, then the return index should
    be 2

    Args:
        data (list[float]): The list of floating pt numbers
        point (float): The number to find the high index

    Returns:
       (int): The next higher index
    """
    try:
      idx = next(idx for idx, val in enumerate(data) if (val >= point))
      return int(idx)
    except StopIteration as exc:
      raise ValueError('Operation Value out of range!') from exc

  def _auto_range(self, channel: int, mode: str, value: float) -> None:
    """Internal function to autorange the load since Chroma63600 lacks one.

    Args:
        channel (int): The target channel
        mode (Eload.OpMode): The operation mode
        value (float): The value to program the operation mode to
    """
    # The range ends in L = Low, M = Medium, or H = High
    range_tags = ['L', 'M', 'H']
    model = self.ch_ids[channel]
    ranges = dataclasses.asdict(Chroma63600.RANGE[model])
    op_ranges = ranges[mode.lower()]
    index = self._find_next_level(op_ranges, value)
    range_cmd = f'{mode}{range_tags[index]}'
    self.data_handler.send(f'CHAN {channel}')
    self.data_handler.send(f'MODE {range_cmd}')

  def short_output(self, channel, enable) -> None:
    self.data_handler.send(f'CHAN {channel}')
    self.data_handler.send(f'LOAD:SHORT {int(enable)}')
    self.enable_output(channel, enable)

  def set_slewrate(self, channel, edge, rate) -> None:
    edge = util.get_from_dict(EDGE_SLOPE, edge)
    self.data_handler.send(f'CURRent:STATic:{edge} {rate}')

  def set_current_dynamic(
      self, channel: int, l1, t1, rise_rate, l2, t2, fall_rate, repeat
  ) -> None:
    raise NotImplementedError(
        'This function is not currently implemented in the Chroma63600'
    )

  def enable_output(self, channel, enable) -> None:
    # Channel output needs to be enabled/disabled in a certain order
    self.data_handler.send(f'CHAN {channel}')
    if enable:
      self.data_handler.send(f'CHANnel:ACTive {int(enable)}')
      self.data_handler.send(f'LOAD {int(enable)}')
    else:
      self.data_handler.send(f'LOAD {int(enable)}')
      self.data_handler.send(f'CHANnel:ACTive {int(enable)}')

  def set_mode(self, channel, mode) -> None:
    self.data_handler.send(f'CHAN {channel}')
    mode = util.get_from_dict(CHANNEL_MODE, mode)
    self.data_handler.send(f'MODE {mode}')

  def set_level(self, channel, mode, value, curr_lim=None) -> None:
    mode_cmd = {
        instrument.ChannelMode.CURRENT_DC: 'CURRent',
        instrument.ChannelMode.VOLTAGE_DC: 'VOLTage',
        instrument.ChannelMode.RESISTANCE: 'RESistance',
        instrument.ChannelMode.POWER: 'POWer',
    }
    self.data_handler.send(f'CHAN {channel}')
    self.data_handler.send(f'{mode_cmd[mode]}:STATic:L1 {value}')
    if mode == instrument.ChannelMode.VOLTAGE_DC and curr_lim:
      self.data_handler.send(f'VOLTage:STAT:ILIMit {curr_lim}')

  def set_sequence(self, channel, voltage, current, delay) -> None:
    raise NotImplementedError(
        'This function is not currently implemented in the Chroma63600'
    )

  def set_range(self, channel, range_type, value) -> None:
    range_type = util.get_from_dict(CHANNEL_MODE, range_type)
    self._auto_range(channel, range_type[:2], value)

  def set_NPLC(
      self,
      channel: int | list[int],
      power_line_freq: int,
      nplc: float | list[float],
  ) -> None:
    raise NotImplementedError(
        'This function is not currently implemented in the Chroma63600'
    )

  def measure_current(self, channel) -> float:
    self.data_handler.send(f'CHAN {channel}')
    return float(self.data_handler.query('MEASure:CURRent?'))

  def measure_voltage(self, channel) -> float:
    self.data_handler.send(f'CHAN {channel}')
    return float(self.data_handler.query('MEASure:VOLTage?'))
