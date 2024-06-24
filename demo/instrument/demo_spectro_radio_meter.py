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

"""Demo code for spectro radio meter."""

from py_lab_hal import builder
from py_lab_hal.cominterface import cominterface


def main() -> None:
  build = builder.PyLabHALBuilder()
  build.connection_config = cominterface.ConnectConfig(
      visa_resource='/dev/ttyACM0'
  )
  build.instrument_config.idn = False
  build.instrument_config.reset = False
  build.instrument_config.clear = False
  radio_meter = build.build_instrument(builder.SpectroRadioMeter.KONICA_CS3000)

  try:
    print(radio_meter.measure())
    print(radio_meter.get_last_xy)
    print(radio_meter.get_last_colortemp())
    print(radio_meter.get_light_frequency())
  finally:
    radio_meter.close()


if __name__ == '__main__':
  main()
