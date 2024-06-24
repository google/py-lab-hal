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

"""Demo code for Remote Power Switch."""

import time

from py_lab_hal import builder
from py_lab_hal.cominterface import cominterface
from py_lab_hal.instrument import instrument


def main() -> None:
  build = builder.PyLabHALBuilder()
  build.connection_config = cominterface.ConnectConfig(
      interface_type='http',
      http_config=cominterface.HttpConfig(
          url='192.168.29.55', login='admin', password='admin'
      ),
  )
  # build.connection_config = cominterface.ConnectConfig(
  #     interface_type='http',
  #     http_config=cominterface.HttpConfig(
  #         url='192.168.29.57', login='admin', password='admin'
  #     ),
  # )
  build.instrument_config = instrument.InstrumentConfig(False, False, False)
  remote = build.build_instrument(builder.RemotePowerSwitch.DIGIPDU_ZDHX)
  # remote = build.build_instrument(builder.RemotePowerSwitch.WEBPOWERSWITCH)
  try:
    for i in range(8):
      remote.enable(i + 1, True)
    time.sleep(10)
    for i in range(8):
      remote.enable(i + 1, False)
  finally:
    remote.close()


if __name__ == '__main__':
  main()
