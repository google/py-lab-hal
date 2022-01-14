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

"""Parent Abstract Module of DMM."""

import abc

from py_lab_hal.instrument import instrument


class DMM(instrument.Instrument, metaclass=abc.ABCMeta):
  """Parent Abstract Class of DMM."""

  channel_modes: dict[int, instrument.ChannelMode]

  @abc.abstractmethod
  def set_NPLC(
      self,
      channel: int,
      value: int | instrument.ValueRange = instrument.ValueRange.DEFFULT,
  ) -> None:
    """Sets the number of points per cycle.

    Args:
        channel (int): The specified output channel.
        value (int): The specified number of points per cycle.
    """
    pass

  @abc.abstractmethod
  def _config_channel_mode(self, channel: int, mode: instrument.ChannelMode):
    """Config the channel mode of the instrument.

    Args:
        channel (int): The specified output channel.
        mode (instrument.ChannelMode): The specified channel mode.
    """
    pass

  def config_channel_mode(self, channel: int, mode: instrument.ChannelMode):
    """Configures the channel mode.

    Args:
        channel (int): The specified output channel.
        mode (instrument.ChannelMode): The specified channel mode.
    """
    self.channel_modes.update({channel: mode})
    self._config_channel_mode(channel, mode)

  @abc.abstractmethod
  def config_range(
      self,
      channel: int,
      value: float | instrument.ValueRange = instrument.ValueRange.DEFFULT,
  ):
    """Configures the range.

    Args:
        channel (int): The specified output channel.
        value (float): The specified range.
    """
    pass

  @abc.abstractmethod
  def config_resolution(
      self,
      channel: int,
      value: float | instrument.ValueRange = instrument.ValueRange.DEFFULT,
  ):
    pass

  @abc.abstractmethod
  def config_autorange(self, channel: int, enable: bool) -> None:
    """Selects whether to enable or not the Autorange function of the DMM.

    Select from the measurement functions to enable Autorange func and the
    channel to enable if using a multi-channel DAQ.

    Args:
        channel (int): The specified output channel.
        enable (bool): If true the Autorange function is enabled.
    """
    pass

  @abc.abstractmethod
  def config_autozero(self, channel: int, enable: bool) -> None:
    """Selects whether to enable or not the Autozero function of the DMM.

    Select from the measurement functions to enable Autozero func and the
    channel to enable if using a multi-channel DAQ.

    Args:
        channel (int): The specified output channel.
        enable (bool): If true the Autozero function is enabled.
    """
    pass

  @abc.abstractmethod
  def config_temperature_probe(
      self, channel: int, probe_type: instrument.TemperatureTransducer
  ) -> None:
    """Configures the temperature probe.

    Args:
        channel (int): The specified output channel.
        probe_type (instrument.TemperatureTransducer): The specified temperature
          probe.
    """
    pass

  @abc.abstractmethod
  def config_thermo_couple(
      self, channel: int, thermo_type: instrument.ThermoCouple
  ) -> None:
    """Configures the thermo couple.

    Args:
        channel (int): The specified output channel.
        thermo_type (instrument.ThermoCouple): The specified thermo couple.
    """
    pass

  def config_measurement(
      self,
      channel: int,
      function: instrument.ChannelMode,
      auto_range: bool,
      mea_range: float | instrument.ValueRange,
      abs_resolution: float | instrument.ValueRange,
  ) -> None:
    """Configures the measurement function of the DMM.

    Args:
        channel (int): The specified output channel.
        function (instrument.ChannelMode): The specified channel mode.
        auto_range (bool): The specified auto range.
        mea_range (float): The specified measurement range.
        abs_resolution (float): The specified absolute resolution.
    """

    self.config_channel_mode(channel, function)
    self.config_autorange(channel, auto_range)
    self.config_range(channel, mea_range)
    self.config_resolution(channel, abs_resolution)

  def config_temperature_measurement(
      self,
      channel: int,
      abs_resolution: float,
      temper_probe_type: instrument.TemperatureTransducer = instrument.TemperatureTransducer.THERMO_COUPLE,
      temper_type: instrument.ThermoCouple = instrument.ThermoCouple.T,
  ):
    """Configures the measurement function of the DMM.

    Args:
        channel (int): The specified output channel.
        abs_resolution (float): The specified absolute resolution.
        temper_probe_type (instrument.TemperatureTransducer): The specified
          temperature probe.
        temper_type (instrument.ThermoCouple): The specified thermo couple.
    """
    self.config_channel_mode(channel, instrument.ChannelMode.TEMPERATURE)
    self.config_temperature_probe(channel, temper_probe_type)
    self.config_thermo_couple(channel, temper_type)
    self.config_resolution(channel, abs_resolution)

  @abc.abstractmethod
  def read(self, channel: int = 1, timeout: float = 10) -> float:
    """Get the reading og the instrument.

    Args:
        channel (int): The specified output channel.
        timeout (float): The second of the timeout setting.

    Returns:
        (float): The result of the reading depending on the input of the
        channel.
    """
    pass
