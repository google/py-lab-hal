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

"""Common code for Keysight N6705C."""

from py_lab_hal.cominterface import cominterface
from py_lab_hal.instrument import instrument
from py_lab_hal.util import util


def get_polarity(value: float):
  if value >= 0:
    return 'POS'
  return 'NEG'


POSITIVE_VOLTAGE = [
    instrument.SmuEmulationMode.PS2Q,
    instrument.SmuEmulationMode.PS1Q,
    instrument.SmuEmulationMode.BATTERY,
    instrument.SmuEmulationMode.CHARGER,
    instrument.SmuEmulationMode.CVLOAD,
]

POSITIVE_CURRENT = [
    instrument.SmuEmulationMode.PS1Q,
    instrument.SmuEmulationMode.CHARGER,
]

NEGATIVE_CURRENT = [instrument.SmuEmulationMode.CCLOAD]

CHANNEL_MODE = {
    instrument.ChannelMode.VOLTAGE_DC: 'VOLTage:DC',
    instrument.ChannelMode.CURRENT_DC: 'CURRent:DC',
    instrument.ChannelMode.RESISTANCE: 'RESistance',
    instrument.ChannelMode.RESISTANCE_4WIRE: 'RESistance',
}

EDGE_SLOPE = {
    instrument.EdgeTriggerSlope.RISE: 'POSitive',
    instrument.EdgeTriggerSlope.FALL: 'NEGative',
}


def check_current_input(
    value: float, emulation_mode: instrument.SmuEmulationMode
):
  if value < 0 and emulation_mode in POSITIVE_CURRENT:
    raise RuntimeError('Current can not be less than 0')
  if value > 0 and emulation_mode in NEGATIVE_CURRENT:
    raise RuntimeError('Current can not be greater than 0')


def check_voltage_input(
    value: float, emulation_mode: instrument.SmuEmulationMode
):
  if value < 0 and emulation_mode in POSITIVE_VOLTAGE:
    raise RuntimeError('Voltage can not be less than 0')


class KeysightN6705c(instrument.Instrument):
  """Child Smu Class of Keysightn6705c."""

  def __init__(
      self,
      com: cominterface.ComInterfaceClass,
      inst_config: instrument.InstrumentConfig,
  ) -> None:
    super().__init__(com, inst_config)
    self.priority = instrument.ChannelMode.VOLTAGE_DC
    self.emulation_mode = instrument.SmuEmulationMode.BATTERY

  # Helper function for N6705C

  def select_mode(
      self,
      channel: int,
      mode: instrument.SmuEmulationMode = instrument.SmuEmulationMode.BATTERY,
  ):
    self.data_handler.send(f'EMULation {mode},(@{channel})')

  def set_level(
      self,
      channel: int,
      mode: instrument.ChannelMode,
      value: float,
      is_limit: bool = False,
  ):
    limit_command = f':LIM:{get_polarity(value)}' if is_limit else ''
    mode = util.get_from_dict(CHANNEL_MODE, mode)
    self.data_handler.send(f'SOUR:{mode}{limit_command} {value},(@{channel})')

  # The function for the Instrument

  def set_priority(self, channel: int, priority: instrument.ChannelMode):
    self.data_handler.send(f'FUNC {priority}, (@{channel})')
    self.priority = priority

  def enable_output(self, channel, enable):
    self.data_handler.send(f'OUTP:STATE {int(enable)},(@{channel})')

  def enable_remote_sense(self, channel, enable):
    if enable == 1:
      rem = 'EXT'
    else:
      rem = 'INT'
    self.data_handler.send(f'VOLT:SENS:SOUR {rem},(@{channel})')

  def enable_OCP(self, channel, enable):
    self.data_handler.send(f'SOUR:CURR:PROT:STAT {int(enable)}, (@{channel})')

  def enable_OVP(self, channel, enable):
    self.data_handler.send(f'SOUR:VOLT:PROT:STAT {int(enable)}, (@{channel})')

  def set_output_voltage(self, channel, voltage):
    check_voltage_input(voltage, self.emulation_mode)
    if self.priority == instrument.ChannelMode.VOLTAGE_DC:
      self.set_level(channel, instrument.ChannelMode.VOLTAGE_DC, voltage, False)
    elif self.priority == instrument.ChannelMode.CURRENT_DC:
      self.set_level(channel, instrument.ChannelMode.VOLTAGE_DC, voltage, True)
    else:
      raise RuntimeError(f'Can not set current in this mode {self.priority}')

  def set_output_current(self, channel, current):
    check_current_input(current, self.emulation_mode)
    if self.priority == instrument.ChannelMode.VOLTAGE_DC:
      self.set_level(channel, instrument.ChannelMode.CURRENT_DC, current, True)
    elif self.priority == instrument.ChannelMode.CURRENT_DC:
      self.set_level(channel, instrument.ChannelMode.CURRENT_DC, current, False)
    else:
      raise RuntimeError(f'Can not set current in this mode {self.priority}')

  def set_OVP_value(self, channel, ovp_voltage):
    self.data_handler.send(
        f'SOUR:VOLT:PROT:REM:{get_polarity(ovp_voltage)} {ovp_voltage},(@{channel})'
    )

  def set_range(self, channel, range_type, max_value):
    range_type = util.get_from_dict(CHANNEL_MODE, range_type)
    self.data_handler.send(f'SOUR:{range_type}:RANG {max_value},(@{channel})')

  def set_slewrate(self, channel, edge, rate):
    mode = self.data_handler.query(f'FUNC? (@{channel})')
    edge = util.get_from_dict(EDGE_SLOPE, edge)
    self.data_handler.send(f'{mode}:SLEW:{edge} {rate},(@{channel})')

  def short_output(self, channel, enable):
    self.data_handler.send(f'OUTPut:SHORt {int(enable)},(@{channel}')

  def measure_current(self, channel) -> float:
    self.data_handler.send(f'measure:scalar:current? (@{channel})')
    return float(self.data_handler.recv())

  def measure_voltage(self, channel) -> float:
    self.data_handler.send(f'measure:scalar:voltage? (@{channel})')
    return float(self.data_handler.recv())

  def measure_power(self, channel) -> float:
    self.data_handler.send(f'measure:scalar:power? (@{channel})')
    return float(self.data_handler.recv())
