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

"""Child Light Module of ArriS120."""

from py_lab_hal.cominterface import cominterface
from py_lab_hal.cominterface import dmx
from py_lab_hal.instrument import instrument
from py_lab_hal.instrument.light import light

COLOR_TEMPERATURE_MAX = 10_000
COLOR_TEMPERATURE_MIN = 2_800

DIMMER_HI_CHANNEL_OFFSET = 1
DIMMER_LO_CHANNEL_OFFSET = 2

COLOR_TEMPERATURE_HI_CHANNEL_OFFSET = 3
COLOR_TEMPERATURE_LO_CHANNEL_OFFSET = 4

RED_HI_CHANNEL_OFFSET = 9
RED_LO_CHANNEL_OFFSET = 10

GREEN_HI_CHANNEL_OFFSET = 11
GREEN_LO_CHANNEL_OFFSET = 12

BLUE_HI_CHANNEL_OFFSET = 13
BLUE_LO_CHANNEL_OFFSET = 14


def _check_percentage(percentage: float):
  if not 0 <= percentage <= 1:
    raise ValueError('The percentage should between 0 - 1')


def percent_to_twobytes(percent: float) -> tuple[int, int]:
  value = int(percent * 0xFFFF)
  return (value & 0xFF00) >> 8, value & 0x00FF


def cal_percent(value, max_value, min_value):
  return (value - min_value) / (max_value - min_value)


class ArriS120(light.Light):
  """Child Light Class of ArriS120.

  Properties:
    base_channel: The base channel of the DMX device.
  """

  inst: dmx.Dmx

  def __init__(
      self,
      com: cominterface.ComInterfaceClass,
      inst_config: instrument.InstrumentConfig,
  ) -> None:
    super().__init__(com, inst_config)

    self.base_channel = 1

  def set_base_channel(self, base_channel: int) -> None:
    """Set the base channel of the DMX device.

    Args:
      base_channel (int): The base channel of the DMX device.
    """
    self.base_channel = base_channel

  def dimmer(self, percent) -> None:
    _check_percentage(percent)
    hi, lo = percent_to_twobytes(percent)

    self.inst.set_value(self.base_channel + DIMMER_HI_CHANNEL_OFFSET, hi)
    self.inst.set_value(self.base_channel + DIMMER_LO_CHANNEL_OFFSET, lo)

  def color_temperature(self, kelvins: int) -> None:
    if not COLOR_TEMPERATURE_MIN <= kelvins <= COLOR_TEMPERATURE_MAX:
      raise ValueError(
          f'The kelvins should between {COLOR_TEMPERATURE_MIN} -'
          f' {COLOR_TEMPERATURE_MAX}'
      )

    percent = cal_percent(kelvins, COLOR_TEMPERATURE_MAX, COLOR_TEMPERATURE_MIN)

    hi, lo = percent_to_twobytes(percent)

    self.inst.set_value(
        self.base_channel + COLOR_TEMPERATURE_HI_CHANNEL_OFFSET, hi
    )
    self.inst.set_value(
        self.base_channel + COLOR_TEMPERATURE_LO_CHANNEL_OFFSET, lo
    )

  def red(self, percent) -> None:
    _check_percentage(percent)

    hi, lo = percent_to_twobytes(percent)

    self.inst.set_value(self.base_channel + RED_HI_CHANNEL_OFFSET, hi)
    self.inst.set_value(self.base_channel + RED_LO_CHANNEL_OFFSET, lo)

  def green(self, percent) -> None:
    _check_percentage(percent)

    hi, lo = percent_to_twobytes(percent)

    self.inst.set_value(self.base_channel + GREEN_HI_CHANNEL_OFFSET, hi)
    self.inst.set_value(self.base_channel + GREEN_LO_CHANNEL_OFFSET, lo)

  def blue(self, percent) -> None:
    _check_percentage(percent)

    hi, lo = percent_to_twobytes(percent)

    self.inst.set_value(self.base_channel + BLUE_HI_CHANNEL_OFFSET, hi)
    self.inst.set_value(self.base_channel + BLUE_LO_CHANNEL_OFFSET, lo)

  def submit(self) -> None:
    """Send the DMX signal."""
    self.inst.submit()
