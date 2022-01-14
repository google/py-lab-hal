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

"""Parent Abstract Module of TempChamber."""

import abc

from py_lab_hal.instrument import instrument


class TempChamber(instrument.Instrument, metaclass=abc.ABCMeta):
  """Parent Abstract Class of TempChamber."""

  @abc.abstractmethod
  def enable_ramp(self, mode):
    pass

  @abc.abstractmethod
  def read_actual_temp(self) -> float:
    """Reads the current chamber temperature.

    Returns:
        (float): The result of the reading.
    """
    pass

  @abc.abstractmethod
  def read_set_point(self) -> float:
    """Reads the current Set Point or Set Value.

    Returns:
        (float): The result of the reading.
    """
    pass

  @abc.abstractmethod
  def set_ramp_rate(self, ramp_rate):
    """Sets the ramp rate in C per minute.

    This only takes effect if Enable_Ramp is ON.

    Args:
        ramp_rate (float): Ramp rate in C per minute.
    """
    pass

  @abc.abstractmethod
  def set_set_point(self, temper):
    """Sets the temperature Set Point.

    Args:
        temper (float): temperature of set point in C.
    """
    pass

  @abc.abstractmethod
  def run_profile(self, num_profile, run: bool):
    pass

  @abc.abstractmethod
  def delete_profile(self, num_porfile):
    pass

  @abc.abstractmethod
  def create_profile(self, name, number, step):
    pass

  @abc.abstractmethod
  def enable_power(self, mode: bool):
    """Select Mode to turn ON or OFF Power to the Chamber.

    Args:
        mode (bool): turn on/off
    """
    pass
