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

"""Demo code for DCpsu."""

from py_lab_hal import builder
from py_lab_hal.cominterface import cominterface


def main() -> None:
  build = builder.PyLabHALBuilder()
  build.connection_config = cominterface.ConnectConfig(
      visa_resource='USB0::10893::3842::MY56002119::0::INSTR',
  )

  dcpsu = build.build_instrument(builder.DCPowerSupply.KEYSIGHT_N6705C)
  instrument_channel = 3
  try:
    dcpsu.set_output(instrument_channel, 5, 1)
    dcpsu.enable_output(instrument_channel, True)
    dcpsu.measure_current(instrument_channel)
    dcpsu.measure_voltage(instrument_channel)
    dcpsu.enable_OCP(instrument_channel, True)
    dcpsu.set_output(instrument_channel, 5, 1)
    dcpsu.enable_output(instrument_channel, True)
    dcpsu.measure_current(instrument_channel)
    dcpsu.measure_voltage(instrument_channel)
    dcpsu.set_OVP_value(instrument_channel, 6)
    dcpsu.enable_OVP(instrument_channel, True)
  finally:
    dcpsu.close()


if __name__ == '__main__':
  main()
