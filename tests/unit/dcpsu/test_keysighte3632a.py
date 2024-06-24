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

"""Keysight E3632A Unit Test."""

from py_lab_hal import builder
from py_lab_hal.cominterface import cominterface
from py_lab_hal.cominterface import debug
import pytest


class TestKeysighte3632a:
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

    TestKeysighte3632a.instrument = build.build_instrument(
        builder.DCPowerSupply.KEYSIGHT_E3632A
    )
    TestKeysighte3632a.instrument.open_instrument()
    TestKeysighte3632a.com = TestKeysighte3632a.instrument.inst
    yield

  @pytest.mark.parametrize('channel, enable', [(1, True), (1, False)])
  def test_set_OCP(self, channel, enable) -> None:
    self.instrument.enable_OCP(channel, enable)
    ans = f'voltage:protection:state {int(enable)}'.encode()
    assert self.com.get_send_queue() == ans

  @pytest.mark.parametrize('channel, enable', [(1, True), (1, False)])
  def test_set_OVP(self, channel, enable) -> None:
    self.instrument.enable_OVP(channel, enable)
    ans = f'voltage:protection:state {int(enable)}'.encode()
    assert self.com.get_send_queue() == ans

  def test_set_OVP_value(self) -> None:
    self.instrument.set_OVP_value(1, 1)
    ans = b'voltage:protection 1'
    assert self.com.get_send_queue() == ans

  # def set_sequence(self, channel, voltage, current, delay):
  #   if len(voltage) != len(current):
  #     print('len error')
  #   if len(voltage) != len(delay):
  #     print('delay len error')

  #   for v, c, t in zip(voltage, current, delay):
  #     time.sleep(t)
  #     self.set_output(channel, v, c)

  # def set_range(self, channel, range_type, value):
  #   pass

  # def enable_remote_sense(self, enable: bool):
  #   pass

  # def set_NPLC(self, channel, power_line_freq, nplc):
  #   pass

  def test_measure_power(self) -> None:
    self.com.push_recv_queue(b'10')
    self.com.push_recv_queue(b'1')
    recv = self.instrument.measure_power(1)
    ans = b'measure:current?'
    assert self.com.get_send_queue() == ans
    ans = b'measure:voltage?'
    assert self.com.get_send_queue() == ans
    assert 10 == recv

  def test_measure_current(self) -> None:
    self.com.push_recv_queue(b'10')
    recv = self.instrument.measure_current(1)
    ans = b'measure:current?'
    assert self.com.get_send_queue() == ans
    assert 10 == recv

  def test_measure_voltage(self) -> None:
    self.com.push_recv_queue(b'10')
    recv = self.instrument.measure_voltage(1)
    ans = b'measure:voltage?'
    assert self.com.get_send_queue() == ans
    assert 10 == recv

  # def measure_power(self, channel) -> float:
  #   pass

  def test_set_output(self) -> None:
    self.instrument.set_output(1, 1, 1)
    ans = b'CURR 1'
    assert self.com.get_send_queue() == ans
    ans = b'VOLT 1'
    assert self.com.get_send_queue() == ans

  @pytest.mark.parametrize(
      'channel, enable, expected_bool', [(1, True, 'ON'), (1, False, 'OFF')]
  )
  def test_enable_output(self, channel, enable, expected_bool) -> None:
    self.instrument.enable_output(channel, enable)
    ans = f'OUTP {expected_bool}'.encode()
    assert self.com.get_send_queue() == ans

  @pytest.mark.parametrize('voltage', [1, 2])
  def test_set_output_voltage(self, voltage) -> None:
    self.instrument.set_output_voltage(1, voltage)
    ans = f'VOLT {voltage}'.encode()
    assert self.com.get_send_queue() == ans

  @pytest.mark.parametrize('current', [1, 2])
  def test_set_current_value(self, current) -> None:
    self.instrument.set_output_current(1, current)
    ans = f'CURR {current}'.encode()
    assert self.com.get_send_queue() == ans
