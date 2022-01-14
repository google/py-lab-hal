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

"""Py-Lab-Hal usb communication interface for Monsoon power minotor."""

import io
import logging
import os

from Monsoon import HVPM
from Monsoon import LVPM
from Monsoon import pmapi
from Monsoon import sampleEngine
from py_lab_hal.cominterface import cominterface
from py_lab_hal.cominterface import usb
from py_lab_hal.util import util


class MonsoonUsbProtocol(util.PyLabHalEnum):
  CPP_BACKEND = pmapi.CPP_Backend_Protocol
  USB_BACKEND = pmapi.USB_protocol


class MonsoonDeviceType(util.PyLabHalEnum):
  HIGH_VOLTAGE = HVPM
  LOW_VOLTAGE = LVPM


def list_resources(out_put_string: io.StringIO, is_win: bool = False):
  del is_win
  monsoon_protocol = pmapi.USB_protocol()
  out_put_string.write('\n-----Monsoon-----\n')
  if monsoon_protocol.enumerateDevices():
    out_put_string.write('Detected\n')


class Usbmonsoon(usb.Usb):
  """This is the interface for Monsoon Devices with USB."""

  def __init__(self, connect_config: cominterface.ConnectConfig):
    self.device_type: MonsoonDeviceType = MonsoonDeviceType.HIGH_VOLTAGE
    self.protocol: MonsoonUsbProtocol = MonsoonUsbProtocol.USB_BACKEND
    self.monitor = None
    self.engine = None
    super().__init__(connect_config)

  def _open(self) -> None:
    assert isinstance(
        self.connect_config.usb_config.device_type, MonsoonDeviceType
    )
    assert isinstance(
        self.connect_config.usb_config.protocol, MonsoonUsbProtocol
    )
    self.device_type = MonsoonDeviceType.get(
        self.connect_config.usb_config.device_type
    )
    self.protocol = MonsoonUsbProtocol.get(
        self.connect_config.usb_config.protocol
    )
    if os.name == 'darwin' and self.protocol == MonsoonUsbProtocol.CPP_BACKEND:
      logging.warning('Monsoon CPP backend may not work as expected on MAC os')

    self.monitor = self.device_type.Monsoon()
    self.monitor.protocol = self.protocol()

    if not self.is_connected(self.connect_config.usb_config.serial_id):
      raise RuntimeError('Monsoon device not connected')
    self.monitor.setup_usb(serialno=self.connect_config.usb_config.serial_id)
    self.engine = sampleEngine.SampleEngine(self.monitor)

  def _close(self) -> None:
    if self._is_open():
      self.monitor.closeDevice()

  def is_connected(self, serial):
    """Checks if monsoon with given serial is attached to Py-Lab-Hal host."""

    if self.monitor and self.monitor.protocol:
      devices = self.monitor.protocol.enumerateDevices()
      return serial in devices if serial else bool(devices)
    return False

  def _is_open(self):
    """Checks monsoon power monitor is minitor in initialized once.

    Monsoon initializes monitor Protocol if it is opened. There is no other
    better way from monsoon to detect device is in opened state.

    Returns:
        (bool): True if the Protocol is open.
    """
    return self.monitor.Protocol is not None

  def _send(self, data) -> None:
    raise NotImplementedError()

  def _recv(self):
    raise NotImplementedError()

  def _query(self, data):
    raise NotImplementedError()

  def _set_timeout(self, seconds) -> None:
    pass

  def _send_data(self, data_g) -> None:
    raise NotImplementedError()

  def _recv_data(self):
    raise NotImplementedError()

  def _query_data(self, data_g):
    raise NotImplementedError()
