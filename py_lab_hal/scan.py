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


def main() -> str:
  """The main entry point of the scan."""
  data = io.StringIO()

  usbmonsoon.list_resources(data, IS_WIN)

  if IS_WIN:
    visa.list_resources(data, IS_WIN)
  else:
    usbtmc.list_resources(data, IS_WIN)

    vxi11.list_resources(data, IS_WIN)

  serial.list_resources(data, IS_WIN)

  return data.getvalue()


if __name__ == '__main__':
  print(main())
