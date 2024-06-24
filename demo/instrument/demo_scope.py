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

"""Demo code for Scope."""

from py_lab_hal import builder
from py_lab_hal.cominterface import cominterface
from py_lab_hal.instrument import instrument


def main() -> None:
  build = builder.PyLabHALBuilder()
  build.connection_config = cominterface.ConnectConfig(
      visa_resource='USB0::1689::1319::C040522::0::INSTR',
  )

  scope = build.build_instrument(builder.Scope.TEKTRONIX_MSO)

  try:
    scope.set_display_style(instrument.LayoutStyle.OVERLAY)
    scope.set_channel_on_off(1, True)
    scope.set_channel_division(1, 1)
    scope.set_horiz_division(4e-4, 0.0, 0.0, instrument.HorizonType.SAMPLESIZE)
    scope.set_channel_coupling(1, instrument.ChannelCoupling.DC, 1_000_000)
    scope.config_edge_trigger(
        1,
        1,
        instrument.EdgeTriggerSlope.RISE,
        instrument.EdgeTriggerCoupling.DC,
    )
    scope.config_continuous_acquisition(False, True)
    scope.start_acquisition()
    scope.wait_acquisition_complete()
    print(scope.get_measurement_statistics(1))
    print(scope.fetch_waveform(1))
    print(scope.get_measurement_statistics(1))
  finally:
    scope.close()


if __name__ == '__main__':
  main()
