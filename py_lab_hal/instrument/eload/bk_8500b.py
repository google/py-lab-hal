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

"""Child eload Module of BK Precision 8500B Series.

The BK Precision 8500B Series Programmable DC Electronic Load System consists of
8542B
8500B
8502B
8510B
8514B
"""

from __future__ import annotations

import warnings

from py_lab_hal.cominterface import cominterface
from py_lab_hal.instrument import instrument
from py_lab_hal.instrument.eload import eload
from py_lab_hal.util import util


CHANNEL_MODE = {
    instrument.ChannelMode.VOLTAGE_DC: 'VOLTage',
    instrument.ChannelMode.CURRENT_DC: 'CURRent',
    instrument.ChannelMode.RESISTANCE: 'RESistance',
    instrument.ChannelMode.POWER: 'POWer',
}

EDGE_SLOPE = {
    instrument.EdgeTriggerSlope.RISE: 'RISE',
    instrument.EdgeTriggerSlope.FALL: 'FALL',
}


class Bk8500b(eload.Eload):
  """Child eload Class of Bk8500b."""

  def open_interface(self):
    super().open_interface()
    # We need to set to remote mode first, so don't run init options here
    self.inst.send_raw(b'SYSTem:REMote')

  def short_output(self, channel, enable) -> None:
    self.data_handler.send(f'INPut:SHORt {int(enable)}')
    self.enable_output(channel, enable)

  def set_slewrate(self, channel, edge, rate) -> None:
    edge = util.get_from_dict(EDGE_SLOPE, edge)
    self.data_handler.send(f'CURRent:SLEW:{edge} {rate}')

  def set_current_dynamic(
      self, channel: int, l1, t1, rise_rate, l2, t2, fall_rate, repeat
  ) -> None:
    raise NotImplementedError(
        'This function is not currently implemented in the BK8500B'
    )

  def enable_output(self, channel, enable) -> None:
    self.data_handler.send(f'INPut {int(enable)}')

  def set_mode(self, channel, mode) -> None:
    mode = util.get_from_dict(CHANNEL_MODE, mode)
    self.data_handler.send(f'FUNCtion {mode}')

  def set_level(self, channel, mode, value, curr_lim=None) -> None:
    """Sets the operation level of the selected channel.

    Units are:
      current, A
      voltage, V
      power, W
      resistance, ohm

    Args:
      channel (int): The target channel
      mode (ChannelMode): The operation mode to set the level
      value (float): The operating level
      curr_lim (float): The optional current limit to set when op_mode = cv

    The BK8500 Does not support Current Limiting in CV Mode!!!
    """
    mode_str = util.get_from_dict(CHANNEL_MODE, mode)
    self.data_handler.send(f'{mode_str} {value}')
    if mode == instrument.ChannelMode.VOLTAGE_DC and curr_lim is not None:
      warnings.warn(
          'The BK8500 Series does not support Current Limitingover CV mode!'
      )

  def set_sequence(self, channel, voltage, current, delay) -> None:
    raise NotImplementedError(
        'This function is not currently implemented in the BK8500B'
    )

  def set_range(self, channel, range_type, value) -> None:
    if (
        range_type == instrument.ChannelMode.CURRENT_DC
        or range_type == instrument.ChannelMode.VOLTAGE_DC
    ):
      range_type = util.get_from_dict(CHANNEL_MODE, range_type)
      self.data_handler.send(f'{range_type}:RANGe {value}')
    else:
      raise NotImplementedError(
          'The BK8500B does not support range settings for CR or CP mode'
      )

  def set_NPLC(self, channel, power_line_freq, nplc) -> None:
    raise NotImplementedError(
        'This function is not currently implemented in the BK8500B'
    )

  def measure_current(self, channel) -> float:
    return float(self.data_handler.query('MEASure:CURRent?'))

  def measure_voltage(self, channel) -> float:
    return float(self.data_handler.query('MEASure:VOLTage?'))
