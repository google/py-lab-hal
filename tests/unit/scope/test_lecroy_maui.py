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

"""Test of LecroyMAUI."""

import math
import os

from py_lab_hal import builder
from py_lab_hal.cominterface import cominterface
from py_lab_hal.cominterface import debug
from py_lab_hal.instrument import instrument
import pytest


class TestLecroyMAUI:
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

    TestLecroyMAUI.instrument = build.build_instrument(
        builder.Scope.LECROY_MAUI
    )
    TestLecroyMAUI.instrument.idn = 'LECROY,HDO6104A-MS,LCRY4068N53330,9.1.0'
    TestLecroyMAUI.instrument.open_instrument()
    TestLecroyMAUI.com = TestLecroyMAUI.instrument.inst
    yield

  def test_set_channel_position(self):
    with pytest.raises(NotImplementedError):
      self.instrument.set_channel_position(1, 1.23)

  def test_set_channel_attenuation(self):
    self.instrument.set_channel_attenuation(1, 10)
    expected = b'C1:ATTN 10'
    assert expected == self.com.get_send_queue()

  def test_set_channel_attenuation_out_range(self):
    self.instrument.set_channel_attenuation(1, 2e5)

  @pytest.mark.parametrize(
      'probe, mode, impedance, expect',
      [
          ('RI', instrument.ChannelCoupling.AC, 1e6, 'A1M'),
          ('ZD', instrument.ChannelCoupling.DC, 50, 'DC120k'),
      ],
  )
  def test_set_channel_coupling(self, probe, mode, impedance, expect):
    self.com.push_recv_queue(probe.encode())
    self.instrument.set_channel_coupling(1, mode, impedance)
    expected = b'C1:PRNA?'
    assert expected == self.com.get_send_queue()
    expected = f'C1:COUPLING {expect}'
    assert expected.encode() == self.com.get_send_queue()

  def test_set_channel_offset(self):
    self.instrument.set_channel_offset(1, 1.23)
    expected = b'C1:OFFSET -1.230'
    assert expected == self.com.get_send_queue()

  def test_set_channel_division(self):
    self.instrument.set_channel_division(1, 1.23)
    expected = b'C1:VDIV 1.230'
    assert expected == self.com.get_send_queue()

  def test_set_channel_on(self):
    self.instrument.set_channel_on_off(1, True)
    expected = b'C1:TRA ON'
    assert expected == self.com.get_send_queue()

  def test_set_channel_off(self):
    self.instrument.set_channel_on_off(1, False)
    expected = b'C1:TRA OFF'
    assert expected == self.com.get_send_queue()

  def test_set_channel_bandwidth_on(self):
    self.instrument.set_channel_bandwidth(1, 20e6, True)
    expected = b'BWL C1,20MHZ'
    assert expected == self.com.get_send_queue()

  def test_set_channel_bandwidth_off(self):
    self.instrument.set_channel_bandwidth(1, 20e6, False)
    expected = b'BWL C1,OFF'
    assert expected == self.com.get_send_queue()

  def test_set_channel_bandwidth_out_range(self):
    self.instrument.set_channel_bandwidth(1, 30e6, True)

  def test_set_channel_labels(self):
    self.instrument.set_channel_labels(1, 'Kok hua')
    expected = b"VBS 'app.Acquisition.C1.ViewLabels = True'"
    assert expected == self.com.get_send_queue()
    expected = b'VBS \'app.Acquisition.C1.LabelsText = "Kok hua"\''
    assert expected == self.com.get_send_queue()

  def test_set_channel_labels_position(self):
    self.instrument.set_channel_labels_position(1, 1.23, 2.34)
    expected = b'VBS \'app.Acquisition.C1.LabelsPosition = "1.23|2.34"\''
    assert expected == self.com.get_send_queue()

  def test_get_channel_labels(self):
    self.com.push_recv_queue(b'Label 1')
    recv = self.instrument.get_channel_labels(1)
    expected = b"VBS? 'return = app.Acquisition.C1.LabelsText'"
    assert expected == self.com.get_send_queue()
    assert 'Label 1' == recv

  def test_get_channel_labels_list(self):
    self.com.push_recv_queue(b'Jamse 1')
    recv = self.instrument.get_channel_labels(1)
    expected = b"VBS? 'return = app.Acquisition.C1.LabelsText'"
    assert expected == self.com.get_send_queue()
    expected = 'Jamse 1'
    assert expected == recv

  def test_config_edge_trigger(self):
    self.instrument.config_edge_trigger(
        1,
        0.5,
        instrument.EdgeTriggerSlope.FALL,
        instrument.EdgeTriggerCoupling.DC,
    )
    expected = b'C1:TRA ON'
    assert expected == self.com.get_send_queue()
    expected = b'TRSE EDGE,SR,C1'
    assert expected == self.com.get_send_queue()
    expected = b'C1:TRLV 0.5'
    assert expected == self.com.get_send_queue()
    expected = b'C1:TRSL NEG'
    assert expected == self.com.get_send_queue()
    expected = b'C1:TRCP DC'
    assert expected == self.com.get_send_queue()

  def test_set_aux_trigger_on(self):
    self.instrument.set_aux_trigger(True)
    expected = b'COUT TRIG'
    assert expected == self.com.get_send_queue()

  def test_set_aux_trigger_off(self):
    self.instrument.set_aux_trigger(False)
    expected = b'COUT OFF'
    assert expected == self.com.get_send_queue()

  def test_config_continuous_acquisition_true_true(self):
    self.instrument.config_continuous_acquisition(True, True)
    expected = b'TRMD AUTO'
    assert expected == self.com.get_send_queue()

  def test_config_continuous_acquisition_true_false(self):
    self.instrument.config_continuous_acquisition(True, False)
    expected = b'TRMD NORM'
    assert expected == self.com.get_send_queue()

  def test_config_continuous_acquisition_false(self):
    self.instrument.config_continuous_acquisition(False, True)
    expected = b'TRMD STOP'
    assert expected == self.com.get_send_queue()

  @pytest.mark.xfail
  def test_config_rolling_mode(self):
    with pytest.raises(NotImplementedError):
      self.instrument.config_rolling_mode(True)

  def test_config_pulse_width_trigger_less(self):
    self.instrument.config_pulse_width_trigger(1, 'LESS', 'NEG', 0.1, 1.3, 2.5)
    expected = b'C1:TRLV 0.1'
    assert expected == self.com.get_send_queue()
    expected = b'C1:TRSL NEG'
    assert expected == self.com.get_send_queue()
    expected = b'TRSE WIDTH,SR,C1,HT,PS,HV,2.5'
    assert expected == self.com.get_send_queue()

  def test_config_pulse_width_trigger_more(self):
    self.instrument.config_pulse_width_trigger(1, 'MORE', 'POS', 0.1, 1.3, 2.5)
    expected = b'C1:TRLV 0.1'
    assert expected == self.com.get_send_queue()
    expected = b'C1:TRSL POS'
    assert expected == self.com.get_send_queue()
    expected = b'TRSE WIDTH,SR,C1,HT,PL,HV,1.3'
    assert expected == self.com.get_send_queue()

  def test_config_pulse_width_trigger_within(self):
    self.instrument.config_pulse_width_trigger(
        1, 'WITHIN', 'NEG', 0.1, 1.3, 2.5
    )
    expected = b'C1:TRLV 0.1'
    assert expected == self.com.get_send_queue()
    expected = b'C1:TRSL NEG'
    assert expected == self.com.get_send_queue()
    expected = b'TRSE WIDTH,SR,C1,HT,P2,HV,1.3,HV2,2.5'
    assert expected == self.com.get_send_queue()

  def test_config_pulse_width_trigger_out(self):
    self.instrument.config_pulse_width_trigger(1, 'OUT', 'NEG', 0.1, 1.3, 2.5)
    expected = b'C1:TRLV 0.1'
    assert expected == self.com.get_send_queue()
    expected = b'C1:TRSL NEG'
    assert expected == self.com.get_send_queue()
    expected = b'TRSE WIDTH,SR,C1,HT,P2,HV,2.5,HV2,1.3'
    assert expected == self.com.get_send_queue()

  def test_set_horiz_division_samplesize(self):
    self.instrument.set_horiz_division(
        25, -1, 2.5e6, instrument.HorizonType.SAMPLESIZE
    )
    expected = b'TDIV 25.000'
    assert expected == self.com.get_send_queue()
    expected = b'TRDL -1.000'
    assert expected == self.com.get_send_queue()
    expect = b'vbs \'app.Acquisition.Horizontal.Maximize = "SetMaximumMemory"\''
    assert expect == self.com.get_send_queue()
    expected = b'MSIZ 2500000.000'
    assert expected == self.com.get_send_queue()

  def test_set_horiz_division_samplesize_out_range(self):
    self.instrument.set_horiz_division(
        25, -1, 2.6e6, instrument.HorizonType.SAMPLESIZE
    )
    expected = b'TDIV 25.000'
    assert expected == self.com.get_send_queue()
    expected = b'TRDL -1.000'
    assert expected == self.com.get_send_queue()
    expect = b'vbs \'app.Acquisition.Horizontal.Maximize = "SetMaximumMemory"\''
    assert expect == self.com.get_send_queue()
    expected = b'MSIZ 2500000.000'
    assert expected == self.com.get_send_queue()

  def test_set_horiz_division_samplerate(self):
    self.instrument.set_horiz_division(2.5, -2, 2.5e6, 'samplerate')
    expected = b'TDIV 2.500'
    assert expected == self.com.get_send_queue()
    expected = b'TRDL -2.000'
    assert expected == self.com.get_send_queue()
    expect = b'vbs \'app.Acquisition.Horizontal.Maximize = "FixedSampleRate"\''
    assert expect == self.com.get_send_queue()
    expected = b'vbs \'app.Acquisition.Horizontal.SampleRate = "2500000.0"\''
    assert expected == self.com.get_send_queue()

  def test_set_horiz_division_samplerate_out_range(self):
    self.instrument.set_horiz_division(2.5, -2, 2.6e6, 'samplerate')
    expected = b'TDIV 2.500'
    assert expected == self.com.get_send_queue()
    expected = b'TRDL -2.000'
    assert expected == self.com.get_send_queue()
    expect = b'vbs \'app.Acquisition.Horizontal.Maximize = "FixedSampleRate"\''
    assert expect == self.com.get_send_queue()
    expected = b'vbs \'app.Acquisition.Horizontal.SampleRate = "2500000.0"\''
    assert expected == self.com.get_send_queue()

  def test_set_horiz_division_samplerate_missing_parameter(self):
    self.instrument.set_horiz_division(2.5, -2, 2.6e6)
    expected = b'TDIV 2.500'
    assert expected == self.com.get_send_queue()
    expected = b'TRDL -2.000'

  def test_set_horiz_offset(self):
    self.instrument.set_horiz_offset(2.5)
    expected = b"VBS 'app.Acquisition.C1.Out.Result.HorizontalOffset = 2.500'"
    assert expected == self.com.get_send_queue()

  def test_set_measurement_reference(self):
    self.instrument.set_measurement_reference(12, 55, 87)

  def test_set_measurement_on(self):
    self.instrument.set_measurement_on_off(1, True)
    expected = b'VBS \'app.measure.measureset = "CUST"\''
    assert expected == self.com.get_send_queue()
    expected = b"VBS 'app.measure.showmeasure = TRUE'"
    assert expected == self.com.get_send_queue()
    expected = b"VBS 'app.measure.p1.view = TRUE'"
    assert expected == self.com.get_send_queue()

  @pytest.mark.parametrize(
      'channel, enable, expected_bool', [(1, True, 'TRUE'), (2, False, 'FALSE')]
  )
  def test_set_measurement_on_mix(self, channel, enable, expected_bool):
    self.instrument.set_measurement_on_off(channel, enable)
    expected = b'VBS \'app.measure.measureset = "CUST"\''
    assert expected == self.com.get_send_queue()
    expected = f"VBS 'app.measure.showmeasure = {expected_bool}'".encode()
    assert expected == self.com.get_send_queue()
    expected = f"VBS 'app.measure.p{channel}.view = {expected_bool}'".encode()
    assert expected == self.com.get_send_queue()

  def test_set_measurement_off(self):
    self.instrument.set_measurement_on_off(1, False)
    expected = b'VBS \'app.measure.measureset = "CUST"\''
    assert expected == self.com.get_send_queue()
    expected = b"VBS 'app.measure.showmeasure = FALSE'"
    assert expected == self.com.get_send_queue()
    expected = b"VBS 'app.measure.p1.view = FALSE'"
    assert expected == self.com.get_send_queue()

  def test_set_measurement_statistics_on(self):
    self.instrument.set_measurement_statistics(True)
    expected = b"VBS 'app.Measure.StatsOn = TRUE'"
    assert expected == self.com.get_send_queue()

  def test_set_measurement_statistics_off(self):
    self.instrument.set_measurement_statistics(False)
    expected = b"VBS 'app.Measure.StatsOn = FALSE'"
    assert expected == self.com.get_send_queue()

  def test_set_measurement_risetime(self):
    self.instrument.set_measurement(1, 2, instrument.MeasurementType.RISETIME)
    expected = b"VBS 'app.Acquisition.C1.View = True'"
    assert expected == self.com.get_send_queue()
    expected = b'VBS \'app.measure.measureset = "CUST"\''
    assert expected == self.com.get_send_queue()
    expected = b"VBS 'app.measure.showmeasure = TRUE'"
    assert expected == self.com.get_send_queue()
    expected = b"VBS 'app.measure.p2.view = TRUE'"
    assert expected == self.com.get_send_queue()
    expected = b'PACU 2,RLEV,C1,10 PCT,90 PCT'
    assert expected == self.com.get_send_queue()

  def test_set_measurement_falltime(self):
    self.instrument.set_measurement(1, 2, instrument.MeasurementType.FALLTIME)
    expected = b"VBS 'app.Acquisition.C1.View = True'"
    assert expected == self.com.get_send_queue()
    expected = b'VBS \'app.measure.measureset = "CUST"\''
    assert expected == self.com.get_send_queue()
    expected = b"VBS 'app.measure.showmeasure = TRUE'"
    assert expected == self.com.get_send_queue()
    expected = b"VBS 'app.measure.p2.view = TRUE'"
    assert expected == self.com.get_send_queue()
    expected = b'PACU 2,FLEV,C1,90 PCT,10 PCT'
    assert expected == self.com.get_send_queue()

  def test_set_measurement_pulsewidth(self):
    self.instrument.set_measurement(
        1, 2, instrument.MeasurementType.PULSEWIDTHPOSITIVE
    )
    expected = b"VBS 'app.Acquisition.C1.View = True'"
    assert expected == self.com.get_send_queue()
    expected = b'VBS \'app.measure.measureset = "CUST"\''
    assert expected == self.com.get_send_queue()
    expected = b"VBS 'app.measure.showmeasure = TRUE'"
    assert expected == self.com.get_send_queue()
    expected = b"VBS 'app.measure.p2.view = TRUE'"
    assert expected == self.com.get_send_queue()
    expected = b'PACU 2,WIDLV,C1,POS,50 PCT'
    assert expected == self.com.get_send_queue()

  def test_set_measurement_risingedgecount(self):
    self.instrument.set_measurement(
        1, 2, instrument.MeasurementType.RISINGEDGECOUNT
    )
    expected = b"VBS 'app.Acquisition.C1.View = True'"
    assert expected == self.com.get_send_queue()
    expected = b'VBS \'app.measure.measureset = "CUST"\''
    assert expected == self.com.get_send_queue()
    expected = b"VBS 'app.measure.showmeasure = TRUE'"
    assert expected == self.com.get_send_queue()
    expected = b"VBS 'app.measure.p2.view = TRUE'"
    assert expected == self.com.get_send_queue()
    expected = b'PACU 2,EDLEV,C1,POS,50 PCT'
    assert expected == self.com.get_send_queue()

  def test_set_measurement_dutycyclepositive(self):
    self.instrument.set_measurement(
        1, 2, instrument.MeasurementType.DUTYCYCLEPOSITIVE
    )
    expected = b"VBS 'app.Acquisition.C1.View = True'"
    assert expected == self.com.get_send_queue()
    expected = b'VBS \'app.measure.measureset = "CUST"\''
    assert expected == self.com.get_send_queue()
    expected = b"VBS 'app.measure.showmeasure = TRUE'"
    assert expected == self.com.get_send_queue()
    expected = b"VBS 'app.measure.p2.view = TRUE'"
    assert expected == self.com.get_send_queue()
    expected = b'PACU 2,DULEV,C1,POS,50 PCT'
    assert expected == self.com.get_send_queue()

  def test_set_measurement_average(self):
    self.instrument.set_measurement(1, 2, 'average')
    expected = b"VBS 'app.Acquisition.C1.View = True'"
    assert expected == self.com.get_send_queue()
    expected = b'VBS \'app.measure.measureset = "CUST"\''
    assert expected == self.com.get_send_queue()
    expected = b"VBS 'app.measure.showmeasure = TRUE'"
    assert expected == self.com.get_send_queue()
    expected = b"VBS 'app.measure.p2.view = TRUE'"
    assert expected == self.com.get_send_queue()
    expected = b'PACU 2,MEAN,C1'
    assert expected == self.com.get_send_queue()

  def test_set_delta_measurement(self):
    self.instrument.set_delta_measurement(
        4, 1, 2, instrument.DeltSlope.RISE, instrument.DeltSlope.RISE
    )
    expected = b'PACU 4,DTLEV,C1,POS,50 PCT,0.5 DIV,C2,POS,50 PCT,0.5 DIV'
    assert expected == self.com.get_send_queue()

  def test_set_cursor_hor(self):
    self.com.push_recv_queue(b'10')
    self.com.push_recv_queue(b'2')
    self.instrument.set_cursor(1, 'HOR', -5, 10)
    expected = b'CRS VREL'
    assert expected == self.com.get_send_queue()
    expected = b'C1:VDIV?'
    assert expected == self.com.get_send_queue()
    expected = b'C1:OFST?'
    assert expected == self.com.get_send_queue()
    expected = b'C1:CRST VREF,-0.3,VDIF,1.2'
    assert expected == self.com.get_send_queue()

  def test_set_cursor_ver(self):
    self.com.push_recv_queue(b'10')
    self.com.push_recv_queue(b'2')
    self.instrument.set_cursor(1, 'ver', -5, 10)
    expected = b'CRS HREL'
    assert expected == self.com.get_send_queue()
    expected = b'TDIV?'
    assert expected == self.com.get_send_queue()
    expected = b'TRDL?'
    assert expected == self.com.get_send_queue()
    expected = b'C1:CRST HREF,4.7,HDIF,6.2'
    assert expected == self.com.get_send_queue()

  def test_set_infinite_persistence_on(self):
    self.instrument.set_infinite_persistence(True)
    expected = b'PERSIST ON'
    assert expected == self.com.get_send_queue()
    expected = b'PESU infinite,ALL'
    assert expected == self.com.get_send_queue()

  def test_set_infinite_persistence_off(self):
    self.instrument.set_infinite_persistence(False)
    expected = b'PERSIST OFF'
    assert expected == self.com.get_send_queue()

  def test_clear_persistence(self):
    self.instrument.clear_persistence()
    expected = b"VBS 'app.Display.ClearSweeps'"
    assert expected == self.com.get_send_queue()

  def test_wait_acquisition_complete(self):
    self.com.push_recv_queue(b'1')
    self.instrument.wait_acquisition_complete(1)
    expected = b'INR?'
    assert expected == self.com.get_send_queue()

  def test_wait_acquisition_complete_timeout(self):
    self.com.push_recv_queue(b'1')
    self.instrument.wait_acquisition_complete(1)
    expected = b'INR?'
    assert expected == self.com.get_send_queue()

  def test_get_acquisition(self):
    self.com.push_recv_queue(b'0')
    recv = self.instrument.get_acquisition()
    expected = b'INR?'
    assert expected == self.com.get_send_queue()
    assert '0' == recv

  def test_arm_single_trig(self):
    self.instrument.arm_single_trig()
    expected = b'TRMD STOP'
    assert expected == self.com.get_send_queue()

  def test_stop_acquisition(self):
    self.instrument.stop_acquisition()
    expected = b'STOP'
    assert expected == self.com.get_send_queue()

  def test_start_acquisition(self):
    self.instrument.start_acquisition()
    expected = b'TRMD AUTO'
    assert expected == self.com.get_send_queue()

  def test_reset_measurement_statistics(self):
    self.instrument.reset_measurement_statistics()
    expected = b"VBS 'app.Measure.ClearSweeps'"
    assert expected == self.com.get_send_queue()

  def test_get_measurement_statistics(self):
    self.com.push_recv_queue(b'0')
    self.com.push_recv_queue(b'MyMeasure')
    self.com.push_recv_queue(
        b'CUST,P1,AMPL,C1,AVG,11,HIGH,22,LAST,33,LOW,44,'
        b'SIGMA,55,SWEEPS,66;Valid'
    )
    self.instrument.get_measurement_statistics(1)
    expected = b"VBS? 'return=app.Measure.ShowMeasure'"
    assert expected == self.com.get_send_queue()
    expected = b"VBS 'app.Measure.ShowMeasure = True'"
    assert expected == self.com.get_send_queue()
    expected = b"VBS? 'return=app.Measure.MeasureSet'"
    assert expected == self.com.get_send_queue()
    expected = (
        b"PAST? CUST, P1;VBS? 'return=app.Measure.P1.Out.Result."
        + b"StatusDescription'"
    )
    assert expected == self.com.get_send_queue()

  def test_wait_task(self):
    self.com.push_recv_queue(b'1')
    self.instrument.wait_task(1)
    expected = b"vbs? 'return=app.WaitUntilIdle(1)'"
    assert expected == self.com.get_send_queue()

  def test_wait_wait_trigger_ready(self):
    self.com.push_recv_queue(b'1')
    self.instrument.wait_trigger_ready(1)
    expected = b"vbs? 'return=app.WaitUntilIdle(1)'"
    assert expected == self.com.get_send_queue()

  def test_fetch_delta_measurement(self):
    self.com.push_recv_queue(b'1,AMPL,C1')
    self.com.push_recv_queue(b'1,-500.01161E-6,OK')
    val = self.instrument.fetch_delta_measurement(
        1, 2, instrument.DeltSlope.RISE, instrument.DeltSlope.FALL, 51, 52
    )
    expected = b'PACU? 1'
    assert expected == self.com.get_send_queue()
    expected = b'PACU 1,DTLEV,C1,POS,51 PCT,C2,NEG,52 PCT'
    assert expected == self.com.get_send_queue()
    expected = b'PAVA? CUST1'
    assert expected == self.com.get_send_queue()
    expected = b'PACU 1,AMPL,C1'
    assert expected == self.com.get_send_queue()
    assert -500.01161e-6 == val

  def test_fetch_delta_measurement_undef(self):
    self.com.push_recv_queue(b'1,AMPL,C1')
    self.com.push_recv_queue(b'1,UNDEF,IV')
    val = self.instrument.fetch_delta_measurement(
        1, 2, instrument.DeltSlope.RISE, instrument.DeltSlope.FALL, 51, 52
    )
    expected = b'PACU? 1'
    assert expected == self.com.get_send_queue()
    expected = b'PACU 1,DTLEV,C1,POS,51 PCT,C2,NEG,52 PCT'
    assert expected == self.com.get_send_queue()
    expected = b'PAVA? CUST1'
    assert expected == self.com.get_send_queue()
    expected = b'PACU 1,AMPL,C1'
    assert expected == self.com.get_send_queue()
    assert math.nan is val

  def test_fetch_measurement_risetime(self):
    self.com.push_recv_queue(b'1,AMPL,C1')
    self.com.push_recv_queue(b'1,9,OK')
    val = self.instrument.fetch_measurement(
        1, instrument.MeasurementType.RISETIME
    )
    expected = b'PACU? 1'
    assert expected == self.com.get_send_queue()
    expected = b'PACU 1,RLEV,C1,10 PCT,90 PCT'
    assert expected == self.com.get_send_queue()
    expected = b'PAVA? CUST1'
    assert expected == self.com.get_send_queue()
    assert 9 == val

  def test_fetch_measurement_pulsewidth(self):
    self.com.push_recv_queue(b'1,AMPL,C1')
    self.com.push_recv_queue(b'1,9,OK')
    val = self.instrument.fetch_measurement(
        1, instrument.MeasurementType.PULSEWIDTHPOSITIVE
    )
    expected = b'PACU? 1'
    assert expected == self.com.get_send_queue()
    expected = b'PACU 1,WIDLV,C1,POS,50 PCT'
    assert expected == self.com.get_send_queue()
    expected = b'PAVA? CUST1'
    assert expected == self.com.get_send_queue()
    assert 9 == val

  def test_fetch_measurement_edgecount(self):
    self.com.push_recv_queue(b'1,AMPL,C1')
    self.com.push_recv_queue(b'1,9,OK')
    val = self.instrument.fetch_measurement(
        1, instrument.MeasurementType.RISINGEDGECOUNT
    )
    expected = b'PACU? 1'
    assert expected == self.com.get_send_queue()
    expected = b'PACU 1,EDLEV,C1,POS,50 PCT'
    assert expected == self.com.get_send_queue()
    expected = b'PAVA? CUST1'
    assert expected == self.com.get_send_queue()
    assert 9 == val

  def test_fetch_measurement_dutycycle(self):
    self.com.push_recv_queue(b'1,AMPL,C1')
    self.com.push_recv_queue(b'1,9,OK')
    val = self.instrument.fetch_measurement(
        1, instrument.MeasurementType.DUTYCYCLEPOSITIVE
    )
    expected = b'PACU? 1'
    assert expected == self.com.get_send_queue()
    expected = b'PACU 1,DULEV,C1,POS,50 PCT'
    assert expected == self.com.get_send_queue()
    expected = b'PAVA? CUST1'
    assert expected == self.com.get_send_queue()
    assert 9 == val

  def test_fetch_measurement_peak2peak(self):
    self.com.push_recv_queue(b'1,AMPL,C1')
    self.com.push_recv_queue(b'1,9,OK')
    val = self.instrument.fetch_measurement(
        1, instrument.MeasurementType.PEAKTOPEAK
    )
    expected = b'PACU? 1'
    assert expected == self.com.get_send_queue()
    expected = b'C1:PAVA? PKPK'
    assert expected == self.com.get_send_queue()
    assert 9 == val

  def test_fetch_measurement_undef(self):
    self.com.push_recv_queue(b'1,AMPL,C1')
    self.com.push_recv_queue(b'FREQ,UNDEF,IV')
    val = self.instrument.fetch_measurement(
        1, instrument.MeasurementType.FREQUENCY
    )
    expected = b'PACU? 1'
    assert expected == self.com.get_send_queue()
    expected = b'C1:PAVA? FREQ'
    assert expected == self.com.get_send_queue()
    assert math.nan is val

  def test_fetch_measurement_falltime_undef(self):
    self.com.push_recv_queue(b'1,AMPL,C1')
    self.com.push_recv_queue(b'1,UNDEF,IV')
    val = self.instrument.fetch_measurement(
        1, instrument.MeasurementType.FALLTIME
    )
    expected = b'PACU? 1'
    assert expected == self.com.get_send_queue()
    expected = b'PACU 1,FLEV,C1,10 PCT,90 PCT'
    assert expected == self.com.get_send_queue()
    assert math.nan is val

  def test_fetch_measure_number(self):
    self.com.push_recv_queue(b'13')
    val = self.instrument.fetch_measure_number(1)
    expected = b"vbs? 'return=app.measure.p1.out.result.value'"
    assert expected == self.com.get_send_queue()
    assert 13 == val

  def test_fetch_measure_number_nodata(self):
    self.com.push_recv_queue(b'No Data Available')
    val = self.instrument.fetch_measure_number(2)
    expected = b"vbs? 'return=app.measure.p2.out.result.value'"
    assert expected == self.com.get_send_queue()
    assert math.nan is val

  def test_fetch_waveform(self):
    self.com.push_recv_queue(
        b'DESCRIPTOR_NAME    : WAVEDESC\r\n'
        b'TEMPLATE_NAME      : LECROY_2_3\r\n'
        b'COMM_TYPE          : word\r\n'
        b'COMM_ORDER         : HIFIRST\r\n'
        b'WAVE_DESCRIPTOR    : 346\r\n'
        b'USER_TEXT          : 0\r\n'
        b'RES_DESC1          : 0\r\n'
        b'TRIGTIME_ARRAY     : 0\r\n'
        b'RIS_TIME_ARRAY     : 0\r\n'
        b'RES_ARRAY1         : 0\r\n'
        b'WAVE_ARRAY_1       : 10004\r\n'
        b'WAVE_ARRAY_2       : 0\r\n'
        b'RES_ARRAY2         : 0\r\n'
        b'RES_ARRAY3         : 0\r\n'
        b'INSTRUMENT_NAME    : LECROYHDO6104A-MRP\r\n'
        b'INSTRUMENT_NUMBER  : 53330\r\n'
        b'TRACE_LABEL        :\r\n'
        b'RESERVED1          : 5002\r\n'
        b'RESERVED2          : 0\r\n'
        b'WAVE_ARRAY_COUNT   : 5002\r\n'
        b'PNTS_PER_SCREEN    : 5000\r\n'
        b'FIRST_VALID_PNT    : 0\r\n'
        b'LAST_VALID_PNT     : 5001\r\n'
        b'FIRST_POINT        : 0\r\n'
        b'SPARSING_FACTOR    : 1\r\n'
        b'SEGMENT_INDEX      : 0\r\n'
        b'SUBARRAY_COUNT     : 1\r\n'
        b'SWEEPS_PER_ACQ     : 1\r\n'
        b'POINTS_PER_PAIR    : 0\r\n'
        b'PAIR_OFFSET        : 0\r\n'
        b'VERTICAL_GAIN      : 1.2500e-04\r\n'
        b'VERTICAL_OFFSET    : -5.0000e-03\r\n'
        b'MAX_VALUE          : 1.5704e+04\r\n'
        b'MIN_VALUE          : -1.6040e+04\r\n'
        b'NOMINAL_BITS       : 12\r\n'
        b'NOM_SUBARRAY_COUNT : 1\r\n'
        b'HORIZ_INTERVAL     : 1.0000e-10\r\n'
        b'HORIZ_OFFSET       : -2.50087542e-07\r\n'
        b'PIXEL_OFFSET       : -2.50000000e-07\r\n'
        b'VERTUNIT           : Unit Name = V\r\n'
        b'HORUNIT            : Unit Name = S\r\n'
        b'HORIZ_UNCERTAINTY  : 1.0000e-12\r\n'
        b'TRIGGER_TIME       : Date = AUG 22, 2022, Time ='
        b'  8:52:45.184039163\r\n'
        b'ACQ_DURATION       : 0.0000e+00\r\n'
        b'RECORD_TYPE        : single_sweep\r\n'
        b'PROCESSING_DONE    : no_processing\r\n'
        b'RESERVED5          : 0\r\n'
        b'RIS_SWEEPS         : 1\r\n'
        b'TIMEBASE           : 50_ns/div\r\n'
        b'VERT_COUPLING      : DC_1MOhm\r\n'
        b'PROBE_ATT          : 1.0000e+01\r\n'
        b'FIXED_VERT_GAIN    : 50_mV/div\r\n'
        b'BANDWIDTH_LIMIT    : off\r\n'
        b'VERTICAL_VERNIER   : 1.0000e+00\r\n'
        b'ACQ_VERT_OFFSET    : 0.0000e+00\r\n'
        b'WAVE_SOURCE        : CHANNEL_2\r\n'
    )
    self.com.push_recv_queue(b'768,512' * 10000)
    recv, _ = self.instrument.fetch_waveform(2)
    expected = b'COMM_ORDER HI'
    assert expected == self.com.get_send_queue()
    expected = b'COMM_FORMAT DEF9,WORD,BIN'
    assert expected == self.com.get_send_queue()
    expected = b'C2:INSPECT? WAVEDESC'
    assert expected == self.com.get_send_queue()
    expected = b'C2:WAVEFORM? DAT1'
    assert expected == self.com.get_send_queue()
    info_dict = {
        'points_number': 5000,
        'x_increment': 1e-10,
        'x_origin': -2.50087542e-07,
        'y_increment': 0.000125,
        'y_origin': -0.005,
    }
    assert info_dict == recv

  def test_load_settings_file(self):
    self.com.push_recv_queue(b'1')
    self.instrument.load_settings_file('HahaThisIsPath')
    expected = b'VBS \' app.SaveRecall.Setup.PanelFilename = "set1.lss"\''
    assert expected == self.com.get_send_queue()
    expected = b'VBS \' app.SaveRecall.Setup.PanelDir = "D:\\Setups"\''
    assert expected == self.com.get_send_queue()
    expected = b"VBS ' app.SaveRecall.Setup.DoRecallPanel'"
    assert expected == self.com.get_send_queue()
    expected = b'*OPC?'
    assert expected == self.com.get_send_queue()

  def test_save_settings_file(self):
    self.com.push_recv_queue(b'1')
    self.com.push_recv_queue(b'setting_file')
    self.instrument.save_settings_file('HahaThisIsPath')
    expected = b'VBS \'app.SaveRecall.Setup.PanelFilename = "set1.lss"\''
    assert expected == self.com.get_send_queue()
    expected = b'VBS \'app.SaveRecall.Setup.PanelDir = "D:\\Setups"\''
    assert expected == self.com.get_send_queue()
    expected = b"VBS 'app.SaveRecall.Setup.DoSavePanel'"
    assert expected == self.com.get_send_queue()
    expected = b'*OPC?'
    assert expected == self.com.get_send_queue()
    expected = b"TRFL? DISK,HDD,FILE,'D:\\Setups\\set1.lss'"
    assert expected == self.com.get_send_queue()
    os.remove('HahaThisIsPath')

  def test_save_screenshot(self):
    self.com.push_recv_queue(b'screenshot')
    self.instrument.save_screenshot('HahaThisIsPath')
    expected = (
        b'HCSU DEV, PNG, FORMAT,PORTRAIT, BCKG, WHITE, DEST, REMOTE,'
        + b' PORT, NET, AREA,GRIDAREAONLY'
    )
    assert expected == self.com.get_send_queue()
    expected = b'SCDP'
    assert expected == self.com.get_send_queue()
    os.remove('HahaThisIsPath')

  def test_get_screenshot(self):
    self.instrument._get_screenshot('HahaThisIsPath')
    expected = (
        b'HARDCOPY_SETUP DEV,PNG,FORMAT,LANDSCAPE,BCKG,BLACK,DEST,'
        + b'FILE,,DIR,HahaThisIsPath,AREA,FULLSCREEN,FILE,test'
    )
    assert expected == self.com.get_send_queue()
    expected = b'SCREEN_DUMP'
    assert expected == self.com.get_send_queue()

  def test_auto_set(self):
    self.instrument.auto_set()
    expected = b"VBS 'app.AutoSetup 1'"
    assert expected == self.com.get_send_queue()

  # @pytest.mark.xfail(raises=AttributeError)

  @pytest.mark.parametrize(
      'bit1, bit2, bit3',
      [
          (b'1', b'0', b'0'),
          (b'0', b'1', b'0'),
          (b'0', b'0', b'1'),
      ],
  )
  def test_get_error_status(self, bit1, bit2, bit3):
    self.com.push_recv_queue(bit1)
    self.com.push_recv_queue(bit2)
    self.com.push_recv_queue(bit3)
    with pytest.raises(AttributeError):
      self.instrument.get_error_status()
    expected = b'CMR?'
    assert expected == self.com.get_send_queue()
    expected = b'EXR?'
    assert expected == self.com.get_send_queue()
    expected = b'DDR?'
    assert expected == self.com.get_send_queue()
