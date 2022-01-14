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

"""Parent Abstract Module of ACpsu."""

import abc

from py_lab_hal.instrument import instrument


class ACpsu(instrument.Instrument, metaclass=abc.ABCMeta):
  """Parent Abstract Class of ACpsu."""

  @abc.abstractmethod
  def set_output(self, voltage, current, freq):
    pass

  @abc.abstractmethod
  def set_output_coupling(self, coupling_mode, dc_offset):
    pass

  @abc.abstractmethod
  def enable_output(self, coupling_mode, enable: bool):
    pass

  @abc.abstractmethod
  def set_voltage_range(self, max_value):
    pass

  @abc.abstractmethod
  def set_voltage_phase(self, phase):
    pass

  @abc.abstractmethod
  def measure_current(self) -> tuple[float, float, float]:
    pass

  @abc.abstractmethod
  def measure_voltage(self) -> tuple[float, float]:
    pass

  @abc.abstractmethod
  def measure_power(self) -> tuple[float, float, float, float]:
    pass

  @abc.abstractmethod
  def measure_freq(self) -> float:
    pass
