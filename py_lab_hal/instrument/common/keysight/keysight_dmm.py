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

"""Common Layer for Keysight DMMs."""

from py_lab_hal.instrument import instrument
from py_lab_hal.instrument.dmm.dmm import DMM
from py_lab_hal.util import util


CHANNEL_MODE = {
    instrument.ChannelMode.VOLTAGE_DC: 'VOLTage:DC',
    instrument.ChannelMode.VOLTAGE_AC: 'VOLTage:AC',
    instrument.ChannelMode.CURRENT_DC: 'CURRent:DC',
    instrument.ChannelMode.CURRENT_AC: 'CURRent:AC',
    instrument.ChannelMode.RESISTANCE: 'RESistance',
    instrument.ChannelMode.RESISTANCE_4WIRE: 'FRESistance',
    instrument.ChannelMode.TEMPERATURE: 'TEMPerature',
    instrument.ChannelMode.FREQUENCY: 'FREQuency',
}


TEMP_TRANSDUCER = {
    instrument.TemperatureTransducer.RTD: 'RTD',
    instrument.TemperatureTransducer.RTD_4WIRE: 'FRTD',
    instrument.TemperatureTransducer.THERMISTOR: 'THERmistor',
    instrument.TemperatureTransducer.THERMISTOR_4WIRE: 'FTHermistor',
    instrument.TemperatureTransducer.THERMO_COUPLE: 'TCouple',
}

THERMO_COUPLE = {
    instrument.ThermoCouple.E: 'E',
    instrument.ThermoCouple.J: 'J',
    instrument.ThermoCouple.K: 'K',
    instrument.ThermoCouple.N: 'N',
    instrument.ThermoCouple.R: 'R',
    instrument.ThermoCouple.T: 'T',
}

VALUE_RANGE = {
    instrument.ValueRange.DEFFULT: 'DEFAULT',
    instrument.ValueRange.MAX: 'MAX',
    instrument.ValueRange.MIN: 'MIN',
}


def _map_value_range(value):
  if isinstance(value, instrument.ValueRange):
    return util.get_from_dict(VALUE_RANGE, value)
  return


class KeysightDMM(DMM):
  """Parent Common Abstract Class of Keysight Common."""

  def error_check(self) -> None:
    error_code, error_message = self.data_handler.query('system:error?').split(
        ','
    )
    error_code = int(error_code)
    error_message = error_message.strip(' "')
    print(f'Code: {error_code}, Message: {error_message}\n')

  def read(self, channel=1, timeout=10) -> float:
    self.data_handler.send(':read?')
    return float(self.data_handler.recv())

  def _get_channel_mode(self, channel: int):
    return util.get_from_dict(CHANNEL_MODE, self.channel_modes[channel])

  def _sense_command(self, channel, config_type, value):
    channel_mode = self._get_channel_mode(channel)
    self.data_handler.send(f'{channel_mode}:{config_type} {value}')

  def _config_channel_mode(self, channel, mode):
    channel_mode = util.get_from_dict(CHANNEL_MODE, mode)
    self.data_handler.send(f'CONF:{channel_mode}')

  def config_range(self, channel, value=instrument.ValueRange.DEFFULT):
    self._sense_command(channel, 'RANGE', _map_value_range(value))

  def config_autorange(self, channel, enable) -> None:
    self._sense_command(channel, 'RANGE:AUTO', int(enable))

  def config_autozero(self, channel, enable):
    self._sense_command(channel, 'ZERO:AUTO', 'ON' if enable else 'OFF')

  def config_temperature_probe(
      self, channel: int, probe_type: instrument.TemperatureTransducer
  ) -> None:
    self._sense_command(
        channel,
        'TRANsducer:TYPE',
        util.get_from_dict(TEMP_TRANSDUCER, probe_type),
    )

  def config_thermo_couple(self, channel, thermo_type):
    self._sense_command(
        channel,
        'TRANsducer:TCouple:TYPE',
        util.get_from_dict(THERMO_COUPLE, thermo_type),
    )

  def set_NPLC(self, channel, value=instrument.ValueRange.DEFFULT):
    self._sense_command(channel, 'NPLC', _map_value_range(value))

  def config_resolution(self, channel, value=instrument.ValueRange.DEFFULT):
    self._sense_command(channel, 'RES', _map_value_range(value))
