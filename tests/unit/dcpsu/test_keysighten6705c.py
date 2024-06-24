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

"""Keysight N6705C Unit Test."""

from py_lab_hal import builder
from py_lab_hal.cominterface import cominterface
from py_lab_hal.cominterface import debug
from py_lab_hal.instrument import instrument
import pytest


class TestKeysightn6705c:
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

    TestKeysightn6705c.instrument = build.build_instrument(
        builder.DCPowerSupply.KEYSIGHT_N6705C
    )
    TestKeysightn6705c.instrument.open_instrument()
    TestKeysightn6705c.com = TestKeysightn6705c.instrument.inst
    yield

  @pytest.mark.parametrize('channel, enable', [(1, True), (1, False)])
  def test_set_OCP(self, channel, enable) -> None:
    self.instrument.enable_OCP(channel, enable)
    ans = f'SOUR:CURR:PROT:STAT {int(enable)}, (@{channel})'.encode()
    assert self.com.get_send_queue() == ans

  @pytest.mark.parametrize('channel, enable', [(1, True), (1, False)])
  def test_set_OVP(self, channel, enable) -> None:
    self.instrument.enable_OVP(channel, enable)
    ans = f'SOUR:VOLT:PROT:STAT {int(enable)}, (@{channel})'.encode()
    assert self.com.get_send_queue() == ans

  @pytest.mark.parametrize(
      'mode, expected',
      [
          (instrument.ChannelMode.CURRENT_DC, 'CURRent:DC'),
          (instrument.ChannelMode.VOLTAGE_DC, 'VOLTage:DC'),
      ],
  )
  def test_set_range(self, mode, expected) -> None:
    self.instrument.set_range(1, mode, 1)
    ans = f'SOUR:{expected}:RANG 1,(@1)'
    assert self.com.get_send_queue() == ans.encode()

  # def enable_remote_sense(self, enable: bool):
  #   pass

  # def set_NPLC(self, channel, power_line_freq, nplc):
  #   pass

  def test_measure_current(self) -> None:
    self.com.push_recv_queue(b'10')
    recv = self.instrument.measure_current(1)
    ans = b'measure:scalar:current? (@1)'
    assert self.com.get_send_queue() == ans
    assert 10 == recv

  def test_measure_voltage(self) -> None:
    self.com.push_recv_queue(b'10')
    recv = self.instrument.measure_voltage(1)
    ans = b'measure:scalar:voltage? (@1)'
    assert self.com.get_send_queue() == ans
    assert 10 == recv

  def test_measure_power(self) -> None:
    self.com.push_recv_queue(b'10')
    self.com.push_recv_queue(b'1')
    recv = self.instrument.measure_power(1)
    ans = b'measure:scalar:power? (@1)'
    assert self.com.get_send_queue() == ans
    assert 10 == recv

  def test_set_output(self) -> None:
    self.instrument.set_output(1, 1, 1)
    ans = b'SOUR:CURRent:DC 1,(@1)'
    assert self.com.get_send_queue() == ans
    ans = b'SOUR:VOLTage:DC 1,(@1)'
    assert self.com.get_send_queue() == ans

  def test_enable_output(self) -> None:
    self.instrument.enable_output(1, 1)
    ans = b'OUTP:STATE 1,(@1)'
    assert self.com.get_send_queue() == ans

    self.instrument.enable_output(1, 0)
    ans = b'OUTP:STATE 0,(@1)'
    assert self.com.get_send_queue() == ans
