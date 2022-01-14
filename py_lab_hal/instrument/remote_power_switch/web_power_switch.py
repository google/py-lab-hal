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

"""Child RemotePowerSwitch of WebPowerSwitch."""

import time
from py_lab_hal.cominterface import cominterface
from py_lab_hal.datagram import datagram
from py_lab_hal.instrument import instrument
from py_lab_hal.instrument.remote_power_switch import remote_power_switch


class WebPowerSwitch(remote_power_switch.RemotePowerSwitch):
  """Child relay Class of WebPowerSwitch."""

  def __init__(
      self,
      com: cominterface.ComInterfaceClass,
      inst_config: instrument.InstrumentConfig,
  ) -> None:
    com.connect_config.http_config.http_auth_mode = 'HTTPDigestAuth'
    super().__init__(com, inst_config)

  def enable(self, channel, enable):
    if enable:
      state = 'true'
    else:
      state = 'false'

    url = self.inst.connect_config.http_config.url
    msg = f'http://{url}/restapi/relay/outlets/{channel-1}/state/'
    dg = datagram.HttpDatagram(
        url=msg,
        headers_dict={'X-CSRF': 'x', 'Accept': 'application/json'},
        method='put',
        data={'value': state},
    )
    self.data_handler.send_dataram(dg)

    time.sleep(0.2)
