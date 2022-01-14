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

"""Child RemotePowerSwitch Module of DigipduZdhx."""

import enum

from py_lab_hal.cominterface import cominterface
from py_lab_hal.cominterface import http
from py_lab_hal.cominterface import serial
from py_lab_hal.datagram import datagram
from py_lab_hal.instrument import instrument
from py_lab_hal.instrument.remote_power_switch import remote_power_switch

COMMAND_HEADER = 0x04


class STATE(enum.IntEnum):
  """The output state."""

  ON = 1
  OFF = 2


def crc(channel: int, state: STATE) -> int:
  """Calculate CRC of the command.

  The CRC here is make sure the sum of the command is 0xFF.

  Args:
    channel (int): The specified output channel.
    state (STATE): The specified output state.

  Returns:
    int: The CRC of the command.
  """
  return 0xFF - COMMAND_HEADER - channel - state


def prepare_serial_command(channel: int, state: STATE) -> bytes:
  """Prepare the serial command.

  Args:
    channel (int): The specified output channel.
    state (STATE): The specified output state.

  Returns:
    bytes: The serial command.
  """
  return bytes.fromhex(
      f'{COMMAND_HEADER:02X} {channel:02X} {state:02X} {crc(channel, state):02X}'
  )


class DigipduZdhx(remote_power_switch.RemotePowerSwitch):
  """Child relay Class of DigipduZdhx."""

  def __init__(
      self,
      com: cominterface.ComInterfaceClass,
      inst_config: instrument.InstrumentConfig,
  ) -> None:
    com.connect_config.http_config.auth_url = (
        f'{com.connect_config.http_config.url}/login_auth.csp'
    )
    com.connect_config.http_config.auth_mode = 'post'
    com.connect_config.http_config.auth_data = {
        'auth_user': com.connect_config.http_config.login,
        'auth_passwd': com.connect_config.http_config.password,
    }
    super().__init__(com, inst_config)

  def enable(self, channel, enable):
    if enable:
      state = STATE.ON
    else:
      state = STATE.OFF

    if isinstance(self.inst, serial.Serial):
      msg = prepare_serial_command(channel, state)
      self.data_handler.send_raw(msg)
    elif isinstance(self.inst, http.Http):
      self.inst.auth()
      url = self.inst.connect_config.http_config.url
      msg = f'http://{url}/out_ctrl.csp?port={channel}&ctrl_kind={state}'
      dg = datagram.HttpDatagram(url=msg, method='get')
      self.data_handler.send_dataram(dg)
    else:
      raise RuntimeError(
          'The selected interface:'
          f' {self.inst.connect_config.interface_type} is not supported. Please'
          ' use serial or http'
      )
