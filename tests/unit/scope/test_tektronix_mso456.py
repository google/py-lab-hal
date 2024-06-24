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

"""Test of TektronixMSO456."""

import os

from py_lab_hal import builder
from py_lab_hal.cominterface import cominterface
from py_lab_hal.cominterface import debug
from py_lab_hal.instrument import instrument
import pytest


class TestTektronixMSO456:
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

    TestTektronixMSO456.instrument = build.build_instrument(
        builder.Scope.TEKTRONIX_MSO
    )
    TestTektronixMSO456.instrument.idn = (
        'LECROY,HDO6104A-MS,LCRY4068N53330,9.1.0'
    )
    TestTektronixMSO456.instrument.open_instrument()
    TestTektronixMSO456.com = TestTektronixMSO456.instrument.inst
    yield

  def test_set_channel_position(self):
    self.instrument.set_channel_position(1, 2.34)
    expected = b'DISplay:WAVEView1:CH1:VERTical:POSition 2.3400e+00'
    assert expected == self.com.get_send_queue()

  def test_set_channel_position_max(self):
    self.instrument.set_channel_position(1, 9)
    expected = b'DISplay:WAVEView1:CH1:VERTical:POSition 9.0000e+00'
    assert expected == self.com.get_send_queue()

  def test_set_channel_position_min(self):
    self.instrument.set_channel_position(1, -9)
    expected = b'DISplay:WAVEView1:CH1:VERTical:POSition -9.0000e+00'
    assert expected == self.com.get_send_queue()

  def test_set_channel_attenuation(self):
    self.instrument.set_channel_attenuation(1, 10)
    expected = b'CH1:PRObe:SET ATTENUATION 10X'
    assert expected == self.com.get_send_queue()

  def test_set_channel_coupling(self):
    self.instrument.set_channel_coupling(1, 'DC', 50)
    expected = b'CH1:COUPling DC'
    assert expected == self.com.get_send_queue()
    expected = b'CH1:TERmination 50'
    assert expected == self.com.get_send_queue()

  def test_set_channel_offset(self):
    self.instrument.set_channel_offset(1, 1.23)
    expected = b'CH1:OFFSet 1.2300e+00'
    assert expected == self.com.get_send_queue()

  def test_set_channel_division(self):
    self.instrument.set_channel_division(1, 1.23)
    expected = b'DISplay:WAVEView1:CH1:VERTical:SCAle 1.2300e+00'
    assert expected == self.com.get_send_queue()

  def test_set_channel_on_off(self):
    self.instrument.set_channel_on_off(1, True)
    expected = b':DISPLAY:WAVEVIEW1:CH1:STATE 1'
    assert expected == self.com.get_send_queue()

  def test_set_channel_bandwidth_on(self):
    self.instrument.set_channel_bandwidth(1, 20e6, True)
    expected = b'CH1:BANdwidth 2.0000e+07'
    assert expected == self.com.get_send_queue()

  def test_set_channel_bandwidth_not_in_list(self):
    self.instrument.set_channel_bandwidth(1, 5.1e8, True)
    expected = b'CH1:BANdwidth 5.0000e+08'
    assert expected == self.com.get_send_queue()

  def test_set_channel_bandwidth_off(self):
    self.instrument.set_channel_bandwidth(1, 3e8, False)
    expected = b'CH1:BANdwidth FULL'
    assert expected == self.com.get_send_queue()

  @pytest.mark.parametrize(
      'channel,name',
      [
          (1, 'Kok hua'),
          (2, 'Mike'),
      ],
  )
  def test_set_channel_labels(self, channel, name):
    self.instrument.set_channel_labels(channel, name)
    expected = f'CH{channel}:LABel:NAMe "{name}"'
    assert expected.encode() == self.com.get_send_queue()

  def test_set_channel_labels_position(self):
    self.instrument.set_channel_labels_position(1, 1.23, 2.34)
    expected = b'CH1:LABel:XPOS 1.23'
    assert expected == self.com.get_send_queue()
    expected = b'CH1:LABel:YPOS 2.34'
    assert expected == self.com.get_send_queue()

  def test_get_channel_labels_one_channel(self):
    self.com.push_recv_queue(b'Kok hua')
    recv = self.instrument.get_channel_labels(1)
    expected = b'CH1:LABel:NAMe?'
    assert expected == self.com.get_send_queue()
    assert 'Kok hua' == recv

  def test_get_channel_labels_many_channel(self):
    self.com.push_recv_queue(b'Kok Hua,James Lee')
    self.com.push_recv_queue(b'Mike')
    recv = self.instrument.get_channel_labels([1, 2])
    expected = b'CH1:LABel:NAMe?'
    assert expected == self.com.get_send_queue()
    expected = b'CH2:LABel:NAMe?'
    assert expected == self.com.get_send_queue()
    assert ['Kok Hua,James Lee', 'Mike'] == recv

  def test_set_vert_range(self):
    self.instrument.set_vert_range(1, True, 12.3, 1.23, 10, 'DC')
    expected = b':DISPLAY:WAVEVIEW1:CH1:STATE 1'
    assert expected == self.com.get_send_queue()
    expected = b'DISplay:WAVEView1:CH1:VERTical:SCAle 1.2300e+00'
    assert expected == self.com.get_send_queue()
    expected = b'CH1:OFFSet 1.2300e+00'
    assert expected == self.com.get_send_queue()
    expected = b'CH1:PRObe:SET ATTENUATION 10X'
    assert expected == self.com.get_send_queue()
    expected = b'CH1:COUPling DC'
    assert expected == self.com.get_send_queue()

  def test_config_edge_trigger(self):
    self.instrument.config_edge_trigger(1, 0.5, 'FALL', 'DC')
    expected = b':DISPLAY:WAVEVIEW1:CH1:STATE 1'
    assert expected == self.com.get_send_queue()
    expected = b'TRIGger:A:TYPe EDGE'
    assert expected == self.com.get_send_queue()
    expected = b'TRIGger:A:EDGE:SOUrce CH1'
    assert expected == self.com.get_send_queue()
    expected = b'TRIGger:A:LEvel:CH1 0.5'
    assert expected == self.com.get_send_queue()
    expected = b'TRIGger:A:EDGE:SLOpe FALL'
    assert expected == self.com.get_send_queue()
    expected = b'TRIGger:A:EDGE:COUPling DC'
    assert expected == self.com.get_send_queue()

  def test_set_aux_trigger_enable(self):
    self.instrument.set_aux_trigger(True)
    expected = b'AUXout:SOUrce ATRIGger'
    assert expected == self.com.get_send_queue()

  def test_set_aux_trigger_disable(self):
    self.instrument.set_aux_trigger(False)
    expected = b'AUXout:SOUrce REFOUT'
    assert expected == self.com.get_send_queue()

  def test_config_continuous_acquisition(self):
    self.instrument.config_continuous_acquisition(True, True)
    expected = b'ACQuire:STOPAfter RUNSTop'
    assert expected == self.com.get_send_queue()
    expected = b'TRIGger:A:MODe Auto'
    assert expected == self.com.get_send_queue()
    expected = b':ACQuire:STATE ON'
    assert expected == self.com.get_send_queue()

  def test_config_rolling_mode(self):
    self.com.push_recv_queue(b'ROLL')
    self.instrument.config_rolling_mode(True)
    expected = b'HORIZONTAL:ROLL?'
    assert expected == self.com.get_send_queue()

  def test_config_pulse_width_trigger_less(self):
    self.instrument.config_pulse_width_trigger(1, 'LESS', 'NEG', 0.1, 1.3, 2.5)
    expected = b':DISPLAY:WAVEVIEW1:CH1:STATE 1'
    assert expected == self.com.get_send_queue()
    expected = b'TRIGger:A:TYPe WIDth'
    assert expected == self.com.get_send_queue()
    expected = b'TRIGger:A:PULSEWidth:SOUrce CH1'
    assert expected == self.com.get_send_queue()
    expected = b'TRIGger:A:LEVel:CH1 0.1'
    assert expected == self.com.get_send_queue()
    expected = b'TRIGger:A:PULSEWidth:POLarity NEGative'
    assert expected == self.com.get_send_queue()
    expected = b'TRIGger:A:PULSEWidth:WHEn LESSthan'
    assert expected == self.com.get_send_queue()
    expected = b'TRIGger:A:PULSEWidth:WIDth 2.5'
    assert expected == self.com.get_send_queue()
    expected = b'TRIGger:A:PULSEWidth:LOGICQUALification OFF'
    assert expected == self.com.get_send_queue()

  def test_config_pulse_width_trigger_more(self):
    self.instrument.config_pulse_width_trigger(1, 'MORE', 'POS', 0.1, 1.3, 2.5)
    expected = b':DISPLAY:WAVEVIEW1:CH1:STATE 1'
    assert expected == self.com.get_send_queue()
    expected = b'TRIGger:A:TYPe WIDth'
    assert expected == self.com.get_send_queue()
    expected = b'TRIGger:A:PULSEWidth:SOUrce CH1'
    assert expected == self.com.get_send_queue()
    expected = b'TRIGger:A:LEVel:CH1 0.1'
    assert expected == self.com.get_send_queue()
    expected = b'TRIGger:A:PULSEWidth:POLarity POSitive'
    assert expected == self.com.get_send_queue()
    expected = b'TRIGger:A:PULSEWidth:WHEn MOREthan'
    assert expected == self.com.get_send_queue()
    expected = b'TRIGger:A:PULSEWidth:WIDth 1.3'
    assert expected == self.com.get_send_queue()
    expected = b'TRIGger:A:PULSEWidth:LOGICQUALification OFF'
    assert expected == self.com.get_send_queue()

  def test_config_pulse_width_trigger_within(self):
    self.instrument.config_pulse_width_trigger(
        1, 'WITHIN', 'NEG', 0.1, 1.3, 2.5
    )
    expected = b':DISPLAY:WAVEVIEW1:CH1:STATE 1'
    assert expected == self.com.get_send_queue()
    expected = b'TRIGger:A:TYPe WIDth'
    assert expected == self.com.get_send_queue()
    expected = b'TRIGger:A:PULSEWidth:SOUrce CH1'
    assert expected == self.com.get_send_queue()
    expected = b'TRIGger:A:LEVel:CH1 0.1'
    assert expected == self.com.get_send_queue()
    expected = b'TRIGger:A:PULSEWidth:POLarity NEGative'
    assert expected == self.com.get_send_queue()
    expected = b'TRIGger:A:PULSEWidth:WHEn WIThin'
    assert expected == self.com.get_send_queue()
    expected = b'TRIGger:A:PULSEWidth:HIGHLimit 2.5'
    assert expected == self.com.get_send_queue()
    expected = b'TRIGger:A:PULSEWidth:LOWLimit 1.3'
    assert expected == self.com.get_send_queue()
    expected = b'TRIGger:A:PULSEWidth:LOGICQUALification OFF'
    assert expected == self.com.get_send_queue()

  def test_config_pulse_width_trigger_out(self):
    self.instrument.config_pulse_width_trigger(1, 'OUT', 'NEG', 0.1, 1.3, 2.5)
    expected = b':DISPLAY:WAVEVIEW1:CH1:STATE 1'
    assert expected == self.com.get_send_queue()
    expected = b'TRIGger:A:TYPe WIDth'
    assert expected == self.com.get_send_queue()
    expected = b'TRIGger:A:PULSEWidth:SOUrce CH1'
    assert expected == self.com.get_send_queue()
    expected = b'TRIGger:A:LEVel:CH1 0.1'
    assert expected == self.com.get_send_queue()
    expected = b'TRIGger:A:PULSEWidth:POLarity NEGative'
    assert expected == self.com.get_send_queue()
    expected = b'TRIGger:A:PULSEWidth:WHEn OUTside'
    assert expected == self.com.get_send_queue()
    expected = b'TRIGger:A:PULSEWidth:HIGHLimit 1.3'
    assert expected == self.com.get_send_queue()
    expected = b'TRIGger:A:PULSEWidth:LOWLimit 2.5'
    assert expected == self.com.get_send_queue()
    expected = b'TRIGger:A:PULSEWidth:LOGICQUALification OFF'
    assert expected == self.com.get_send_queue()

  def test_set_horiz_division_samplesize(self):
    self.instrument.set_horiz_division(25, -1, 3.125e7, 'samplesize')
    expected = b'HORizontal:MODE MANual'
    assert expected == self.com.get_send_queue()
    expected = b'HORizontal:MODe:MANual:CONFIGure RECORDLength'
    assert expected == self.com.get_send_queue()
    expected = b'HORizontal:SAMPLERate 1.2500e+05'
    assert expected == self.com.get_send_queue()

  def test_set_horiz_division_samplerate(self):
    self.instrument.set_horiz_division(2.5, -2, 1.257e6, 'samplerate')
    expected = b'HORizontal:MODE MANual'
    assert expected == self.com.get_send_queue()
    expected = b'HORizontal:MODe:MANual:CONFIGure RECORDLength'
    assert expected == self.com.get_send_queue()
    expected = b'HORizontal:SAMPLERate 1.2570e+06'
    assert expected == self.com.get_send_queue()

  def test_set_horiz_division_missing_parameter(self):
    self.instrument.set_horiz_division(2.5, -2, 1.25e6)

  def test_set_horiz_offset(self):
    self.instrument.set_horiz_offset(87)
    expected = b'HORizontal:POSition 8.7000e+01'
    assert expected == self.com.get_send_queue()

  def test_set_horiz_offset_out_of_range(self):
    self.instrument.set_horiz_offset(-187)
    expected = b'HORizontal:POSition 0.0000e+00'
    assert expected == self.com.get_send_queue()

  def test_set_measurement_reference(self):
    self.instrument.set_measurement_reference(12, 55, 87)
    expected = b':MEASUrement:REFLevels:TYPE GLOBal'
    assert expected == self.com.get_send_queue()
    expected = b':MEASUrement:REFLevels:METHod PERCent'
    assert expected == self.com.get_send_queue()
    expected = b':MEASUrement:REFLevels:PERCent:TYPE CUSTom'
    assert expected == self.com.get_send_queue()
    expected = b':MEASUrement:REFLevels:BASETop AUTO'
    assert expected == self.com.get_send_queue()
    expected = b'MEASUrement:REFLevels:PERCent:RISELow 12'
    assert expected == self.com.get_send_queue()
    expected = b'MEASUrement:REFLevels:PERCent:FALLLow 12'
    assert expected == self.com.get_send_queue()
    expected = b'MEASUrement:REFLevels:PERCent:RISEMid 55'
    assert expected == self.com.get_send_queue()
    expected = b'MEASUrement:REFLevels:PERCent:FALLMid 55'
    assert expected == self.com.get_send_queue()
    expected = b'MEASUrement:REFLevels:PERCent:RISEHigh 87'
    assert expected == self.com.get_send_queue()
    expected = b'MEASUrement:REFLevels:PERCent:FALLHigh 87'
    assert expected == self.com.get_send_queue()
    expected = b':MEASUrement:REFLevels:MODE CONTinuous'
    assert expected == self.com.get_send_queue()

  def test_set_measurement_on(self):
    self.instrument.set_measurement(3, 1, 'risetime')
    expected = b'MEASUrement:MEAS1:TYPE RISETIME'
    assert expected == self.com.get_send_queue()
    expected = b'MEASUrement:MEAS1:SOURCE CH3'
    assert expected == self.com.get_send_queue()
    self.instrument.set_measurement_on_off(1, True)
    expected = b'MEASUrement:MEAS1:TYPE RISETIME'
    assert expected == self.com.get_send_queue()
    expected = b'MEASUrement:MEAS1:SOURCE CH3'
    assert expected == self.com.get_send_queue()

  def test_set_measurement_off(self):
    self.instrument.set_measurement(2, 1, 'falltime')
    expected = b'MEASUrement:MEAS1:TYPE FallTIME'
    assert expected == self.com.get_send_queue()
    expected = b'MEASUrement:MEAS1:SOURCE CH2'
    assert expected == self.com.get_send_queue()
    self.instrument.set_measurement_on_off(1, False)
    expected = b'MEASUrement:DELete "MEAS1"'
    assert expected == self.com.get_send_queue()

  def test_set_measurement_notexist(self):
    self.instrument.set_measurement_on_off(1, False)

  def test_set_measurement_statistics_on(self):
    self.instrument.set_measurement_statistics(True)
    expected = b'MEASTABle:ADDNew "TABLE1"'
    assert expected == self.com.get_send_queue()

  def test_set_measurement_statistics_off(self):
    self.com.push_recv_queue(b'TABLE1')
    self.instrument.set_measurement_statistics(False)
    expected = b'MEASTABle:List?'
    assert expected == self.com.get_send_queue()
    expected = b':MEASTABle:DEL "TABLE1"'
    assert expected == self.com.get_send_queue()

  def test_set_measurement(self):
    self.instrument.set_measurement(1, 2, 'rise time')
    expected = b'MEASUrement:MEAS2:TYPE RISETIME'
    assert expected == self.com.get_send_queue()
    expected = b'MEASUrement:MEAS2:SOURCE CH1'
    assert expected == self.com.get_send_queue()

  def test_set_delta_measurement(self):
    self.instrument.set_delta_measurement(4, 1, 2, 'RAISE', 'RAISE')
    expected = b':DISPLAY:WAVEVIEW1:CH1:STATE 1'
    assert expected == self.com.get_send_queue()
    expected = b':DISPLAY:WAVEVIEW1:CH2:STATE 1'
    assert expected == self.com.get_send_queue()
    expected = b'MEASUrement:MEAS4:TYPE DELAY'
    assert expected == self.com.get_send_queue()
    expected = b'MEASUrement:MEAS4:SOURCE1 CH1'
    assert expected == self.com.get_send_queue()
    expected = b'MEASUrement:MEAS4:SOURCE2 CH2'
    assert expected == self.com.get_send_queue()
    expected = b'MEASUrement:MEAS4:FROMedge RISe'
    assert expected == self.com.get_send_queue()
    expected = b'MEASUrement:MEAS4:TOEdge RISe'
    assert expected == self.com.get_send_queue()
    expected = b'MEASUrement:MEAS4:TOEDGESEARCHDIRect FORWard'
    assert expected == self.com.get_send_queue()

  def test_set_cursor(self):
    self.instrument.set_cursor(1, 'HOR', -5, 7)
    expected = b'DISplay:WAVEView1:CURSor:CURSOR1:STATE ON'
    assert expected == self.com.get_send_queue()
    expected = b'DISplay:WAVEView1:CURSor:CURSOR1:ASOUrce CH1'
    assert expected == self.com.get_send_queue()
    expected = b'DISPLAY:WAVEVIEW1:CURSOR:CURSOR1:FUNCTION HBArs'
    assert expected == self.com.get_send_queue()
    expected = b'DISPLAY:WAVEVIEW1:CURSOR:CURSOR1:MODE INDEPENDENT'
    assert expected == self.com.get_send_queue()
    expected = b'DISplay:WAVEView1:CURSor:CURSOR1:HBArs:APOSition -5'
    assert expected == self.com.get_send_queue()
    expected = b'DISplay:WAVEView1:CURSor:CURSOR1:HBArs:BPOSition 7'
    assert expected == self.com.get_send_queue()

  def test_set_infinite_persistence_on(self):
    self.instrument.set_infinite_persistence(True)
    expected = b'DISplay:PERSistence INFInite'
    assert expected == self.com.get_send_queue()

  def test_set_infinite_persistence_off(self):
    self.instrument.set_infinite_persistence(False)
    expected = b'DISplay:PERSistence OFF'
    assert expected == self.com.get_send_queue()

  def test_clear_persistence(self):
    self.instrument.clear_persistence()
    expected = b'DISplay:PERSistence:RESET'
    assert expected == self.com.get_send_queue()

  def test_wait_acquisition_complete(self):
    self.com.push_recv_queue(b'0')
    self.instrument.wait_acquisition_complete(1)
    expected = b'ACQuire:STATE?'
    assert expected == self.com.get_send_queue()

  def test_wait_acquisition_complete_timeout(self):
    self.com.push_recv_queue(b'1')
    self.instrument.wait_acquisition_complete(1)
    expected = b'ACQuire:STATE?'
    assert expected == self.com.get_send_queue()

  def test_get_acquisition(self):
    self.com.push_recv_queue(b'0')
    recv = self.instrument.get_acquisition()
    expected = b'ACQuire:STATE?'
    assert expected == self.com.get_send_queue()
    assert '0' == recv

  def test_arm_single_trig(self):
    self.instrument.arm_single_trig()
    expected = b'ACQuire:STOPAfter SEQuence'
    assert expected == self.com.get_send_queue()
    expected = b'TRIGger:A:MODe Norm'
    assert expected == self.com.get_send_queue()
    expected = b':ACQuire:SEQuence:MODe NUMACQs'
    assert expected == self.com.get_send_queue()
    expected = b':ACQuire:SEQuence:NUMSEQuence 1'
    assert expected == self.com.get_send_queue()
    expected = b'ACQUIRE:STATE ON'
    assert expected == self.com.get_send_queue()

  def test_stop_acquisition(self):
    self.instrument.stop_acquisition()
    expected = b'ACQUIRE:STATE OFF'
    assert expected == self.com.get_send_queue()

  def test_start_acquisition(self):
    self.instrument.start_acquisition()
    expected = b'ACQUIRE:STATE ON'
    assert expected == self.com.get_send_queue()

  def test_reset_measurement_statistics(self):
    self.instrument.reset_measurement_statistics()
    expected = b'CLEAR'
    assert expected == self.com.get_send_queue()

  def test_get_measurement_statistics(self):
    self.com.push_recv_queue(b'11')
    self.com.push_recv_queue(b'22')
    self.com.push_recv_queue(b'33')
    self.com.push_recv_queue(b'44')
    self.com.push_recv_queue(b'55')
    self.com.push_recv_queue(b'66')
    recv = self.instrument.get_measurement_statistics(1)
    expected = b'MEASUrement:MEAS1:RESUlts:CURRentacq:MEAN?'
    assert expected == self.com.get_send_queue()
    expected = b'MEASUrement:MEAS1:RESUlts:ALLAcqs:POPUlation?'
    assert expected == self.com.get_send_queue()
    expected = b'MEASUrement:MEAS1:RESUlts:ALLAcqs:MAXimum?'
    assert expected == self.com.get_send_queue()
    expected = b'MEASUrement:MEAS1:RESUlts:ALLAcqs:MEAN?'
    assert expected == self.com.get_send_queue()
    expected = b'MEASUrement:MEAS1:RESUlts:ALLAcqs:MINimum?'
    assert expected == self.com.get_send_queue()
    expected = b'MEASUrement:MEAS1:RESUlts:ALLAcqs:STDDev?'
    assert expected == self.com.get_send_queue()
    expected = {
        'current_value': 11,
        'count': 22,
        'max': 33,
        'mean': 44,
        'min': 55,
        'std_dev': 66,
    }
    assert expected == recv

  def test_wait_task(self):
    self.com.push_recv_queue(b'1')
    self.instrument.wait_task(1)
    expected = b'*OPC?'
    assert expected == self.com.get_send_queue()

  def test_wait_task_timeout(self):
    self.com.push_recv_queue(b'1999')
    self.instrument.wait_task(1)
    expected = b'*OPC?'
    assert expected == self.com.get_send_queue()

  def test_wait_trigger_ready(self):
    self.com.push_recv_queue(b'REA')
    self.instrument.wait_trigger_ready(1)
    expected = b'TRIGger:STATE?'
    assert expected == self.com.get_send_queue()

  def test_wait_trigger_ready_timeout(self):
    self.com.push_recv_queue(b'AUTO')
    self.instrument.wait_trigger_ready(1)
    expected = b'TRIGger:STATE?'
    assert expected == self.com.get_send_queue()

  def test_fetch_delta_measurement(self):
    self.com.push_recv_queue(b'5487')
    recv = self.instrument.fetch_delta_measurement(
        1, 2, 'RAISE', 'FALL', 51, 52
    )
    expected = b'MEASU:IMMED:GlobalRef 0'
    assert expected == self.com.get_send_queue()
    expected = b'MEASUrement:IMMED:TYPE DELAY'
    assert expected == self.com.get_send_queue()
    expected = b'MEASUREMENT:IMMED:SOURCE1 CH1'
    assert expected == self.com.get_send_queue()
    expected = b'MEASUREMENT:IMMED:SOURCE2 CH2'
    assert expected == self.com.get_send_queue()
    expected = b'MEASUrement:IMMed:REFLevels1:METHod percent'
    assert expected == self.com.get_send_queue()
    expected = b'MEASUrement:IMMed:REFLevels2:METHod percent'
    assert expected == self.com.get_send_queue()
    expected = b'MEASUrement:IMMed:REFLevels1:percent:type custom'
    assert expected == self.com.get_send_queue()
    expected = b'MEASUrement:IMMed:REFLevels2:percent:type custom'
    assert expected == self.com.get_send_queue()
    expected = b'MEASUREMENT:IMMED:DELAY:EDGE1 RISe'
    assert expected == self.com.get_send_queue()
    expected = b'MEASUREMENT:IMMED:DELAY:EDGE2 FALL'
    assert expected == self.com.get_send_queue()
    expected = b'MEASUREMENT:IMMED:REFL1:PERC:RISeMid 51'
    assert expected == self.com.get_send_queue()
    expected = b'MEASUREMENT:IMMED:REFL2:PERC:FALLMid 52'
    assert expected == self.com.get_send_queue()
    expected = b'MEASUrement:IMMED:value?'
    assert expected == self.com.get_send_queue()
    assert 5487 == recv

  def test_fetch_measure_number(self):
    self.com.push_recv_queue(b'MEAS1')
    self.com.push_recv_queue(b'789')
    recv = self.instrument.fetch_measure_number(1)
    expected = b'MEASUrement:LIST?'
    assert expected == self.com.get_send_queue()
    expected = b'MEASUrement:MEAS1:VALUE?'
    assert expected == self.com.get_send_queue()
    assert 789 == recv

  def test_fetch_measure_number_notexist(self):
    self.com.push_recv_queue(b'')
    recv = self.instrument.fetch_measure_number(2)
    expected = b'MEASUrement:LIST?'
    assert expected == self.com.get_send_queue()

  def test_fetch_waveform(self):
    self.com.push_recv_queue(b'10')
    self.com.push_recv_queue(
        b'2;16;ASC;RI;INT;MSB;"Ch1, DC coupling;'
        + b'250000;Y;LIN;"s";400.0E-9;320.1599999971222E-9;'
        + b'125000;"V";781.2500E-9;0.0E+0;'
        + b'-1.2000E-3;TIME;ANALOG;0.0E+0;0.0E+0;0.0E+0;1'
    )
    self.com.push_recv_queue(b'768,512')
    recv = self.instrument.fetch_waveform(1)
    expected = b':DATa:SOUrce CH1'
    assert expected == self.com.get_send_queue()
    expected = b':DATa:START 1'
    assert expected == self.com.get_send_queue()
    expected = b'HORizontal:RECOrdlength?'
    assert expected == self.com.get_send_queue()
    expected = b':DATa:STOP 10.0'
    assert expected == self.com.get_send_queue()
    expected = b':WFMOutpre:ENCdg ASCii'
    assert expected == self.com.get_send_queue()
    expected = b':WFMOutpre:BYT_Nr 8'
    assert expected == self.com.get_send_queue()
    expected = b'WFMOutpre?'
    assert expected == self.com.get_send_queue()
    expected = b':CURVe?'
    assert expected == self.com.get_send_queue()
    info_dict = {
        'points_number': 250000,
        'point_size': 2,
        'trace_info': 'Ch1, DC coupling',
        'x_increment': 4e-07,
        'x_unit': 's',
        'x_origin': 125000.0,
        'y_increment': 7.8125e-07,
        'y_unit': 'V',
        'y_origin': -0.0012,
    }
    curve = '768,512'
    assert [info_dict, curve] == recv

  def test_fetch_waveform_list(self):
    self.com.push_recv_queue(b'10')
    self.com.push_recv_queue(
        b'2;16;ASC;RI;INT;MSB;"Ch1, DC coupling;'
        + b'250000;Y;LIN;"s";400.0E-9;320.1599999971222E-9;'
        + b'125000;"V";781.2500E-9;0.0E+0;'
        + b'-1.2000E-3;TIME;ANALOG;0.0E+0;0.0E+0;0.0E+0;1'
    )
    self.com.push_recv_queue(b'768,512')
    self.com.push_recv_queue(b'20')
    self.com.push_recv_queue(
        b'2;16;ASC;RI;INT;MSB;"Ch2, DC coupling;'
        + b'250000;Y;LIN;"s";400.0E-9;320.1599999971222E-9;'
        + b'125000;"V";781.2500E-9;0.0E+0;'
        + b'-1.2000E-3;TIME;ANALOG;0.0E+0;0.0E+0;0.0E+0;1'
    )
    self.com.push_recv_queue(b'2768,2512')
    recv = self.instrument.fetch_waveform([1, 2])
    expected = b':DATa:SOUrce CH1'
    assert expected == self.com.get_send_queue()
    expected = b':DATa:START 1'
    assert expected == self.com.get_send_queue()
    expected = b'HORizontal:RECOrdlength?'
    assert expected == self.com.get_send_queue()
    expected = b':DATa:STOP 10.0'
    assert expected == self.com.get_send_queue()
    expected = b':WFMOutpre:ENCdg ASCii'
    assert expected == self.com.get_send_queue()
    expected = b':WFMOutpre:BYT_Nr 8'
    assert expected == self.com.get_send_queue()
    expected = b'WFMOutpre?'
    assert expected == self.com.get_send_queue()
    expected = b':CURVe?'
    assert expected == self.com.get_send_queue()
    expected = b':DATa:SOUrce CH2'
    assert expected == self.com.get_send_queue()
    expected = b':DATa:START 1'
    assert expected == self.com.get_send_queue()
    expected = b'HORizontal:RECOrdlength?'
    assert expected == self.com.get_send_queue()
    expected = b':DATa:STOP 20.0'
    assert expected == self.com.get_send_queue()
    expected = b':WFMOutpre:ENCdg ASCii'
    assert expected == self.com.get_send_queue()
    expected = b':WFMOutpre:BYT_Nr 8'
    assert expected == self.com.get_send_queue()
    expected = b'WFMOutpre?'
    assert expected == self.com.get_send_queue()
    expected = b':CURVe?'
    assert expected == self.com.get_send_queue()
    info_dict1 = {
        'points_number': 250000,
        'point_size': 2,
        'trace_info': 'Ch1, DC coupling',
        'x_increment': 4e-07,
        'x_unit': 's',
        'x_origin': 125000.0,
        'y_increment': 7.8125e-07,
        'y_unit': 'V',
        'y_origin': -0.0012,
    }
    info_dict2 = {
        'points_number': 250000,
        'point_size': 2,
        'trace_info': 'Ch2, DC coupling',
        'x_increment': 4e-07,
        'x_unit': 's',
        'x_origin': 125000.0,
        'y_increment': 7.8125e-07,
        'y_unit': 'V',
        'y_origin': -0.0012,
    }
    curve1 = '768,512'
    curve2 = '2768,2512'
    assert [[info_dict1, curve1], [info_dict2, curve2]] == recv

  def test_fetch_measurement(self):
    self.com.push_recv_queue(b'8787')
    recv = self.instrument.fetch_measurement(
        1, instrument.MeasurementType.PEAKTOPEAK
    )
    expected = b'MEASUREMENT:IMMED:TYPE PK2PK'
    assert expected == self.com.get_send_queue()
    expected = b'MEASUrement:IMMED:source CH1'
    assert expected == self.com.get_send_queue()
    expected = b'MEASUrement:IMMED:value?'
    assert expected == self.com.get_send_queue()
    assert 8787 == recv

  def test_load_settings_file(self):
    self.instrument.load_settings_file('HahaThisIsPath')
    expected = b'RECAll:SETUp "HahaThisIsPath"'
    assert expected == self.com.get_send_queue()

  def test_save_settings_file(self):
    self.com.push_recv_queue(b'setting_file')
    self.instrument.save_settings_file('HahaThisIsPath')
    expected = b'SAVE:SETUP "C:/Temp/setting_file.set"'
    assert expected == self.com.get_send_queue()
    expected = b'FILESystem:READFile "C:/Temp/setting_file.set"'
    assert expected == self.com.get_send_queue()
    os.remove('HahaThisIsPath')

  def test_get_screenshot(self):
    self.instrument._get_screenshot('HahaThisIsPath')
    expected = b'SAVe:IMAGe "HahaThisIsPath"'
    assert expected == self.com.get_send_queue()

  def test_save_screenshot(self):
    self.com.push_recv_queue(b'home_dir')
    self.com.push_recv_queue(b'1')
    self.com.push_recv_queue(b'screenshot')
    self.instrument.save_screenshot('HahaThisIsPath')
    expected = b'filesystem:homedir?'
    assert expected == self.com.get_send_queue()
    expected = b'filesystem:cwd home_dir'
    assert expected == self.com.get_send_queue()
    expected = b'SAVe:IMAGe "temp.png"'
    assert expected == self.com.get_send_queue()
    expected = b'*OPC?'
    assert expected == self.com.get_send_queue()
    expected = b'FILESystem:READFile "temp.png"'
    assert expected == self.com.get_send_queue()
    os.remove('HahaThisIsPath')

  def test_auto_set(self):
    self.instrument.auto_set()
    expected = b'AUTOset'
    assert expected == self.com.get_send_queue()

  def test_get_error_status(self):
    self.com.push_recv_queue(b'0')
    self.com.push_recv_queue(b'0,noerror')
    self.instrument.get_error_status()
    expected = b'*ESR?'
    assert expected == self.com.get_send_queue()
    expected = b'EVMsg?'
    assert expected == self.com.get_send_queue()

  def test_get_error_status_esr(self):
    self.com.push_recv_queue(b'1')
    self.com.push_recv_queue(b'0,noerror')
    self.instrument.get_error_status()
    expected = b'*ESR?'
    assert expected == self.com.get_send_queue()
    expected = b'EVMsg?'
    assert expected == self.com.get_send_queue()

  def test_get_error_status_evm(self):
    self.com.push_recv_queue(b'0')
    self.com.push_recv_queue(b'1,yeserror')
    self.instrument.get_error_status()
    expected = b'*ESR?'
    assert expected == self.com.get_send_queue()
    expected = b'EVMsg?'
    assert expected == self.com.get_send_queue()
