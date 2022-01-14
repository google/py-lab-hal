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

"""Child Relay Module of Usbrelay."""

import time

from py_lab_hal.instrument.relay import relay

HEADER = 0xA0


def crc(channel: int, enable: bool):
  """Calculate CRC of the command.

  The CRC here is the sum of the command.

  Args:
    channel (int): The specified output channel.
    enable (bool): The specified output state.

  Returns:
    int: The CRC of the command.
  """
  return HEADER + channel + int(enable)


class Usbrelay(relay.Relay):
  """Child relay Class of Usbrelay."""

  def enable(self, channel, enable):
    message_bytes = bytes.fromhex(
        f'{HEADER:02X} {channel:02X} {int(enable):02X} {crc(channel, enable):02X}'
    )
    self.data_handler.send_raw(message_bytes)
    time.sleep(0.2)
