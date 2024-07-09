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
import ifcfg
from py_lab_hal.cominterface import cominterface
import vxi11


def vxi_connect(out_put_string: io.StringIO, resources: str) -> None:
  """Connect the VXI-11 device and ask IDN."""

  out_put_string.write(f'\n{resources}\n')
  vxi_inst = vxi11.Instrument(resources)
  try:
    out_put_string.write(f'{vxi_inst.ask("*IDN?")}\n')
  except vxi11.vxi11.Vxi11Exception:
    out_put_string.write('Unknown Devices\n')


def list_resources(out_put_string: io.StringIO, is_win: bool = False) -> None:
  """List resource strings for all detected VXI-11 devices."""
  del is_win

  out_put_string.write('\n-----VXI-----\n')

  for name, interface in ifcfg.interfaces().items():
    for addr in interface['broadcasts']:
      if addr:
        out_put_string.write(f'Send Scan on {name}, {addr}\n')
        res = vxi11.list_devices(ip=addr)
        for item in res:
          vxi_connect(out_put_string, item)


class Vxi11(cominterface.ComInterfaceClass):
  """Child ComInterfaceClass Module of visa."""

  _inst: vxi11.Instrument

  def _open(self) -> None:
    self.connect_config.interface_type = 'vxi11'
    logging.info(
        'Connecting to instrument on %s',
        self.connect_config.visa_resource,
    )
    self._inst = vxi11.Instrument(
        self.connect_config.visa_resource,
    )

  def _close(self) -> None:
    self._inst.close()

  def _send(self, data: bytes) -> None:
    self._inst.write_raw(data)

  def _recv(self, size) -> bytes:
    return self._inst.read_raw(size)

  def _query(self, data: bytes, size) -> bytes:
    return self._inst.ask_raw(data, size)

  def _set_timeout(self, seconds: int) -> None:
    self._inst.timeout = seconds
