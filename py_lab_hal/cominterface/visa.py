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

"""Child ComInterfaceClass Module of visa."""

import io
import logging
import typing

from py_lab_hal.cominterface import cominterface
import pyvisa
from pyvisa.constants import InterfaceType


VI_ASRL_PAR_NONE = 0
VI_ASRL_PAR_ODD = 1
VI_ASRL_PAR_EVEN = 2
VI_ASRL_PAR_MARK = 3
VI_ASRL_PAR_SPACE = 4

VI_Parity = {
    'N': VI_ASRL_PAR_NONE,
    'E': VI_ASRL_PAR_EVEN,
    'O': VI_ASRL_PAR_ODD,
    'M': VI_ASRL_PAR_MARK,
    'S': VI_ASRL_PAR_MARK,
}


def list_resources(out_put_string: io.StringIO, is_win: bool = False):
  """Scan the instrument with pyvisa on Windows."""
  del is_win

  rm = pyvisa.ResourceManager()
  ins_list = rm.list_resources()

  out_put_string.write('\n-----VISA-----\n')
  out_put_string.write(f'{ins_list}\n')

  for ins in ins_list:
    out_put_string.write(f'{ins} ')
    try:
      with rm.open_resource(ins) as inst:
        out_put_string.write(f'{inst.query("*IDN?").strip()}\n')
        inst.close()
    except pyvisa.errors.VisaIOError:
      out_put_string.write('Unknown Devices\n')


class Visa(cominterface.ComInterfaceClass):
  """Child ComInterfaceClass Module of visa."""

  _inst: pyvisa.resources.MessageBasedResource

  def _open(self) -> None:
    self.connect_config.interface_type = 'visa'
    self.rm = pyvisa.ResourceManager('@ivi')
    logging.info(
        'Connecting to instrument on %s',
        self.connect_config.visa_resource,
    )
    self._inst = typing.cast(
        pyvisa.resources.MessageBasedResource,
        self.rm.open_resource(self.connect_config.visa_resource),
    )

    self._inst.read_termination = self.connect_config.terminator.read
    self._inst.write_termination = self.connect_config.terminator.write

    if self._inst.interface_type == InterfaceType.asrl:
      self._inst.baud_rate = self.connect_config.serial_config.baud_rate  # type: ignore
      self._inst.data_bits = self.connect_config.serial_config.data_bits  # type: ignore
      self._inst.stop_bits = int(self.connect_config.serial_config.stop_bits.value * 10)  # type: ignore
      self._inst.parity = VI_Parity[self.connect_config.serial_config.parity.value]  # type: ignore
      self._inst.flow_control = self.connect_config.serial_config.flow_control  # type: ignore

  def _close(self) -> None:
    self._inst.close()

  def _send(self, data: bytes) -> None:
    self._inst.write_raw(data)

  def _recv(self, size) -> bytes:
    if size < 0:
      return self._inst.read().encode()
    return self._inst.read_bytes(count=size, break_on_termchar=True).strip()

  def _query(self, data: bytes, size) -> bytes:
    self.send_raw(data)
    return self.recv_raw(size)

  def _set_timeout(self, seconds: int) -> None:
    self._inst.timeout = seconds * 1000
