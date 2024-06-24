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

"""Generic Demo using a dc power supply to output voltage and dmm read back."""

import time

from py_lab_hal import builder
from py_lab_hal.cominterface import cominterface

build = builder.PyLabHALBuilder()

build.connection_config = cominterface.ConnectConfig(
    visa_resource='USB0::10893::769::MY59006118::0::INSTR',
)
dmm = build.build_instrument(builder.DMM.AGILENT_34465A)


build.connection_config = cominterface.ConnectConfig(
    visa_resource='ASRL/dev/ttyUSB0::INSTR',
    serial_config=cominterface.SerialConfig(),
)
dcpsu = build.build_instrument(builder.DCPowerSupply.GWIN_PST3202)

try:
  dcpsu.set_output(1, 5, 1)
  dcpsu.enable_output(1, True)
  print('output 5 V')
  time.sleep(1)
  for i in range(5):
    print(dmm.read())

  dcpsu.set_output(1, 6, 1)
  dcpsu.enable_output(1, True)
  print('output 6 V')
  time.sleep(1)
  for i in range(5):
    print(dmm.read())

finally:
  dmm.close()
  dcpsu.close()
