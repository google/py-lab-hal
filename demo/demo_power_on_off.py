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
# TODO: b/333311346 - Possible scrub or exclude from external build, rail name.

"""Power On/Off Debugging Demo using a scope and USB Relay."""
import datetime
import time

from py_lab_hal import builder
from py_lab_hal.cominterface import cominterface
from py_lab_hal.util import util

build = builder.PyLabHALBuilder()

build.connection_config = cominterface.ConnectConfig(
    visa_resource='USB0::1689::1319::C040522::0::INSTR',
)
scope = build.build_instrument(builder.Scope.TEKTRONIX_MSO)

build.connection_config = cominterface.ConnectConfig(
    visa_resource='ASRL/dev/ttyUSB0::INSTR',
)
relay = build.build_instrument(builder.Relay.USBRELAY)

start_time = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')

time.sleep(1)

####################################################
# Scope setup
util.loop_channel(scope.set_channel_on_off, [1, 2, 3, 4], True)
util.loop_channel(scope.set_channel_bandwidth, [1, 2, 3, 4], 25e7, True)
util.loop_channel(
    scope.set_channel_position, [1, 2, 3, 4], [-1.9, -3.54, -1.8, -3]
)
util.loop_channel(scope.set_channel_offset, [1, 2, 3, 4], 0)
util.loop_channel(
    scope.set_channel_division, [1, 2, 3, 4], [0.5, 0.5, 0.5, 0.2]
)

scope.set_channel_labels(1, 'SOC_CAM_1V2_EN')
scope.set_channel_labels(2, 'PP3300')
scope.set_channel_labels(3, 'PP1800')
scope.set_channel_labels(4, 'PP1200')

scope.set_display_style('STA')

print('scope setup done')

# Time Scale 1
scope.set_horiz_division(1e-3)
print('Time Sclae 1 set done')

# Set to 40% horizontal position
scope.set_horiz_offset(40)

####################################################
for i in range(1):
  # Config Trigger to RISE
  scope.config_edge_trigger(3, 1.65, 'raise', 'Norm')
  print('Trigger Configured to RISE')
  scope.config_continuous_acquisition(False, True)
  scope.start_acquisition()

  # Power On
  relay.enable(1, True)
  print('AC Power On')
  scope.wait_acquisition_complete()

  # Set and Save - RISE
  numer = ''
  number_a = ''
  number = start_time + 'AC_HW_Reboot-' + str(i)
  number_a = number + '-RISE'
  scope.save_screenshot(number_a)
  print('Screenshot %s' % (number_a))
  time.sleep(3)

  # Config Trigger to FALL
  scope.config_edge_trigger(3, 1.65, 'fall', 'Norm')
  print('Trigger Configured to FALL')
  scope.config_continuous_acquisition(False, True)
  scope.start_acquisition()

  # Power Off
  relay.enable(1, True)
  print('AC Power Off')
  scope.wait_acquisition_complete()

  # Set and Save - FALL
  number_b = ''
  number_b = number + '-FALL'
  scope.save_screenshot(number_b)
  print('Screenshot %s' % (number_b))
  time.sleep(3)

scope.close()
relay.close()
