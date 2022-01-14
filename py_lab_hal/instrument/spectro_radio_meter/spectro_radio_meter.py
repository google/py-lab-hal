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

"""Parent Abstract Module of Spectroradiometer."""

import abc

from py_lab_hal.instrument import instrument


class SpectroRadioMeter(instrument.Instrument, metaclass=abc.ABCMeta):
  """Parent Abstract Class of Spectroradiometer."""

  @abc.abstractmethod
  def get_last_tristim(self):
    """Get the CIE 1931 tristimulus value of the last measurement.

    X = CIE 1931 tristimulus X (Red).
    Y = CIE 1931 tristimulus Y (Green).
    Z = CIE 1931 tristimulus Z (Blue).
    """
    pass

  @abc.abstractmethod
  def get_last_uv(self):
    """Get the photometric brightness CIE 1976 u', v' of the last measurement.

    Y = Photometric brightness.
    u'= CIE 1976 u'.
    v'= CIE 1976 v'.
    """
    pass

  @abc.abstractmethod
  def get_last_xy(self):
    """Get the photometric brightness CIE 1931 x,y of the last measurement.

    Y = Photometric brightness.
    x = CIE 1931 x.
    y = CIE 1931 y.
    """
    pass

  @abc.abstractmethod
  def get_last_spectrum(self):
    """Get the spectral radiation luminance value of the last measurement."""
    pass

  @abc.abstractmethod
  def get_last_colortemp(self):
    """Get the color temperature of the last measurement."""
    pass

  @abc.abstractmethod
  def get_light_frequency(self):
    """Get the light frequency of the last measurement."""
    pass

  @abc.abstractmethod
  def measure(self):
    pass
