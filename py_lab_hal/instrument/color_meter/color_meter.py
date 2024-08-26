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

"""Parent Abstract Module of Colormeter."""

import abc

from py_lab_hal.instrument import instrument


class ColorMeter(instrument.Instrument, metaclass=abc.ABCMeta):
  """Parent Abstract Class of Colormeter."""

  @abc.abstractmethod
  def measure_XYZ(self):
    pass

  @abc.abstractmethod
  def measure_Yxy(self):
    pass

  @abc.abstractmethod
  def measure_Yuv(self):
    pass

  @abc.abstractmethod
  def measure_CCT(self):
    pass

  @abc.abstractmethod
  def measure_luminance(self):
    pass

  @abc.abstractmethod
  def measure_colortemp(self):
    pass
