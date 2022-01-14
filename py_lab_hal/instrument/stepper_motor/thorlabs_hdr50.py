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

"""Child StepperMotor Class of ThorlabsHdr50."""

from __future__ import annotations

import struct

from py_lab_hal.instrument.stepper_motor import stepper_motor
from py_lab_hal.util import util

HOST_ADDRESS = 0x01
CHANNEL_ADDRESS_PREFIX = 0x20

MSG_HW_NO_FLASH_PROGRAMMING = 0x0018
MSG_MOD_SET_CHANENABLESTATE = 0x0210

MSG_MOT_SET_VELPARAMS = 0x0413
MSG_MOT_SET_JOGPARAMS = 0x0416

MSG_MOT_MOVE_HOME = 0x0443
MSG_MOT_MOVE_HOMED = 0x0444

MSG_MOT_SET_MOVEABSPARAMS = 0x0450
MSG_MOT_MOVE_ABSOLUTE = 0x0453

MSG_MOT_MOVE_COMPLETED = 0x0464
MSG_MOT_MOVE_STOP = 0x0465
MSG_MOT_MOVE_JOG = 0x046A


def _channel_map_dest(channel: int):
  return channel + CHANNEL_ADDRESS_PREFIX


class ThorlabsHdr50(stepper_motor.StepperMotor):
  """Child StepperMotor Class of ThorlabsHdr50."""

  MICRO_STEPS = 409600
  GEAR_RATIO = 66

  JOG_DIR = {
      'FOR': 1,
      'REV': 2,
  }
  STOP_MODE = {
      'IMM': 1,
      'CON': 2,
  }
  JOG_MODE = {
      'CON': 1,
      'SIN': 2,
  }
  _UINT_RATIO = {
      'POS': 1.0,
      'VEL': 50.68,
      'ACC': 1 / 90.9,
  }

  def _pack_command(
      self,
      mesg_id: int,
      dest: int,
      source: int = HOST_ADDRESS,
      param1: int = 0,
      param2: int = 0,
      data: bytes | None = None,
      with_data: bool = True,
  ) -> bytes:
    if data is None:
      return struct.pack('<H2b2B', mesg_id, param1, param2, dest, source)

    header = struct.pack('<HHBB', mesg_id, len(data), dest | 0x80, source)
    if with_data:
      return header + data
    return header

  def _deg_to_unit(self, deg: float, unit: str = 'POS') -> int:
    unit_factor = util.get_from_dict(self._UINT_RATIO, unit)
    return int(deg / 360 * self.MICRO_STEPS * self.GEAR_RATIO * unit_factor)

  def _wait_for_command(self, cmd: bytes) -> None:
    idx = 0
    ans = b''
    while True:
      recv = self.data_handler.recv_raw()
      count = 0
      while count < len(recv):
        if recv[count] == cmd[idx]:
          idx += 1
          ans += bytes([recv[count]])
        else:
          idx = 0
          ans = b''
        count += 1
      if ans == cmd:
        break

  def _send_command(
      self,
      mesg_id: int,
      dest: int,
      source: int = HOST_ADDRESS,
      param1: int = 0,
      param2: int = 0,
      data: bytes | None = None,
      with_data: bool = True,
  ):
    command = self._pack_command(
        mesg_id,
        dest,
        source,
        param1,
        param2,
        data,
        with_data,
    )
    self.data_handler.send_raw(command)

  def home(self, channel) -> None:
    self._send_command(
        MSG_MOT_MOVE_HOME, _channel_map_dest(channel), param1=channel
    )
    self.homed(channel)

  def homed(self, channel):
    command = self._pack_command(
        MSG_MOT_MOVE_HOMED,
        HOST_ADDRESS,
        _channel_map_dest(channel),
        param1=channel,
    )
    self._wait_for_command(command)

  def stop(self, channel, stop_mode) -> None:
    stop_m = util.get_from_dict(self.STOP_MODE, stop_mode)
    self._send_command(
        MSG_MOT_MOVE_STOP,
        _channel_map_dest(channel),
        param1=channel,
        param2=stop_m,
    )

  def move_completed(self, channel):
    dummy_len14_data = b'0' * 14
    command = self._pack_command(
        MSG_MOT_MOVE_COMPLETED,
        HOST_ADDRESS,
        _channel_map_dest(channel),
        data=dummy_len14_data,
        with_data=False,
    )
    self._wait_for_command(command)

  def set_vel(self, channel, acceleration, max_velocity) -> None:
    min_vel = 0
    data = struct.pack(
        '<H3l',
        channel,
        self._deg_to_unit(min_vel, 'VEL'),
        self._deg_to_unit(acceleration, 'ACC'),
        self._deg_to_unit(max_velocity, 'VEL'),
    )
    self._send_command(
        MSG_MOT_SET_VELPARAMS, _channel_map_dest(channel), data=data
    )

  def set_move_abs(self, channel, absolute_position) -> None:
    data = struct.pack('<Hl', channel, self._deg_to_unit(absolute_position))
    self._send_command(
        MSG_MOT_SET_MOVEABSPARAMS, _channel_map_dest(channel), data=data
    )

  def move_absolute(self, channel) -> None:
    self._send_command(
        MSG_MOT_MOVE_ABSOLUTE, _channel_map_dest(channel), param1=channel
    )
    self.move_completed(channel)

  def set_jog(
      self,
      channel,
      jog_mode,
      step_size,
      acceleration,
      max_velocity,
      stop_mode,
  ) -> None:
    jog_m = util.get_from_dict(self.JOG_MODE, jog_mode)
    stop_m = util.get_from_dict(self.STOP_MODE, stop_mode)
    min_velocity = 0
    data = struct.pack(
        '<HH4lH',
        channel,
        jog_m,
        self._deg_to_unit(step_size),
        self._deg_to_unit(min_velocity, 'VEL'),
        self._deg_to_unit(acceleration, 'ACC'),
        self._deg_to_unit(max_velocity, 'VEL'),
        stop_m,
    )
    self._send_command(
        MSG_MOT_SET_JOGPARAMS, _channel_map_dest(channel), data=data
    )

  def move_jog(self, channel, direction) -> None:
    dire = util.get_from_dict(self.JOG_DIR, direction)
    self._send_command(
        MSG_MOT_MOVE_JOG,
        _channel_map_dest(channel),
        param1=channel,
        param2=dire,
    )
    self.move_completed(channel)

  def set_channel(self, channel: int) -> None:
    self._send_command(MSG_HW_NO_FLASH_PROGRAMMING, _channel_map_dest(channel))
    enable = 0x01
    self._send_command(
        MSG_MOD_SET_CHANENABLESTATE,
        _channel_map_dest(channel),
        param1=channel,
        param2=enable,
    )
    self.set_vel(channel, 25, 50)
