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

"""Demo code for Arch."""

from py_lab_hal import builder
from py_lab_hal.cominterface import cominterface


def main() -> None:
  build = builder.PyLabHALBuilder()
  build.connection_config = cominterface.ConnectConfig(
      network=cominterface.NetworkConfig(host='192.168.0.11', port=8000)
  )

  arm = build.build_instrument(builder.Arm.ARCH)

  try:
    arm.move_to_origin()
    arm.abs_move_to(x=100, y=400)
    arm.rel_move_to(x=-100, y=-400)
  finally:
    arm.close()


if __name__ == '__main__':
  main()
