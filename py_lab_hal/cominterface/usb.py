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

"""Py-Lab-Hal USB communication interface implementation."""

from py_lab_hal.cominterface import cominterface


class Usb(cominterface.ComInterfaceClass):
  inst = None

  def __init__(self, connect_config: cominterface.ConnectConfig) -> None:
    super().__init__(connect_config)
    self.connect_config.interface_type = 'usb'
