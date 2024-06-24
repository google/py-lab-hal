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

"""Demo code for Stepper Motor."""

import time

from py_lab_hal import builder
from py_lab_hal.cominterface import cominterface


def main() -> None:
  build = builder.PyLabHALBuilder()
  build.connection_config = cominterface.ConnectConfig(
      visa_resource='/dev/ttyUSB0',
      serial_config=cominterface.SerialConfig(
          baud_rate=115200,
          flow_control=cominterface.ControlFlow.RST_CTS,
      ),
      # py_lab_hal_board_ip='192.168.29.46:50051',
      terminator=cominterface.TerminatorConfig(read=''),
  )

  thro = build.build_instrument(builder.StepperMotor.THORLABS_HDR50)

  time.sleep(2)
  thro.home(1)

  # thro.set_vel(1, 5, 10)
  thro.set_jog(1, 'SIN', 10, 5, 10, 'CON')

  for i in range(10):
    thro.set_move_abs(1, 10 * (i + 1))
    thro.move_absolute(1)
    # thro.move_jog(1, 'FOR')
    time.sleep(1)

  thro.home(1)


if __name__ == '__main__':
  main()
