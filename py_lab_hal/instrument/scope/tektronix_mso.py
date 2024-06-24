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

"""Child Scope Module of TektronixMSO."""

import dataclasses
import logging
import time

from py_lab_hal.datagram import datagram
from py_lab_hal.instrument import instrument
from py_lab_hal.instrument.scope import scope
from py_lab_hal.util import util

# For Yposition v offset label tracking in pixels
CHAN_YPOS_OFFSET = 18
CHAN_YPOS_PER_DIV = 88


MEASUREMENT_TYPE = {
    instrument.MeasurementType.RISETIME: 'RISETIME',
    instrument.MeasurementType.FALLTIME: 'FallTIME',
    instrument.MeasurementType.FREQUENCY: 'FREQuency',
    instrument.MeasurementType.PERIOD: 'PERiod',
    instrument.MeasurementType.AMPLITUDE: 'AMPLitude',
    instrument.MeasurementType.RMS: 'RMS',
    instrument.MeasurementType.MAX: 'MAXIMUM',
    instrument.MeasurementType.MIN: 'MINIMUM',
    instrument.MeasurementType.HIGH: 'HIGH',
    instrument.MeasurementType.LOW: 'LOW',
    instrument.MeasurementType.PEAKTOPEAK: 'PK2PK',
    instrument.MeasurementType.AVERAGE: 'MEAN',
    instrument.MeasurementType.PULSEWIDTHPOSITIVE: 'PWIDTH',
    instrument.MeasurementType.PULSEWIDTHNEGATIVE: 'NWIdth',
    instrument.MeasurementType.DUTYCYCLEPOSITIVE: 'PDUTY',
    instrument.MeasurementType.DUTYCYCLENEGATIVE: 'NDUty',
    instrument.MeasurementType.OVERSHOOT: 'POVERSHOOT',
    instrument.MeasurementType.UNDERSHOOT: 'NOVershoot',
    instrument.MeasurementType.AREA: 'AREA',
}


CHANNEL_COUPLING = {
    instrument.ChannelCoupling.AC: 'AC',
    instrument.ChannelCoupling.DC: 'DC',
    instrument.ChannelCoupling.DCREJECT: 'DCREJect',
}


EDGE_TRIGGER_COUPLING = {
    instrument.EdgeTriggerCoupling.DC: 'DC',
    instrument.EdgeTriggerCoupling.HFREJECT: 'HFRej',
    instrument.EdgeTriggerCoupling.LFREJECT: 'LFRej',
    instrument.EdgeTriggerCoupling.NOISEREJECT: 'NOISErej',
}


EDGE_TRIGGER_SLOPE = {
    instrument.EdgeTriggerSlope.RISE: 'RISe',
    instrument.EdgeTriggerSlope.FALL: 'FALL',
    instrument.EdgeTriggerSlope.EITHER: 'EITher',
}


EDGE_TRIGGER_MODE = {
    instrument.EdgeTriggerMode.AUTO: 'AUTO',
    instrument.EdgeTriggerMode.NORM: 'NORMal',
}


PULSE_TRIGGER_MODE = {
    instrument.PulseTriggerMode.LESS: 'LESSthan',
    instrument.PulseTriggerMode.MORE: 'MOREthan',
    instrument.PulseTriggerMode.WITHIN: 'WIThin',
    instrument.PulseTriggerMode.OUT: 'OUTside',
}


PULSE_TRIGGER_SLOPE = {
    instrument.PulseTriggerSlope.NEG: 'NEGative',
    instrument.PulseTriggerSlope.POS: 'POSitive',
}


CURSOR_TYPE = {
    instrument.CursorType.VER: 'VBArs',
    instrument.CursorType.HOR: 'HBArs',
}


HORIZONTAL_TYPE = {
    instrument.HorizonType.SAMPLESIZE: 'SAMPLESIZE',
    instrument.HorizonType.SAMPLERATE: 'SAMPLERATE',
}


REFERENCE_TYPE = {
    instrument.ReferenceType.PER: 'PERCent',
    instrument.ReferenceType.ABS: 'ABSolute',
}


REFERENCE_SCOPE = {
    instrument.ReferenceScope.GLOBAL: 'ON',
    instrument.ReferenceScope.LOCAL: 'OFF',
}


TIMEOUT_TRIG_POLARITY = {
    instrument.TimeoutTrigPolarity.STAYHIGH: 'STAYSHigh',
    instrument.TimeoutTrigPolarity.STAYLOW: 'STAYSLow',
    instrument.TimeoutTrigPolarity.EITHER: 'EITher',
}


LAYOUT_STYLE = {
    instrument.LayoutStyle.OVERLAY: 'OVErlay',
    instrument.LayoutStyle.STACK.STACK: 'STACK',
}


