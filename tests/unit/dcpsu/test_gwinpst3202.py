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

"""GW Instek PST3202 Unit Test."""

from py_lab_hal import builder
from py_lab_hal.cominterface import cominterface
from py_lab_hal.cominterface import debug
import pytest


class TestGwinpst3202:
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

    TestGwinpst3202.instrument = build.build_instrument(
        builder.DCPowerSupply.GWIN_PST3202
    )
    TestGwinpst3202.instrument.open_instrument()
    TestGwinpst3202.com = TestGwinpst3202.instrument.inst
    yield

  @pytest.mark.parametrize('channel, enable', [(1, True), (1, False)])
  def test_enable_OCP(self, channel, enable) -> None:
    self.instrument.enable_OCP(channel, enable)
    ans = f'CHAN{channel}:PROTection:CURRent {int(enable)}'.encode()
    assert self.com.get_send_queue() == ans

  def test_enable_OVP(self) -> None:
    self.instrument.enable_OVP(1, True)

  def test_set_OVP_value(self) -> None:
    self.instrument.set_OVP_value(1, 100)
    ans = b'CHAN1:PROTection:VOLTage 100.00'
    assert self.com.get_send_queue() == ans

  # def set_range(self, channel, range_type, value):
  #   pass

  # def enable_remote_sense(self, enable: bool):
  #   pass

  # def set_NPLC(self, channel, power_line_freq, nplc):
  #   pass

  def test_measure_current(self) -> None:
    self.com.push_recv_queue(b'10')
    recv = self.instrument.measure_current(1)
    ans = b'CHAN1:MEAS:CURR?'
    assert self.com.get_send_queue() == ans
    assert 10 == recv

  def test_measure_voltage(self) -> None:
    self.com.push_recv_queue(b'10')
    recv = self.instrument.measure_voltage(1)
    ans = b'CHAN1:MEAS:VOLT?'
    assert self.com.get_send_queue() == ans
    assert 10 == recv

  def test_measure_power(self):
    self.com.push_recv_queue(b'10')
    self.com.push_recv_queue(b'10')
    recv = self.instrument.measure_power(1)
    ans = b'CHAN1:MEAS:CURR?'
    assert self.com.get_send_queue() == ans
    ans = b'CHAN1:MEAS:VOLT?'
    assert self.com.get_send_queue() == ans
    assert 100 == recv

  def test_set_output(self):
    self.instrument.set_output(1, 1, 1)
    ans = b'CHAN1:CURR 1.00'
    assert self.com.get_send_queue() == ans
    ans = b'CHAN1:VOLT 1.00'
    assert self.com.get_send_queue() == ans

  @pytest.mark.parametrize('channel, enable', [(1, True), (1, False)])
  def test_enable_output(self, channel, enable):
    self.instrument.enable_output(channel, enable)
    ans = f'OUTP:STATE {int(enable)}'.encode()
    assert self.com.get_send_queue() == ans
