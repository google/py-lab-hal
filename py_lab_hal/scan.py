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

"""Scan helper."""

import io
import platform

from py_lab_hal.cominterface import serial
from py_lab_hal.cominterface import usbmonsoon
from py_lab_hal.cominterface import usbtmc
from py_lab_hal.cominterface import visa
from py_lab_hal.cominterface import vxi11

IS_WIN = platform.system() == 'Windows'


def main() -> tuple[str, list[str], list[str]]:
  """The main entry point of the scan."""
  data = io.StringIO()

  serial_resource = []
  network_resource = []

  serial_resource += usbmonsoon.list_resources(data, IS_WIN)

  if IS_WIN:
    serial_resource += visa.list_resources(data, IS_WIN)
  else:
    serial_resource += usbtmc.list_resources(data, IS_WIN)

    network_resource += vxi11.list_resources(data, IS_WIN)

  serial_resource += serial.list_resources(data, IS_WIN)

  return data.getvalue(), serial_resource, network_resource


if __name__ == '__main__':
  resource_string, _, _ = main()
  print(resource_string)