class TektronixMSO(scope.Scope):
  """Child Scope Class of TektronixMSO."""

  BANDWIDTH = [2e7, 25e7, 5e8, 1e9]

  SAMPLE_RATE = [
      1.5625,
      2.5,
      3.125,
      5,
      6.25,
      10,
      12.5,
      25,
      31.25,
      50,
      62.5,
      100,
      125,
      250,
      312.5,
      500,
      625,
      1e3,
      1.25e3,
      2.5e3,
      3.125e3,
      5e3,
      6.25e3,
      1e4,
      1.25e4,
      2.5e4,
      3.125e4,
      5e4,
      6.25e4,
      1e5,
      1.25e5,
      2.5e5,
      3.125e5,
      5e5,
      6.25e5,
      1e6,
      1.25e6,
      2.5e6,
      3.125e6,
      5e6,
      6.25e6,
      1.25e7,
      2.5e7,
      3.125e7,
      6.25e7,
      1.25e8,
      2.5e8,
      3.125e8,
      6.25e8,
      1.25e9,
      1.5625e9,
      3.125e9,
      6.25e9,
      1.25e10,
      2.5e10,
      6.25e10,
      1.25e11,
      2.5e11,
      5e11,
  ]

  MAX_HORIZ_OFFSET = 100
  MIN_HORIZ_OFFSET = 0
  MAX_SAMPLESIZE = 5e8
  MIN_SAMPLESIZE = 1e3
  MAX_POSITION = 5
  MIN_POSITION = -5
  NUM_GRATICULE_DIVISION = 10

  def open_instrument(self):
    super().open_instrument()
    self.set_display_style('OVErlay')
    self.data_handler.send(':HEADer 0')
    self.data_handler.send(':VERBose 0')
    # Moved from set_measurement_reference to init
    # These two should be scope wide general settings by default
    self.data_handler.send(':MEASUrement:REFLevels:TYPE GLOBal')
    self.data_handler.send(':MEASUrement:REFLevels:MODE CONTinuous')

  def set_channel_position(self, channel, position):
    self.data_handler.send(
        f'DISplay:WAVEView1:CH{channel}:VERTical:POSition {position:.4e}'
    )
    if position > self.MAX_POSITION:
      logging.warning(
          'Channel %s is set to its maximum value %s.',
          channel,
          self.MAX_POSITION,
      )
    elif position < self.MIN_POSITION:
      logging.warning(
          'Channel %s is set to its minimum value %s.',
          channel,
          self.MIN_POSITION,
      )

  def set_channel_attenuation(self, channel, attenuation_factor):
    self.data_handler.send(
        f'CH{channel}:PRObe:SET ATTENUATION {attenuation_factor}X'
    )

  def set_channel_coupling(self, channel, mode, impedance):
    coupling = util.get_from_dict(CHANNEL_COUPLING, mode)
    self.data_handler.send(f'CH{channel}:COUPling {coupling}')  # AC DC
    if impedance:
      self.data_handler.send(f'CH{channel}:TERmination {impedance}')
    # print(self.data_handler.query(f'CH{channel}:COUPling?'))

  def set_channel_offset(self, channel, voffset):
    # offset label tracking formula
    def calc_label_offset(ch: int, pos: float):
      v_div = float(self.data_handler.query(f'CH{ch}:SCAle?'))
      div = pos / v_div

      return (div * CHAN_YPOS_PER_DIV) + CHAN_YPOS_OFFSET

    # ypos = float(self.data_handler.query(f'CH{ch}:LABel:YPOS?'))
    self.data_handler.send(f'CH{channel}:OFFSet {-voffset:.4e}')  # (V)
    offset = calc_label_offset(channel, voffset)
    self.data_handler.send(f'CH{channel}:LABel:YPOS {offset}')
    # print(self.data_handler.query(f'CH{channel}:OFFSet?'))

  def set_channel_division(self, channel, vdiv):
    self.data_handler.send(
        f'DISplay:WAVEView1:CH{channel}:VERTical:SCAle {vdiv:.4e}'
    )
    # print(self.data_handler.query(f'DISplay:WAVEView1:CH{channel}:VERTical:SCAle?'))

  def set_channel_on_off(self, channel, enable):
    self.data_handler.send(
        f':DISPLAY:WAVEVIEW1:CH{channel}:STATE {int(enable)}'
    )
    # print(self.data_handler.query(f':DISPLAY:WAVEVIEW1:CH{channel}:STATE?'))

  def set_channel_bandwidth(self, channel, value, enable):
    if enable:
      val = util.find_the_nearest(self.BANDWIDTH, value)
      if value not in self.BANDWIDTH:
        logging.warning('The control is set to cloest value %s.', val)
      self.data_handler.send(f'CH{channel}:BANdwidth {val:.4e}')
    else:
      self.data_handler.send(f'CH{channel}:BANdwidth FULL')

  def set_channel_labels(self, channel, value):
    self.data_handler.send(f'CH{channel}:LABel:NAMe "{value}"')

  def set_channel_labels_position(
      self,
      channel,
      x,
      y,
  ):
    self.data_handler.send(f'CH{channel}:LABel:XPOS {x}')  # px
    self.data_handler.send(f'CH{channel}:LABel:YPOS {y}')  # px

  def get_channel_labels(self, channel):
    if isinstance(channel, list):
      labels = []
      for ch in channel:
        label = self.data_handler.query(f'CH{ch}:LABel:NAMe?').strip('"')
        labels.append(label)
    else:
      labels = self.data_handler.query(f'CH{channel}:LABel:NAMe?').strip('"')
    return labels

  def set_vert_range(
      self,
      channel,
      channel_enable,
      vertical_range,
      vertical_offset,
      probe_attenuation,
      vertical_coupling,
  ):
    self.set_channel_on_off(channel, channel_enable)
    self.set_channel_division(
        channel, vertical_range / self.NUM_GRATICULE_DIVISION
    )
    self.set_channel_offset(channel, vertical_offset)
    self.set_channel_attenuation(channel, probe_attenuation)
    vert_coup = util.get_from_dict(CHANNEL_COUPLING, vertical_coupling)
    self.data_handler.send(f'CH{channel}:COUPling {vert_coup}')

  def config_edge_trigger(self, channel, level, edge, mode):
    edg = util.get_from_dict(EDGE_TRIGGER_SLOPE, edge)
    mod = util.get_from_dict(EDGE_TRIGGER_COUPLING, mode)
    self.set_channel_on_off(channel, True)
    self.data_handler.send('TRIGger:A:TYPe EDGE')
    self.data_handler.send(f'TRIGger:A:EDGE:SOUrce CH{channel}')
    self.data_handler.send(f'TRIGger:A:LEvel:CH{channel} {level}')
    self.data_handler.send(f'TRIGger:A:EDGE:SLOpe {edg}')
    self.data_handler.send(f'TRIGger:A:EDGE:COUPling {mod}')

  def set_aux_trigger(self, enable):
    if enable:
      self.data_handler.send('AUXout:SOUrce ATRIGger')
    else:
      self.data_handler.send('AUXout:SOUrce REFOUT')

  def config_continuous_acquisition(self, en_cont_acq, en_auto_trig):
    if en_cont_acq:
      self.data_handler.send('ACQuire:STOPAfter RUNSTop')
    else:
      self.data_handler.send('ACQuire:STOPAfter SEQuence')

    if en_auto_trig:
      self.data_handler.send('TRIGger:A:MODe Auto')
    else:
      self.data_handler.send('TRIGger:A:MODe Norm')

    if en_cont_acq and en_auto_trig:
      self.data_handler.send(':ACQuire:STATE ON')

  def config_rolling_mode(self, enable):
    self.data_handler.query('HORIZONTAL:ROLL?')
    raise AttributeError(
        'MSO56 can only queries the horizontal rolling mode status.'
    )

  def config_pulse_width_trigger(
      self, channel, mode, slope, level, low_limit, hi_limit
  ):
    mod = util.get_from_dict(PULSE_TRIGGER_MODE, mode)
    slo = util.get_from_dict(PULSE_TRIGGER_SLOPE, slope)
    self.set_channel_on_off(channel, True)
    self.data_handler.send('TRIGger:A:TYPe WIDth')
    self.data_handler.send(f'TRIGger:A:PULSEWidth:SOUrce CH{channel}')
    self.data_handler.send(f'TRIGger:A:LEVel:CH{channel} {level}')
    self.data_handler.send(f'TRIGger:A:PULSEWidth:POLarity {slo}')
    self.data_handler.send(f'TRIGger:A:PULSEWidth:WHEn {mod}')
    if mode == instrument.PulseTriggerMode.LESS:
      self.data_handler.send(f'TRIGger:A:PULSEWidth:WIDth {hi_limit}')
    elif mode == instrument.PulseTriggerMode.MORE:
      self.data_handler.send(f'TRIGger:A:PULSEWidth:WIDth {low_limit}')
    elif mode == instrument.PulseTriggerMode.WITHIN:
      self.data_handler.send(f'TRIGger:A:PULSEWidth:HIGHLimit {hi_limit}')
      self.data_handler.send(f'TRIGger:A:PULSEWidth:LOWLimit {low_limit}')
    else:
      self.data_handler.send(f'TRIGger:A:PULSEWidth:HIGHLimit {low_limit}')
      self.data_handler.send(f'TRIGger:A:PULSEWidth:LOWLimit {hi_limit}')
    self.data_handler.send('TRIGger:A:PULSEWidth:LOGICQUALification OFF')

  def config_timeout_trigger(self, channel, polarity, level, timeout):
    pol = util.get_from_dict(TIMEOUT_TRIG_POLARITY, polarity)
    self.data_handler.send('TRIGger:A:TYPe TIMEOut')
    self.data_handler.send(
        f'TRIGger:A:TIMEOut:SOUrce CH{channel}; POLarity {pol}'
    )
    self.data_handler.send(f'TRIGger:A:TIMEOut:TIMe {timeout}')
    self.data_handler.send(f'TRIGger:A:LEVel:CH{channel} {level}')

  def set_horiz_division(self, hor_div, delay, sample_value, sample_type):
    self.data_handler.send('HORizontal:MODE MANual')
    self.data_handler.send('HORizontal:MODe:MANual:CONFIGure RECORDLength')
    if sample_type == instrument.HorizonType.SAMPLESIZE:
      sample_value = sample_value / hor_div / self.NUM_GRATICULE_DIVISION
    self.__set_horiz_samplerate(sample_value)

    self.data_handler.send(f'HORizontal:MODE:SCAle {hor_div:.4e}')
    if delay:
      self.data_handler.send('HORizontal:DELay:MODe On')
      self.data_handler.send(f'HORizontal:DELay:TIMe {-delay}')

  def __set_horiz_samplerate(self, samplerate):
    if samplerate not in self.SAMPLE_RATE:
      sample_rate = util.find_the_nearest(self.SAMPLE_RATE, samplerate)
      logging.warning('Sample rate is set to %s.', sample_rate)
    self.data_handler.send(f'HORizontal:SAMPLERate {samplerate:.4e}')

  def set_horiz_offset(self, hor_offset):
    if hor_offset < self.MIN_HORIZ_OFFSET or hor_offset > self.MAX_HORIZ_OFFSET:
      hor_offset = util.find_the_nearest(
          [self.MIN_HORIZ_OFFSET, self.MAX_HORIZ_OFFSET], hor_offset
      )
      logging.warning('The control is set to cloest value %s.', hor_offset)
    self.data_handler.send(f'HORizontal:POSition {hor_offset:.4e}')

  def _set_meas_reference(self, low, mid, high, r_type, meas_number):
    """Helper internal function to issue reference setting commands."""
    r_type = util.get_from_dict(REFERENCE_TYPE, r_type)
    meas_cmd = f':MEAS{meas_number}'
    self.data_handler.send(f':MEASUrement{meas_cmd}:REFLevels:METHod {r_type}')
    self.data_handler.send(
        f':MEASUrement{meas_cmd}:REFLevels:{r_type}:TYPE CUSTom'
    )
    self.data_handler.send(f':MEASUrement{meas_cmd}:REFLevels:BASETop AUTO')
    self.data_handler.send(
        f'MEASUrement{meas_cmd}:REFLevels:{r_type}:RISELow {low}'
    )
    self.data_handler.send(
        f'MEASUrement{meas_cmd}:REFLevels:{r_type}:FALLLow {low}'
    )
    self.data_handler.send(
        f'MEASUrement{meas_cmd}:REFLevels:{r_type}:RISEMid {mid}'
    )
    self.data_handler.send(
        f'MEASUrement{meas_cmd}:REFLevels:{r_type}:FALLMid {mid}'
    )
    self.data_handler.send(
        f'MEASUrement{meas_cmd}:REFLevels:{r_type}:RISEHigh {high}'
    )
    self.data_handler.send(
        f'MEASUrement{meas_cmd}:REFLevels:{r_type}:FALLHigh {high}'
    )

  def _set_delta_reference(self, mid2, r_type, meas_number):
    """Helper internal function to issue extra ref settings for delta meas."""
    r_type = util.get_from_dict(REFERENCE_TYPE, r_type)
    self.data_handler.send(
        f':MEASUrement:MEAS{meas_number}:REFLevels2:METHod {r_type}'
    )
    self.data_handler.send(
        f'MEASUrement:MEAS{meas_number}:REFLevels2:{r_type}:TYPE CUSTom'
    )
    self.data_handler.send(
        f'MEASUrement:MEAS{meas_number}:REFLevels2:{r_type}:RISEMid {mid2}'
    )
    self.data_handler.send(
        f'MEASUrement:MEAS{meas_number}:REFLevels2:{r_type}:FALLMid {mid2}'
    )

  def set_measurement_reference(
      self, low, mid, high, mid2, reference_type, reference_scope, meas_number
  ):
    # The Global reference here is tracked in PyLabHAL, not in the scope
    # This is because Global reference in TekMSO456 does not allow setting for
    # mid2 for delta measurements unlike previous Tek scopes

    # Check to see if this is a global or local scope
    # If global we want to target all existing measurements that scoped globally
    if reference_scope == instrument.ReferenceScope.GLOBAL:
      for meas, meas_item in self.measurement_item.items():
        m_type = meas_item.meas_type
        # Check to see if there is an existing reference setup in local scope
        # If not, assumes measurement is in default state which is Global
        ref = self.measurement_ref.get(f'{meas}_ref')

        if ref:
          if ref.reference_scope == instrument.ReferenceScope.LOCAL:
            if meas_number != meas:
              continue
          else:
            ref.reference_scope = instrument.ReferenceScope.GLOBAL
        if meas_item.displayed:
          self._set_meas_reference(low, mid, high, reference_type, meas)
          if m_type == 'set_delta_measurement':
            self._set_delta_reference(mid2, reference_type, meas)
    # If Local scope, we only target the specific measurement number
    elif (
        reference_scope == instrument.ReferenceScope.LOCAL
        and meas_number in self.measurement_item
    ):
      if self.measurement_item[meas_number].displayed:
        self._set_meas_reference(low, mid, high, reference_type, meas_number)
        m_type = self.measurement_item[meas_number].meas_type
        if m_type == 'set_delta_measurement':
          self._set_delta_reference(mid2, reference_type, meas_number)

    if reference_scope == instrument.ReferenceScope.GLOBAL:
      meas = 'global'
    else:
      meas = meas_number
    ref = self.ReferenceLevels(
        low, mid, high, mid2, reference_type, reference_scope, meas_number
    )
    self.measurement_ref[f'{meas}_ref'] = ref

  def set_measurement_on_off(self, meas_number, enable):
    if meas_number not in self.measurement_item:
      logging.error('Measure number does not exist')
      return

    if enable:
      self._load_measurement(meas_number)
    else:
      self.data_handler.send(f'MEASUrement:DELete "MEAS{meas_number}"')
      self.measurement_item[meas_number].displayed = False

  def set_measurement_statistics(self, enable):
    if enable:
      self.data_handler.send('MEASTABle:ADDNew "TABLE1"')
      return

    tables = self.data_handler.query('MEASTABle:List?').split(',')
    for table in tables:
      if table != 'NONE':
        self.data_handler.send(f':MEASTABle:DEL "{table}"')

  def set_measurement(self, channel, meas_number, measurement_type):
    mtype = util.get_from_dict(MEASUREMENT_TYPE, measurement_type)
    self.data_handler.send(f'MEASUrement:MEAS{meas_number}:TYPE {mtype}')
    self.data_handler.send(f'MEASUrement:MEAS{meas_number}:SOURCE CH{channel}')
    self.data_handler.send(f'MEASUrement:MEAS{meas_number}:GLOBalref OFF')
    self.measurement_item[meas_number] = scope.Scope.MeasurementConfig(
        meas_type='set_measurement',
        meas_args={
            'channel': channel,
            'meas_number': meas_number,
            'measurement_type': measurement_type,
        },
        displayed=True,
    )
    # Check if there is an existing reference and apply it
    # If new measurement, apply global
    ref = self.measurement_ref.get(f'{meas_number}_ref')

    if ref:
      if ref.reference_scope == instrument.ReferenceScope.LOCAL:
        ch_ref = ref
      elif ref.reference_scope == instrument.ReferenceScope.GLOBAL:
        ch_ref = self.measurement_ref.get('global_ref')
      else:
        raise RuntimeError(
            f'The ref_scope is wrong, we get {ref.reference_scope}.'
        )
    else:
      ch_ref = self.measurement_ref.get('global_ref')

    if ch_ref:
      ch_ref.meas_number = meas_number
      ch_ref_dict = dataclasses.asdict(ch_ref)
      self.set_measurement_reference(**ch_ref_dict)

  def set_delta_measurement(
      self, meas_number, channel1, channel2, start_edge, end_edge
  ):
    startedge = util.get_from_dict(EDGE_TRIGGER_SLOPE, start_edge)
    endedge = util.get_from_dict(EDGE_TRIGGER_SLOPE, end_edge)
    util.loop_channel(self.set_channel_on_off, [channel1, channel2], True)
    self.data_handler.send(f'MEASUrement:MEAS{meas_number}:TYPE DELAY')
    self.data_handler.send(
        f'MEASUrement:MEAS{meas_number}:SOURCE1 CH{channel1}'
    )
    self.data_handler.send(
        f'MEASUrement:MEAS{meas_number}:SOURCE2 CH{channel2}'
    )
    self.data_handler.send(
        f'MEASUrement:MEAS{meas_number}:FROMedge {startedge}'
    )
    self.data_handler.send(f'MEASUrement:MEAS{meas_number}:TOEdge {endedge}')
    self.data_handler.send(
        f'MEASUrement:MEAS{meas_number}:TOEDGESEARCHDIRect FORWard'
    )
    self.data_handler.send(f'MEASUrement:MEAS{meas_number}:GLOBalref OFF')
    self.measurement_item[meas_number] = scope.Scope.MeasurementConfig(
        meas_type='set_delta_measurement',
        meas_args={
            'meas_number': meas_number,
            'channel1': channel1,
            'channel2': channel2,
            'start_edge': start_edge,
            'end_edge': end_edge,
        },
        displayed=True,
    )
    ref = self.measurement_ref.get(f'{meas_number}_ref')

    if ref:
      if ref.reference_scope == instrument.ReferenceScope.LOCAL:
        ch_ref = ref
      elif ref.reference_scope == instrument.ReferenceScope.GLOBAL:
        ch_ref = self.measurement_ref.get('global_ref')
      else:
        raise RuntimeError(
            f'The ref_scope is wrong, we get {ref.reference_scope}.'
        )
    else:
      ch_ref = self.measurement_ref.get('global_ref')

    if ch_ref:
      ch_ref.meas_number = meas_number
      ch_ref_dict = dataclasses.asdict(ch_ref)
      self.set_measurement_reference(**ch_ref_dict)

  def set_cursor(self, channel, cursor_type, cur1_pos, cur2_pos):
    c_type = util.get_from_dict(CURSOR_TYPE, cursor_type)
    self.data_handler.send('DISplay:WAVEView1:CURSor:CURSOR1:STATE ON')
    self.data_handler.send(
        f'DISplay:WAVEView1:CURSor:CURSOR1:ASOUrce CH{channel}'
    )
    self.data_handler.send(
        f'DISPLAY:WAVEVIEW1:CURSOR:CURSOR1:FUNCTION {c_type}'
    )
    self.data_handler.send('DISPLAY:WAVEVIEW1:CURSOR:CURSOR1:MODE INDEPENDENT')
    self.data_handler.send(
        f'DISplay:WAVEView1:CURSor:CURSOR1:{c_type}:APOSition {cur1_pos}'
    )
    self.data_handler.send(
        f'DISplay:WAVEView1:CURSor:CURSOR1:{c_type}:BPOSition {cur2_pos}'
    )

  def set_infinite_persistence(self, enable):
    if enable:
      self.data_handler.send('DISplay:PERSistence INFInite')
    else:
      self.data_handler.send('DISplay:PERSistence OFF')

  def clear_persistence(self):
    self.data_handler.send('DISplay:PERSistence:RESET')

  def wait_acquisition_complete(self, timeout=60):
    time_now = time.time()
    while self.get_acquisition() != '0':
      logging.info('waiting to stop acquisition')
      time.sleep(1)
      if time.time() - time_now > timeout:
        raise RuntimeError('Timeout')

  def get_acquisition(self):
    return self.data_handler.query('ACQuire:STATE?')

  def arm_single_trig(self):
    self.config_continuous_acquisition(False, False)
    self.data_handler.send(':ACQuire:SEQuence:MODe NUMACQs')
    self.data_handler.send(':ACQuire:SEQuence:NUMSEQuence 1')
    self.start_acquisition()

  def stop_acquisition(self):
    self.data_handler.send('ACQUIRE:STATE OFF')

  def start_acquisition(self):
    self.data_handler.send('ACQUIRE:STATE ON')

  def reset_measurement_statistics(self):
    self.data_handler.send('CLEAR')

  def get_measurement_statistics(self, meas_number):
    ans = {}
    ans['current_value'] = float(
        self.data_handler.query(
            f'MEASUrement:MEAS{meas_number}:RESUlts:CURRentacq:MEAN?'
        )
    )
    ans['count'] = float(
        self.data_handler.query(
            f'MEASUrement:MEAS{meas_number}:RESUlts:ALLAcqs:POPUlation?'
        )
    )
    ans['max'] = float(
        self.data_handler.query(
            f'MEASUrement:MEAS{meas_number}:RESUlts:ALLAcqs:MAXimum?'
        )
    )
    ans['mean'] = float(
        self.data_handler.query(
            f'MEASUrement:MEAS{meas_number}:RESUlts:ALLAcqs:MEAN?'
        )
    )
    ans['min'] = float(
        self.data_handler.query(
            f'MEASUrement:MEAS{meas_number}:RESUlts:ALLAcqs:MINimum?'
        )
    )
    ans['std_dev'] = float(
        self.data_handler.query(
            f'MEASUrement:MEAS{meas_number}:RESUlts:ALLAcqs:STDDev?'
        )
    )
    return ans

  def wait_task(self, timeout=30):
    time_now = time.time()
    while self.data_handler.query('*OPC?') != '1':
      logging.info('Wait for all pending OPC operations are finished.')
      time.sleep(1)
      if time.time() - time_now > timeout:
        raise RuntimeError('Timeout')

  def wait_trigger_ready(self, timeout=30):
    time_now = time.time()
    while self.data_handler.query('TRIGger:STATE?') != 'REA':
      logging.info('Wait for the trigger to be armed and ready.')
      time.sleep(1)
      if time.time() - time_now > timeout:
        raise RuntimeError('Timeout')

  def force_trigger(self):
    self.data_handler.send('TRIGger FORCe')

  def fetch_delta_measurement(
      self, channel1, channel2, start_edge, end_edge, mid, mid2
  ):
    start_edge = util.get_from_dict(EDGE_TRIGGER_SLOPE, start_edge)
    end_edge = util.get_from_dict(EDGE_TRIGGER_SLOPE, end_edge)
    self.data_handler.send('MEASU:IMMED:GlobalRef 0')
    self.data_handler.send('MEASUrement:IMMED:TYPE DELAY')
    self.data_handler.send(f'MEASUREMENT:IMMED:SOURCE1 CH{channel1}')
    self.data_handler.send(f'MEASUREMENT:IMMED:SOURCE2 CH{channel2}')
    self.data_handler.send('MEASUrement:IMMed:REFLevels1:METHod percent')
    self.data_handler.send('MEASUrement:IMMed:REFLevels2:METHod percent')
    self.data_handler.send('MEASUrement:IMMed:REFLevels1:percent:type custom')
    self.data_handler.send('MEASUrement:IMMed:REFLevels2:percent:type custom')
    self.data_handler.send(f'MEASUREMENT:IMMED:DELAY:EDGE1 {start_edge}')
    self.data_handler.send(f'MEASUREMENT:IMMED:DELAY:EDGE2 {end_edge}')
    self.data_handler.send(
        f'MEASUREMENT:IMMED:REFL1:PERC:{start_edge}Mid {mid}'
    )
    self.data_handler.send(f'MEASUREMENT:IMMED:REFL2:PERC:{end_edge}Mid {mid2}')
    return float(self.data_handler.query('MEASUrement:IMMED:value?'))

  def fetch_measure_number(self, measure_number):
    measure_list = self.data_handler.query('MEASUrement:LIST?').split(',')
    measure_number = f'MEAS{measure_number}'
    if measure_number in measure_list:
      return float(
          self.data_handler.query(f'MEASUrement:{measure_number}:VALUE?')
      )
    else:
      raise AttributeError('Measure number does not exist.')

  def fetch_waveform(self, channel):
    def get_waveform(channel):
      self.data_handler.send(f':DATa:SOUrce CH{channel}')
      self.data_handler.send(':DATa:START 1')
      length = float(self.data_handler.query('HORizontal:RECOrdlength?'))
      self.data_handler.send(f':DATa:STOP {length}')
      self.data_handler.send(':WFMOutpre:ENCdg ASCii')
      self.data_handler.send(':WFMOutpre:BYT_Nr 8')
      info_get = self.data_handler.query('WFMOutpre?').split(';')
      info_list = [item.strip(' "') for item in info_get]

      info_dict = {}
      info_dict['points_number'] = int(info_list[7])
      info_dict['point_size'] = int(info_list[0])
      info_dict['trace_info'] = info_list[6]
      info_dict['x_increment'] = float(info_list[11])
      info_dict['x_unit'] = info_list[10]
      info_dict['x_origin'] = float(info_list[13])
      info_dict['y_increment'] = float(info_list[15])
      info_dict['y_unit'] = info_list[14]
      info_dict['y_origin'] = float(info_list[17])
      return info_dict, self.data_handler.query(':CURVe?')

    if isinstance(channel, list):
      waveform = []
      for ch in channel:
        info, curve = get_waveform(ch)
        waveform.append([info, curve])
    else:
      waveform = list(get_waveform(channel))
    return waveform

  def set_search_edges_on_off(self, enable):
    if enable:
      search_cmd = 'SEARCH:ADDNEW “SEARCH1”'
    else:
      search_cmd = 'SEARCH:DELETEALL'
    self.data_handler.send(search_cmd)

  def set_search_edges(self, channel, edge, level):
    slope = util.get_from_dict(EDGE_TRIGGER_SLOPE, edge)
    self.data_handler.send('SEARCH:SEARCH1:TRIGger:A:TYPe EDGE')
    self.data_handler.send(f'SEARCH:SEARCH1:TRIGger:A:EDGE:SLOpe {slope}')
    self.data_handler.send(f'SEARCH:SEARCH1:TRIGger:A:EDGE:SOUrce CH{channel}')
    self.data_handler.send(f'SEARCH:SEARCH1:TRIGger:A:EDGE:THReshold {level}')

  def get_search_edges(self, start_index=0, count=-1):
    self.data_handler.send('searchtable:addnew "TABLE2"')
    home_dir = self.data_handler.query('filesystem:homedir?')
    self.data_handler.send(f'filesystem:cwd {home_dir}')
    temp_file = 'search_result.csv'
    self.data_handler.send(f'SAVe:EVENTtable:SEARCHTable "{temp_file}"')
    self.wait_task()
    self.data_handler.send(f'FILESystem:READFile "{temp_file}"')
    temp_list = self.data_handler.recv()
    # Data starts at the 6th line
    temp_list = temp_list.split('\r\n')[5:]
    x_list = [float(x.split(',')[0]) for x in temp_list]
    self.data_handler.send(f'FILESystem:DELEte "{temp_file}"')
    self.data_handler.send('searchtable:delete "TABLE2"')
    if x_list:
      try:
        if count == -1:
          return_list = x_list[start_index:]
        else:
          return_list = x_list[start_index : start_index + count]
        return return_list
      except IndexError:
        pass
    else:
      # TODO: b/333307624 - Fix empty list return.
      return []  # pytype: disable=bad-return-type

  def load_settings_file(self, path):
    # TODO: b/333307803 - transfer setup file from pc to scope.
    self.data_handler.send(f'RECAll:SETUp "{path}"')
    self.wait_task()

  def save_settings_file(self, path):
    temp_path = 'C:/Temp/setting_file.set'
    self.data_handler.send(f'SAVE:SETUP "{temp_path}"')
    self.data_handler.send(f'FILESystem:READFile "{temp_path}"')
    with open(path, 'wb+') as f:
      f.write(self.data_handler.recv_raw())
    # self.data_handler.send(f'FILESystem:DELEte "{temp_path}"')

  def _cd_home(self):
    home_dir = self.data_handler.query('filesystem:homedir?')
    self.data_handler.send(f'filesystem:cwd {home_dir}')

  def _get_screenshot(self, path):
    self.data_handler.send(f'SAVe:IMAGe "{path}"')
    self.wait_task()

  def save_screenshot(self, path):
    file_name = 'temp.png'
    self._cd_home()
    self._get_screenshot(file_name)
    self.save_file(file_name, path, file_type='png')

  def add_plot(self, plot_type: str, plot_number: int, meas_number: int):
    channel = self.measurement_item[meas_number].meas_args['channel']

    self.data_handler.send(f'PLOT:ADDNew PLOT{plot_number}')
    self.data_handler.send(f'PLOT:PLOT{plot_number}:TYPe {plot_type}')
    self.data_handler.send(
        f'PLOT:PLOT{plot_number}:SOUrce{channel} MEAS{meas_number}'
    )

  def save_plot(self, plot_number: int, path: str):
    self._cd_home()
    self.data_handler.send(f'DISplay:SELect:VIEW PLOTVIEW{plot_number}')
    file_name = 'temp.csv'
    self.data_handler.send(f'SAVe:PLOTData "{file_name}"')
    self.wait_task()
    self.save_file(file_name, path)

  def _read_file(self, file: str):
    self.data_handler.send(f'FILESystem:READFile "{file}"')

    if self.inst.connect_config.interface_type == 'socket':
      self.data_handler.send('!r')

  def save_file(self, file_name: str, path: str, file_type: str = ''):
    self._read_file(file_name)

    if file_type == 'png':
      self._save_png_file(path)
    else:
      with open(path, 'wb+') as f:
        f.write(self.data_handler.recv_raw())

  def _save_png_file(self, path: str):
    png_dg = self.data_handler.recv_dataram(datagram.PngDatagram())
    with open(path, 'wb+') as f:
      f.write(png_dg.data)

  def auto_set(self):
    self.data_handler.send('AUTOset')

  def auto_scale(self, channel: int):
    self.stop_acquisition()
    self.set_horiz_division(0.01, 0, 1e6, instrument.HorizonType.SAMPLERATE)
    self.data_handler.send(f':DISPLAY:WAVEVIEW1:CH{channel}:STATE 1')
    self.set_channel_division(channel, 10)
    self.set_channel_offset(channel, 0)

    self.start_acquisition()

    for _ in range(2):
      a = self.fetch_measurement(channel, 'AMPlITUDE')
      self.stop_acquisition()
      self.set_channel_division(channel, float(f'{a / 3:0.3e}'))
      self.start_acquisition()

    period = self.fetch_measurement(channel, 'PERIOD')
    self.set_horiz_division(period, 0, 1e6, instrument.HorizonType.SAMPLERATE)

  def auto_trigger(
      self,
      channel: int,
      edge: instrument.EdgeTriggerSlope,
      mode: instrument.EdgeTriggerCoupling,
      scale: bool,
  ):
    if scale:
      self.auto_scale(channel)
    a = self.fetch_measurement(channel, 'AMPlITUDE')
    l = self.fetch_measurement(channel, 'LOW')
    self.config_edge_trigger(channel, a / 2 + l, edge, mode)

  def fetch_measurement(self, channel, measurement_type):
    mtype = util.get_from_dict(MEASUREMENT_TYPE, measurement_type)
    self.data_handler.send(f'MEASUREMENT:IMMED:TYPE {mtype}')
    self.data_handler.send(f'MEASUrement:IMMED:source CH{channel}')
    return float(self.data_handler.query('MEASUrement:IMMED:value?'))

  def set_display_style(self, mode):
    # {OVErlay|STAcked}
    layout_style = util.get_from_dict(LAYOUT_STYLE, mode)
    self.data_handler.send(f'DISplay:WAVEView1:VIEWStyle {layout_style}')

  def get_error_status(self):
    esr = self.event_status_register()
    evm = int(self.data_handler.query('EVMsg?').split(',')[0])
    if esr:
      raise AttributeError(f'Standard Event Error: {esr}')
    if evm:
      raise AttributeError(f'Event Queue Error: {evm}')
