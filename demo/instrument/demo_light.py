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

"""Demo code for Light."""

import time

from py_lab_hal import builder
from py_lab_hal.cominterface import cominterface


def main() -> None:
  build = builder.PyLabHALBuilder()
  build.connection_config = cominterface.ConnectConfig(
      interface_type='dmx',
      visa_resource='/dev/ttyUSB0',
      serial_config=cominterface.SerialConfig(
          baud_rate=56700,
      ),
      terminator=cominterface.TerminatorConfig(write=''),
  )

  light = build.build_instrument(builder.Light.ARRI_S120)

  try:
    for i in range(100):
      light.dimmer(i / 100)
      light.color_temperature(10000)
      # light.red(1)
      # light.red(0.5)
      # light.red(0.5)
      light.submit()
      time.sleep(0.1)
    # light.red(1)
  finally:
    light.close()


if __name__ == '__main__':
  main()
