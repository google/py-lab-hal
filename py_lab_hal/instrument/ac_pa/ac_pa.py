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

"""Parent Abstract Module of ACPA."""

import abc

from py_lab_hal.instrument import instrument


class ACPA(instrument.Instrument, metaclass=abc.ABCMeta):
  """Parent Abstract Class of ACPA."""

  # TODO: b/333308711 - Check need for enums for methods.
  @abc.abstractmethod
  def display(self, display):
    pass

  @abc.abstractmethod
  def shunt_selection(self, shunt):
    pass

  @abc.abstractmethod
  def set_mode(self, mode):
    pass

  @abc.abstractmethod
  def set_measurement_type(self, measurement_type):
    pass

  @abc.abstractmethod
  def configure_system(
      self,
      blaking: bool,
      averaging: bool,
      auto_zero: bool,
  ):
    pass

  @abc.abstractmethod
  def read_measurement(
      self,
      measurement_type,
      averaging: bool,
      auto_zero: bool,
  ):
    pass

  @abc.abstractmethod
  def clear_measurement(self):
    pass
