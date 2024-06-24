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

"""Demo code for Eload."""

from py_lab_hal import builder
from py_lab_hal.cominterface import cominterface


def main() -> None:
  build = builder.PyLabHALBuilder()
  build.connection_config = cominterface.ConnectConfig(
      visa_resource='USB0::2665::2110::636002001440::0::INSTR',
  )
  eload = build.build_instrument(builder.Eload.CHROMA_63600)

  try:
    eload.set_current_dynamic(1, 0.1, 2, 0.1, 0.5, 2, 0.1, 10)
    eload.enable_output(1, True)
  finally:
    eload.close()


if __name__ == '__main__':
  main()
