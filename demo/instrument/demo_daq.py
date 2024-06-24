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

"""Demo code for DAQ."""

from py_lab_hal import builder
from py_lab_hal.cominterface import cominterface
from py_lab_hal.instrument import instrument


def main() -> None:
  build = builder.PyLabHALBuilder()
  build.connection_config = cominterface.ConnectConfig(
      visa_resource='ASRL/dev/ttyUSB0::INSTR',
      serial_config=cominterface.SerialConfig(baud_rate=56700),
  )

  daq = build.build_instrument(builder.DMM.KEYSIGHT_34970A)

  try:
    daq.config_measurement(
        105,
        instrument.ChannelMode.VOLTAGE_DC,
        False,
        0.1,
        instrument.ValueRange.DEFFULT,
    )
    print(daq.read(105))
  finally:
    daq.close()


if __name__ == '__main__':
  main()
