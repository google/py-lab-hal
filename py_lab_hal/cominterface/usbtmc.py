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

"""USB TMC implementation for usb comm interface."""

import io
import logging

from py_lab_hal.cominterface.usb import Usb
import usb
import usbtmc


def connect(out_put_string: io.StringIO, resources_id: str) -> None:
  """Connect the USBTMC device and ask IDN."""

  out_put_string.write(f'\n{resources_id}\n')

  usb_inst = usbtmc.Instrument(resources_id)
  try:
    out_put_string.write(f'{usb_inst.ask("*IDN?")}\n')
  except usb.core.USBError:
    out_put_string.write('Unknown Devices\n')


def build_resources_id(resources: usb.core.Device) -> str:
  resources_id = f'USB::{resources.idVendor}::{resources.idProduct}::'

  if resources.serial_number:
    resources_id += f'{resources.serial_number}::'

  resources_id += 'INSTR'

  return resources_id


def list_resources(out_put_string: io.StringIO, is_win: bool = False) -> None:
  """List resource strings for all connected USBTMC devices."""
  del is_win

  out_put_string.write('-----USB-----\n')

  res = usbtmc.list_devices()
  for item in res:
    connect(out_put_string, build_resources_id(item))


class Usbtmc(Usb):
  """Child ComInterfaceClass Module of USB."""

  _inst: usbtmc.Instrument

  def _open(self) -> None:
    logging.info(
        'Connecting to instrument on %s',
        self.connect_config.visa_resource,
    )
    self._inst = usbtmc.Instrument(
        self.connect_config.visa_resource,
    )

  def _close(self) -> None:
    self._inst.close()

  def _send(self, data: bytes) -> None:
    self._inst.write_raw(data)

  def _recv(self, size) -> bytes:
    return self._inst.read_raw(size)

  def _query(self, data, size) -> bytes:
    return self._inst.ask_raw(data, size)

  def _set_timeout(self, seconds: int) -> None:
    self._inst.timeout = seconds
