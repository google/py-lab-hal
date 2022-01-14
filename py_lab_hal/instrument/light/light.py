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

"""Parent Abstract Module of Light."""

import abc

from py_lab_hal.instrument import instrument


class Light(instrument.Instrument, metaclass=abc.ABCMeta):
  """Parent Abstract Class of Light."""

  @abc.abstractmethod
  def dimmer(self, percent: float) -> None:
    """The dimmer leve; of the light.

    Args:
        percent (float): The percent of the dimmer.
    """
    pass

  @abc.abstractmethod
  def color_temperature(self, kelvins: int) -> None:
    """Set the color temperature of the light.

    Args:
        kelvins (int): Color Temperature in kelvins.
    """
    pass

  @abc.abstractmethod
  def red(self, percent: float) -> None:
    """Set the red intensity.

    Args:
        percent (float): The percentage of the intensity.
    """
    pass

  @abc.abstractmethod
  def green(self, percent: float) -> None:
    """Set the green intensity.

    Args:
        percent (float): The percentage of the intensity.
    """
    pass

  @abc.abstractmethod
  def blue(self, percent: float) -> None:
    """Set the blue intensity.

    Args:
        percent (float): The percentage of the intensity.
    """
    pass
