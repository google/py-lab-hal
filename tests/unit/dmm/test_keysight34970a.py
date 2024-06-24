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

"""Keysight 34970A Unit Test."""

from py_lab_hal import builder
from py_lab_hal.cominterface import cominterface
from py_lab_hal.cominterface import debug
import pytest


class TestKeysight34970a:
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
    build.instrument_config.auto_init = False

    TestKeysight34970a.instrument = build.build_instrument(
        builder.DMM.AGILENT_34410A
    )
    TestKeysight34970a.instrument.open_instrument()
    TestKeysight34970a.com = TestKeysight34970a.instrument.inst

  # def config_autozero(self, auto_zero_func, channel, enable: bool):
  #   pass

  # def config_measurement(self, channel, function, mea_range, abs_resolution):
  #   pass

  # def test_read(self):
  #   self.com.push_recv_queue(b'10')
  #   recv = self.instrument.read()
  #   ans = b':read?'
  #   assert self.com.get_send_queue() ==  ans
  #   assert 10 ==  recv
