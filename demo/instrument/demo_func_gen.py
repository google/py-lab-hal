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

"""Demo code for Function Gen."""

from py_lab_hal import builder
from py_lab_hal.cominterface import cominterface
from py_lab_hal.instrument import instrument


def main() -> None:
  build = builder.PyLabHALBuilder()
  build.connection_config = cominterface.ConnectConfig(
      visa_resource='USB::2391::11271::MY59000806::INSTR',
  )

  fg = build.build_instrument(builder.FunctionGenerator.KEYSIGHT_N33500B)

  try:
    fg.configure_output(
        1,
        instrument.FunctionType.SIN,
        1e3,
        5,
        2.5,
        0,
    )

    fg.set_output_function(2, instrument.FunctionType.SQU)
    fg.set_output_frequency(2, 1e4)
    fg.set_output_voltage(2, 5, 0)
    fg.set_output_phase(2, 90)

    fg.enable_output(1, True)
    fg.enable_output(2, True)
  finally:
    fg.close()


if __name__ == '__main__':
  main()
