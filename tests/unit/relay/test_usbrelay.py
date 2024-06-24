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

"""USB Relay Unit Test."""

from py_lab_hal import builder
from py_lab_hal.cominterface import cominterface
from py_lab_hal.cominterface import debug
import pytest


class TestUsbrelay:
  com: debug.Debug

  @pytest.fixture(scope='function', autouse=True)
  def setup_thermal_f(self):
    self.com.clean_send_queue()
    yield

  @pytest.fixture(scope='class', autouse=True)
  def setup_thermal(self):
    build = builder.PyLabHALBuilder()
    build.connection_config = cominterface.ConnectConfig(interface_type='debug')
    build.instrument_config.clear = False
    build.instrument_config.reset = False
    build.instrument_config.idn = False
    TestUsbrelay.instrument = build.build_instrument(builder.Relay.USBRELAY)
    TestUsbrelay.com = TestUsbrelay.instrument.inst
    yield

  def test_set_channel_position(self):
    self.instrument.enable(1, True)
    ans = b'\xa0\x01\x01\xa2'
    assert self.com.get_send_queue() == ans

    self.instrument.enable(1, False)
    ans = b'\xa0\x01\x00\xa1'
    assert self.com.get_send_queue() == ans
