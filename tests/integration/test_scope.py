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

"""Preliminary Scope Unit Test."""

import os
import time
import unittest
from py_lab_hal import instrument
from py_lab_hal.cominterface import cominterface
from py_lab_hal.logger import Logger


class ScopeTestCase(unittest.TestCase):

  def setUp(self):
    self.scope_type = 'lecroyMAUI'
    cc = cominterface.ConnectConfig(
        visa_resource='USB0::0x05FF::0x1023::4068N53330::INSTR'
    )
    com = cominterface.select(connect_config=cc)
    self.scope = instrument.select('scope', self.scope_type, com)

  def tearDown(self):
    self.scope.close()

  def test_set_channel_position(self):
    if self.scope_type == 'lecroyMAUI':
      self.skipTest('lecroyMAUI do not support this function.')
    self.scope.set_channel_position(1, 2.34)
    self.scope.get_error_status()

  def test_set_channel_position_max(self):
    if self.scope_type == 'lecroyMAUI':
      self.skipTest('lecroyMAUI do not support this function.')
    self.scope.set_channel_position(1, 9)
    self.scope.get_error_status()

  def test_set_channel_position_min(self):
    if self.scope_type == 'lecroyMAUI':
      self.skipTest('lecroyMAUI do not support this function.')
    self.scope.set_channel_position(1, -9)
    self.scope.get_error_status()

  # TODO: b/333309357 - unskip after building the probe attenuation dict.
  @unittest.skip('Probe attenuation dictionary has not been builded')
  def test_set_channel_attenuation(self):
    self.scope.set_channel_attenuation(1, 10)
    self.scope.get_error_status()

  def test_set_channel_attenuation_out_range(self):
    self.scope.set_channel_attenuation(1, 2e5)

  def test_set_channel_coupling_dc(self):
    if self.scope_type == 'tektronixs4':
      self.scope.set_channel_coupling(1, 'DC')
    else:
      self.scope.set_channel_coupling(1, 'DC', 1e6)
    self.scope.get_error_status()

  def test_set_channel_coupling_ac(self):
    if self.scope_type == 'tektronixs4':
      self.scope.set_channel_coupling(1, 'AC')
    else:
      self.scope.set_channel_coupling(1, 'AC', 1e6)
    self.scope.get_error_status()

  def test_set_channel_offset(self):
    self.scope.set_channel_offset(1, 1.23)
    self.scope.get_error_status()

  def test_set_channel_division(self):
    self.scope.set_channel_division(1, 1.23)
    self.scope.get_error_status()

  def test_set_channel_on(self):
    self.scope.set_channel_on_off(1, True)
    self.scope.get_error_status()

  def test_set_channel_off(self):
    self.scope.set_channel_on_off(1, False)
    self.scope.get_error_status()

  def test_set_channel_bandwidth_on(self):
    self.scope.set_channel_bandwidth(1, 20e6, True)
    self.scope.get_error_status()

  def test_set_channel_bandwidth_off(self):
    self.scope.set_channel_bandwidth(1, 20e6, False)
    self.scope.get_error_status()

  def test_set_channel_bandwidth_out_range(self):
    self.scope.set_channel_bandwidth(1, 30e6, True)
    self.scope.get_error_status()

  def test_set_channel_labels(self):
    channel = 1
    expected = 'Kok Hua, Mike'
    self.scope.set_channel_labels(channel, expected)
    result = self.scope.get_channel_labels(channel)
    assert expected == result

  def test_set_channel_labels_list(self):
    channel = [1, 2]
    expected = ['Kok Hua, Mike', 'James, Charlie']
    self.scope.set_channel_labels(channel, expected)
    result = self.scope.get_channel_labels(channel)
    assert expected == result

  def test_set_channel_labels_position(self):
    self.scope.set_channel_labels_position(1, 1.23, 2.34)
    self.scope.get_error_status()

  def test_config_edge_trigger(self):
    self.scope.config_edge_trigger(1, 0.5, 'FALL', 'DC')
    self.scope.get_error_status()

  def test_set_aux_trigger_on(self):
    self.scope.set_aux_trigger(True)
    self.scope.get_error_status()

  def test_set_aux_trigger_off(self):
    self.scope.set_aux_trigger(False)
    self.scope.get_error_status()

  def test_config_continuous_acquisition_true_true(self):
    self.scope.config_continuous_acquisition(True, True)
    self.scope.get_error_status()

  def test_config_continuous_acquisition_true_false(self):
    self.scope.config_continuous_acquisition(True, False)
    self.scope.get_error_status()

  def test_config_continuous_acquisition_false(self):
    self.scope.config_continuous_acquisition(False, True)
    self.scope.get_error_status()

  def test_config_rolling_mode(self):
    self.scope.config_rolling_mode(True)

  def test_config_pulse_width_trigger_less(self):
    self.scope.config_pulse_width_trigger(1, 'LESS', 'NEG', 0.1, 1.3, 2.5)
    self.scope.get_error_status()

  def test_config_pulse_width_trigger_more(self):
    self.scope.config_pulse_width_trigger(1, 'MORE', 'POS', 0.1, 1.3, 2.5)
    self.scope.get_error_status()

  def test_config_pulse_width_trigger_within(self):
    self.scope.config_pulse_width_trigger(1, 'WITHIN', 'NEG', 0.1, 1.3, 2.5)
    self.scope.get_error_status()

  def test_config_pulse_width_trigger_out(self):
    self.scope.config_pulse_width_trigger(1, 'OUT', 'NEG', 0.1, 1.3, 2.5)
    self.scope.get_error_status()

  def test_set_horiz_division_samplesize(self):
    self.scope.set_horiz_division(25, -1, 3.125e7, 'samplesize')
    self.scope.get_error_status()

  def test_set_horiz_division_samplesize_out_range(self):
    self.scope.set_horiz_division(25, -1, 2.6e6, 'samplesize')
    self.scope.get_error_status()

  def test_set_horiz_division_samplerate(self):
    self.scope.set_horiz_division(2.5, -2, 1.25e6, 'samplerate')
    self.scope.get_error_status()

  def test_set_horiz_division_samplerate_out_range(self):
    self.scope.set_horiz_division(2.5, -2, 2.6e6, 'samplerate')
    self.scope.get_error_status()

  def test_set_horiz_division_samplerate_missing_parameter(self):
    self.scope.set_horiz_division(2.5, -2, 2.6e6)
    self.scope.get_error_status()

  def test_set_horiz_offset(self):
    self.scope.set_horiz_offset(87)
    self.scope.get_error_status()

  def test_set_measurement_reference(self):
    self.scope.set_measurement_reference(12, 55, 87)
    self.scope.get_error_status()

  def test_set_measurement_on(self):
    self.scope.set_measurement_on_off(1, True)
    self.scope.get_error_status()

  def test_set_measurement_on_mix(self):
    self.scope.set_measurement_on_off([1, 2], [True, False])
    self.scope.get_error_status()

  def test_set_measurement_off(self):
    self.scope.set_measurement_on_off(1, False)
    self.scope.get_error_status()

  def test_set_measurement_statistics_on(self):
    self.scope.set_measurement_statistics(True)
    self.scope.get_error_status()

  def test_set_measurement_statistics_off(self):
    self.scope.set_measurement_statistics(False)
    self.scope.get_error_status()

  def test_set_measurement_risetime(self):
    # need probe to calabrate
    channel = 1
    measure_number = 2
    measurement_type = 'risetime'
    self.scope.auto_set()
    self.scope.set_measurement(channel, measure_number, measurement_type)
    self.scope.config_continuous_acquisition(False, False)
    time.sleep(1)
    expected = round(
        self.scope.fetch_measurement(channel, measurement_type), 10
    )
    result = round(self.scope.fetch_measure_number(measure_number), 10)
    assert expected == result

  def test_set_measurement_falltime(self):
    # need probe to calabrate
    channel = 1
    measure_number = 2
    measurement_type = 'falltime'
    self.scope.auto_set()
    self.scope.config_continuous_acquisition(False, False)
    time.sleep(1)
    self.scope.set_measurement(channel, measure_number, measurement_type)
    expected = round(
        self.scope.fetch_measurement(channel, measurement_type), 10
    )
    result = round(self.scope.fetch_measure_number(measure_number), 10)
    assert expected == result

  def test_set_measurement_pulsewidth(self):
    # need probe to calabrate
    channel = 1
    measure_number = 2
    measurement_type = 'pulsewidthpositive'
    self.scope.config_continuous_acquisition(False, False)
    self.scope.set_measurement(channel, measure_number, measurement_type)
    expected = round(self.scope.fetch_measurement(channel, measurement_type), 3)
    result = round(self.scope.fetch_measure_number(measure_number), 3)
    assert expected == result

  def test_set_measurement_risingedgecount(self):
    # need probe to calabrate
    if self.scope_type == 'tektronixs4':
      self.skipTest('tektronixs4 do not support this function.')
    channel = 1
    measure_number = 2
    measurement_type = 'risingedgecount'
    self.scope.set_measurement(channel, measure_number, measurement_type)
    expected = round(self.scope.fetch_measurement(channel, measurement_type), 3)
    result = round(self.scope.fetch_measure_number(measure_number), 3)
    assert expected == result

  def test_set_measurement_dutycyclepositive(self):
    # need probe to calabrate
    channel = 1
    measure_number = 2
    measurement_type = 'dutycyclepositive'
    self.scope.auto_set()
    self.scope.config_continuous_acquisition(False, False)
    self.scope.set_measurement(channel, measure_number, measurement_type)
    expected = round(self.scope.fetch_measurement(channel, measurement_type), 3)
    result = round(self.scope.fetch_measure_number(measure_number), 3)
    assert expected == result

  def test_set_measurement_average(self):
    # need probe to calabrate
    channel = 1
    measure_number = 2
    measurement_type = 'average'
    self.scope.set_measurement(channel, measure_number, measurement_type)
    self.scope.auto_set()
    self.scope.config_continuous_acquisition(False, False)
    time.sleep(1)
    expected = round(self.scope.fetch_measurement(channel, measurement_type), 3)
    result = round(self.scope.fetch_measure_number(measure_number), 3)
    assert expected == result

  def test_set_delta_measurement(self):
    # need probe to calabrate
    measure_number = 4
    self.scope.set_measurement_reference(10, 50, 90)
    self.scope.set_delta_measurement(measure_number, 1, 2, 'RAISE', 'RAISE')
    self.scope.set_horiz_division(0.001)
    self.scope.set_channel_division([1, 2], 1)
    self.scope.config_continuous_acquisition(False, False)
    time.sleep(4)
    result = round(self.scope.fetch_measure_number(measure_number), 10)
    expected = round(
        self.scope.fetch_delta_measurement(1, 2, 'RAISE', 'RAISE', 50, 50), 10
    )
    assert expected == result

  def test_set_cursor_hor(self):
    self.scope.set_cursor(1, 'HOR', -5, 7)
    self.scope.get_error_status()

  def test_set_cursor_ver(self):
    self.scope.set_cursor(1, 'VER', -5, 7)
    self.scope.get_error_status()

  def test_set_infinite_persistence_on(self):
    self.scope.set_infinite_persistence(True)
    self.scope.get_error_status()

  def test_set_infinite_persistence_off(self):
    self.scope.set_infinite_persistence(False)
    self.scope.get_error_status()

  def test_clear_persistence(self):
    self.scope.clear_persistence()
    self.scope.get_error_status()

  def test_wait_acquisition_complete(self):
    self.scope.wait_acquisition_complete(1)

  def test_get_acquisition(self):
    self.scope.get_acquisition()
    self.scope.get_error_status()

  def test_arm_single_trig(self):
    self.scope.arm_single_trig()
    self.scope.get_error_status()

  def test_stop_acquisition(self):
    self.scope.stop_acquisition()
    self.scope.get_error_status()

  def test_start_acquisition(self):
    self.scope.start_acquisition()
    self.scope.get_error_status()

  def test_reset_measurement_statistics(self):
    self.scope.reset_measurement_statistics()
    self.scope.set_measurement(1, 1, 'AMPLITUDE')
    result = self.scope.get_measurement_statistics(1)['count']
    self.assertTrue(result <= 1)

  def test_wait_task(self):
    self.scope.wait_task(1)
    self.scope.get_error_status()

  def test_wait_trigger_ready(self):
    self.scope.wait_trigger_ready(1)
    self.scope.get_error_status()

  def test_fetch_waveform(self):
    self.scope.fetch_waveform(1)
    self.scope.get_error_status()

  # TODO: b/333309362 - unskip after this function completes.
  @unittest.skip('Function not complete')
  def test_load_settings_file(self):
    self.scope.load_settings_file('HahaThisIsPath')
    self.scope.get_error_status()
    os.remove('HahaThisIsPath')

  def test_save_settings_file(self):
    self.scope.save_settings_file('HahaThisIsPath')
    self.scope.get_error_status()
    os.remove('HahaThisIsPath')

  def test_get_screenshot(self):
    self.scope.get_screenshot('HahaThisIsPath')
    self.scope.get_error_status()


if __name__ == '__main__':
  Logger.set_std_out(30)
  unittest.main()
