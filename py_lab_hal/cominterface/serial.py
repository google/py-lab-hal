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

"""Child ComInterfaceClass Module of Serial."""

import io
import time

from py_lab_hal.cominterface import cominterface
import serial
from serial.tools import list_ports


def resources_name(port: str, is_win: bool):
  return f'ASRL{port[3:]}::INSTR\n' if is_win else f'{port}\n'


def list_resources(out_put_string: io.StringIO, is_win: bool = False):
  out_put_string.write('\n-----Serial-----\n')
  for port, desc, hwid in list_ports.comports():
    out_put_string.write(resources_name(port, is_win))
    out_put_string.write(f'{desc} {hwid}\n')


class Serial(cominterface.ComInterfaceClass):
  """Serial instrument interface client."""

  _serial: serial.Serial

  def _open(self) -> None:
    self.connect_config.interface_type = 'serial'

    control_flow = list(
        format(self.connect_config.serial_config.flow_control, '03b')
    )
    str_to_bool = lambda x: x == '1'
    dsrdtr, rtscts, xonxoff = tuple(map(str_to_bool, control_flow))

    self._serial = serial.Serial(
        port=self.connect_config.visa_resource,
        baudrate=self.connect_config.serial_config.baud_rate,
        bytesize=self.connect_config.serial_config.data_bits,
        parity=self.connect_config.serial_config.parity.value,
        stopbits=self.connect_config.serial_config.stop_bits.value,
        xonxoff=xonxoff,
        rtscts=rtscts,
        dsrdtr=dsrdtr,
    )

  def _close(self) -> None:
    self._serial.close()

  def _send(self, data: bytes) -> None:
    self._serial.write(data)

    if self._serial.dsrdtr:
      time.sleep(0.1)
      while not self._serial.dsr:
        time.sleep(0.01)

  def _recv(self, size) -> bytes:
    end_term = self.connect_config.terminator.read.encode()
    while True:
      if size > 0:
        if len(self.buf) >= size:
          return bytes(self.buf.get(size))
      else:
        ans = self.buf.search(end_term)
        if ans is not None:
          return bytes(ans)
      self.buf.put(self._serial.read())

  def _query(self, data, size) -> bytes:
    self.send_raw(data)
    return self.recv_raw(size)

  def _set_timeout(self, seconds) -> None:
    self._serial.timeout = seconds
