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

"""Abstract class for Power Meter/Monitor."""

import abc
import dataclasses
from typing import Any, List

from py_lab_hal.instrument import instrument
from py_lab_hal.util import util


class SamplingMode(util.PyLabHalEnum):
  periodic = 1
  oneShot = 2


@dataclasses.dataclass
class MeasurementTriggerConfig:
  startTrigger: Any = None
  stopTrigger: Any = None
  triggerChannel: Any = None
  numSamples: int = 1
  samplingMode: SamplingMode = SamplingMode.oneShot
  enableConsoleOut = False


@dataclasses.dataclass
class PowerMeasurements:
  pass


class PowerMeter(instrument.Instrument, metaclass=abc.ABCMeta):

  @abc.abstractmethod
  def set_output_voltage(
      self,
      voltage: float,
  ):
    """Sets the output voltage.

    Args:
        voltage (float): Output voltage to be set on selected source.
    """
    pass

  @abc.abstractmethod
  def start_sampling(self, measurement_cfg: MeasurementTriggerConfig):
    """Starts the power measurement sampling."""
    pass

  @abc.abstractmethod
  def stop_sampling(self, measurement_cfg: MeasurementTriggerConfig):
    """Stops the power measurement if sampling is ongoing."""
    pass

  def enable_channel(self):
    """Enables power from the source channel."""
    pass

  @abc.abstractmethod
  def measure_current(self) -> List[PowerMeasurements]:
    """Returns measured value of instantaneous current."""
    pass

  @abc.abstractmethod
  def get_measurements(
      self, trigger_config: MeasurementTriggerConfig
  ) -> list[PowerMeasurements]:
    """Return available power measurements.

    Args:
        trigger_config (MeasurementTriggerConfig): Trigger configurations.

    Returns:
      PowerMeasurements: List of available PowerMeasurements.
    """
    pass
