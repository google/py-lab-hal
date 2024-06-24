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

"""Board Client."""

import time
from py_lab_hal import instrument
from py_lab_hal.cominterface import cominterface


def main():
  cc = cominterface.ConnectConfig(
      # network=cominterface.NetworkConfig(host='127.0.0.1', port=5025),
      # py_lab_hal_board_ip='localhost:50051'
      # py_lab_hal_board_ip='192.168.43.119:50051',
      visa_resource='/dev/ttyUSB2',
      py_lab_hal_board_ip='100.85.211.180:50051',
  )

  com = cominterface.select(cc)
  # com.scan()

  relay = instrument.relay.Usbrelay(com, False, False)

  cc1 = cominterface.ConnectConfig(
      visa_resource='/dev/ttyUSB0',
      py_lab_hal_board_ip='100.85.211.180:50051',
  )
  com1 = cominterface.select(cc1)
  dc = instrument.dcpsu.Keysighte3632a(com1)

  try:
    dc.set_output(1, 5, 0.5)

    for _ in range(5):
      dc.enable_output(1, True)

      relay.enable(1, False)
      time.sleep(1)
      relay.enable(1, True)
      time.sleep(1)
      dc.enable_output(1, False)
      time.sleep(1)

  finally:
    dc.close()
    relay.close()


if __name__ == '__main__':
  main()
