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

"""Child Scope Module of Lecroy."""

import logging
import math
import struct
import time

from py_lab_hal.instrument import instrument
from py_lab_hal.instrument.scope import scope
from py_lab_hal.util import util

CHANNEL_COUPLING = {
    'RP': {
        instrument.ChannelCoupling.DC: 'DC',
        instrument.ChannelCoupling.GROUND: 'GND',
    },
    'CP': {
        instrument.ChannelCoupling.DC: 'DC',
        instrument.ChannelCoupling.AC: 'AC',
        instrument.ChannelCoupling.GROUND: 'GND',
    },
    'ZD': {
        instrument.ChannelCoupling.DC: 'DC120k',
        instrument.ChannelCoupling.GROUND: 'GND',
    },
    'RI': {
        instrument.ChannelCoupling.DC: ['D50', 'D1M'],
        instrument.ChannelCoupling.AC: 'A1M',
        instrument.ChannelCoupling.GROUND: 'GND',
    },
}

BANDWIDTH = {
    20e6: '20M',
    200e6: '200M',
}

PULSE_TRIGGER_MODE = {
    instrument.PulseTriggerMode.LESS: 'LESS',
    instrument.PulseTriggerMode.MORE: 'MORE',
    instrument.PulseTriggerMode.WITHIN: 'WITHIN',
    instrument.PulseTriggerMode.OUT: 'OUT',
}
PULSE_TRIGGER_SLOPE = {
    instrument.PulseTriggerSlope.NEG: 'NEG',
    instrument.PulseTriggerSlope.POS: 'POS',
}
EDGE_TRIGGER_COUPLING = {
    instrument.EdgeTriggerCoupling.AC: 'AC',
    instrument.EdgeTriggerCoupling.DC: 'DC',
    instrument.EdgeTriggerCoupling.HFREJECT: 'HFREJ',
    instrument.EdgeTriggerCoupling.LFREJECT: 'LFREJ',
}
EDGE_TRIGGER_SLOPE = {
    instrument.EdgeTriggerSlope.RISE: 'POS',
    instrument.EdgeTriggerSlope.FALL: 'NEG',
    instrument.EdgeTriggerSlope.EITHER: 'EIT',
}
CURSOR_TYPE = {
    instrument.CursorType.VER: ['HREL', 'HREF', 'HDIF'],
    instrument.CursorType.HOR: ['VREL', 'VREF', 'VDIF'],
}
DELTA_SLOPE = {
    instrument.DeltSlope.RISE: 'POS',
    instrument.DeltSlope.FALL: 'NEG',
    instrument.DeltSlope.EITHER: 'EIT',
}
MEASUREMENT_TYPE = {
    instrument.MeasurementType.RISETIME: 'RLEV',
    instrument.MeasurementType.FALLTIME: 'FLEV',
    instrument.MeasurementType.FREQUENCY: 'FREQ',
    instrument.MeasurementType.PERIOD: 'PER',
    instrument.MeasurementType.AMPLITUDE: 'AMPL',
    instrument.MeasurementType.RMS: 'RMS',
    instrument.MeasurementType.MAX: 'MAX',
    instrument.MeasurementType.MIN: 'MIN',
    instrument.MeasurementType.HIGH: 'TOP',
    instrument.MeasurementType.LOW: 'BASE',
    instrument.MeasurementType.PEAKTOPEAK: 'PKPK',
    instrument.MeasurementType.AVERAGE: 'MEAN',
    instrument.MeasurementType.PULSEWIDTHPOSITIVE: 'POS',
    instrument.MeasurementType.PULSEWIDTHNEGATIVE: 'NEG',
    instrument.MeasurementType.DUTYCYCLEPOSITIVE: 'POS',
    instrument.MeasurementType.DUTYCYCLENEGATIVE: 'NEG',
    instrument.MeasurementType.OVERSHOOT: 'OVSP',
    instrument.MeasurementType.UNDERSHOOT: 'OVSN',
    instrument.MeasurementType.AREA: 'AREA',
    instrument.MeasurementType.RISINGEDGECOUNT: 'POS',
    instrument.MeasurementType.FALLINGEDGECOUNT: 'NEG',
}
HORIZONTAL_TYPE = {
    instrument.HorizonType.SAMPLESIZE: 'SAMPLESIZE',
    instrument.HorizonType.SAMPLERATE: 'SAMPLERATE',
}
REFERENCE_TYPE = {
    instrument.ReferenceType.PER: 'PCT',
    instrument.ReferenceType.ABS: 'V',
}
TIMEOUT_TRIG_POLARITY = {
    instrument.TimeoutTrigPolarity.STAYHIGH: 'POS',
    instrument.TimeoutTrigPolarity.STAYLOW: 'NEG',
    instrument.TimeoutTrigPolarity.EITHER: 'POS',
}


class LecroyMAUI(scope.Scope):
  """Child Scope Class of Lecory."""

  SAMPLE_RATE = [
      1e3,
      2.5e3,
      5e3,
      1e4,
      2.5e4,
      5e4,
      1e5,
      2.5e5,
      5e5,
      1e6,
      2.5e6,
      5e6,
      1e7,
      2.5e7,
      5e7,
      1e8,
      2.5e8,
      5e8,
      1.25e9,
      2.5e9,
      5e9,
      1e10,
  ]

  SAMPLE_SIZE = [
      5e2,
      1e3,
      2.5e3,
      5e3,
      1e4,
      2.5e4,
      5e4,
      1e5,
      2.5e5,
      5e5,
      1e6,
      2.5e6,
      5e6,
      1e7,
      2.5e7,
      5e7,
  ]

  MAX_ATTENUATION = 1e5
  MIN_ATTENUATION = 1
  NUM_GRATICULE_DIVISION = 8
  NUM_TIME_DIVISION = 10
  HYSTERESIS = 0.5

  def open_instrument(self):
    super().open_instrument()
    self.scope_name = self.idn.split(',')[1]
    self.data_handler.send('COMM_HEADER OFF')
    # Set to single grid like traditional scope display instead of stacked
    self.data_handler.send('GRID SINGLE')

  def set_channel_position(self, channel, position):
    raise NotImplementedError('Function not support by the device.')

  def set_channel_attenuation(self, channel, attenuation_factor):
    # TODO: b/333308752 - Investigate need for a probe attenuation table.

    if self.MIN_ATTENUATION <= attenuation_factor <= self.MAX_ATTENUATION:
      self.data_handler.send(f'C{channel}:ATTN {attenuation_factor}')
    else:
      logging.warning('Setting value out of range.')

  def set_channel_coupling(self, channel, mode, impedance=None):
    probe_name = self.data_handler.query(f'C{channel}:PRNA?')[0:2]
    mod_dict = util.get_from_dict(CHANNEL_COUPLING, probe_name)
    mode_cmd = util.get_from_dict(mod_dict, mode)
    if probe_name == 'RI' and mode == instrument.ChannelCoupling.DC:
      mode_cmd = mode_cmd[impedance == 1e6]
    self.data_handler.send(f'C{channel}:COUPLING {mode_cmd}')

  def set_channel_offset(self, channel, voffset):
    self.data_handler.send(f'C{channel}:OFFSET {-voffset:.3f}')

  def set_channel_division(self, channel, vdiv):
    self.data_handler.send(f'C{channel}:VDIV {vdiv:.3f}')

  def set_channel_on_off(self, channel, enable):
    if enable:
      self.data_handler.send(f'C{channel}:TRA ON')
    else:
      self.data_handler.send(f'C{channel}:TRA OFF')

  def set_channel_bandwidth(self, channel, value, enable):
    if enable:
      val = util.find_the_nearest(BANDWIDTH, value)
      if value not in BANDWIDTH:
        logging.info('Bandwidth is set to the nearest value %s', val)
      self.data_handler.send(f'BWL C{channel},{BANDWIDTH[val]}HZ')
    else:
      self.data_handler.send(f'BWL C{channel},OFF')
      # self.data_handler.query(f'C{ch}:BWL?')

  def set_channel_labels(self, channel, value):
    self.data_handler.send(
        f"VBS 'app.Acquisition.C{channel}.ViewLabels = True'"
    )
    self.data_handler.send(
        f'VBS \'app.Acquisition.C{channel}.LabelsText = "{value}"\''
    )

  def set_channel_labels_position(self, channel, x, y):
    self.data_handler.send(
        f'VBS \'app.Acquisition.C{channel}.LabelsPosition = "{x}|{y}"\''
    )

  def get_channel_labels(self, channel):
    return self.data_handler.query(
        f"VBS? 'return = app.Acquisition.C{channel}.LabelsText'"
    )

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
    self.set_channel_coupling(channel, vertical_coupling)

  def config_edge_trigger(self, channel, level, edge, mode):
    edg = util.get_from_dict(EDGE_TRIGGER_SLOPE, edge)
    mod = util.get_from_dict(EDGE_TRIGGER_COUPLING, mode)
    self.set_channel_on_off(channel, True)
    self.data_handler.send(f'TRSE EDGE,SR,C{channel}')
    self.data_handler.send(f'C{channel}:TRLV {level}')
    self.data_handler.send(f'C{channel}:TRSL {edg}')
    self.data_handler.send(f'C{channel}:TRCP {mod}')

  def set_aux_trigger(self, enable):
    if enable:
      self.data_handler.send('COUT TRIG')
    else:
      self.data_handler.send('COUT OFF')

  def config_continuous_acquisition(self, en_cont_acq, en_auto_trig):
    if en_cont_acq:
      if en_auto_trig:
        self.data_handler.send('TRMD AUTO')
      else:
        self.data_handler.send('TRMD NORM')
    else:
      self.data_handler.send('TRMD STOP')

  def config_rolling_mode(self, enable):
    raise NotImplementedError(
        'This scope does not support disabling of roll mode.'
    )

  def config_pulse_width_trigger(
      self, channel, mode, slope, level, low_limit, hi_limit
  ):
    slo = util.get_from_dict(PULSE_TRIGGER_SLOPE, slope)
    self.data_handler.send(f'C{channel}:TRLV {level}')
    self.data_handler.send(f'C{channel}:TRSL {slo}')
    if mode == instrument.PulseTriggerMode.LESS:
      self.data_handler.send(f'TRSE WIDTH,SR,C{channel},HT,PS,HV,{hi_limit}')
    elif mode == instrument.PulseTriggerMode.MORE:
      self.data_handler.send(f'TRSE WIDTH,SR,C{channel},HT,PL,HV,{low_limit}')
    elif mode == instrument.PulseTriggerMode.WITHIN:
      self.data_handler.send(
          f'TRSE WIDTH,SR,C{channel},HT,P2,HV,{low_limit},HV2,{hi_limit}'
      )
    elif mode == instrument.PulseTriggerMode.OUT:
      self.data_handler.send(
          f'TRSE WIDTH,SR,C{channel},HT,P2,HV,{hi_limit},HV2,{low_limit}'
      )
    else:
      raise AttributeError('User input error')

  def config_timeout_trigger(
      self,
      channel: int,
      polarity: str,
      level: float,
      timeout: float,
  ) -> None:
    pol = util.get_from_dict(TIMEOUT_TRIG_POLARITY, polarity)
    ignore_last_edge = 'false'
    if polarity == instrument.TimeoutTrigPolarity.EITHER:
      # If it is either, it doesn't matter what edge we set, we need to
      # toggle another setting
      ignore_last_edge = 'true'
    self.data_handler.send(f'C{channel}:TRLV {level}')
    self.data_handler.send(f'C{channel}:TRSL {pol}')
    self.data_handler.send(f'TRSE DROP,SR,C{channel},HT,TI,HV,{timeout}')
    self.data_handler.send(
        "vbs 'app.Acquisition.Trigger.Dropout.IgnoreLastEdge = "
        f"{ignore_last_edge}'"
    )

  def set_horiz_division(self, hor_div, delay, sample_value, sample_type):
    self.data_handler.send(f'TDIV {hor_div:.3f}')
    self.data_handler.send(f'TRDL {delay:.3f}')
    if sample_type == instrument.HorizonType.SAMPLESIZE:
      if sample_value not in self.SAMPLE_SIZE:
        sample_value = util.find_the_nearest(self.SAMPLE_SIZE, sample_value)
      self.data_handler.send(
          "vbs 'app.Acquisition.Horizontal.Maximize = " + '"SetMaximumMemory"\''
      )
      self.data_handler.send(f'MSIZ {sample_value:.3f}')
    else:
      if sample_value not in self.SAMPLE_RATE:
        sample_value = util.find_the_nearest(self.SAMPLE_RATE, sample_value)
      self.data_handler.send(
          "vbs 'app.Acquisition.Horizontal.Maximize = " + '"FixedSampleRate"\''
      )
      self.data_handler.send(
          "vbs 'app.Acquisition.Horizontal.SampleRate = "
          + f'"{sample_value}"\''
      )

  def set_horiz_offset(self, hor_offset):
    self.data_handler.send(
        "VBS 'app.Acquisition.C1.Out.Result.HorizontalOffset = "
        + f"{hor_offset:.3f}'"
    )

  def set_measurement_reference(
      self, low, mid, high, mid2, reference_type, reference_scope, meas_number
  ):
    if reference_scope == instrument.ReferenceScope.GLOBAL:
      meas = 'global'
    else:
      meas = meas_number
    ref = scope.Scope.ReferenceLevels(
        low, mid, high, mid2, reference_type, reference_scope, meas_number
    )
    self.measurement_ref[f'{meas}_ref'] = ref

    # Check to see if this is a global or local scope
    # If global we want to target all existing measurements that scoped globally
    if reference_scope == instrument.ReferenceScope.GLOBAL:
      for meas in self.measurement_item:
        # Check to see if there is an existing reference setup in local scope
        # If not, assumes measurement is in default state which is Global
        ref = self.measurement_ref.get(f'{meas}_ref')

        if ref:
          if ref.reference_scope == instrument.ReferenceScope.LOCAL:
            if meas_number != meas:
              continue
            else:
              ref.reference_scope = instrument.ReferenceScope.GLOBAL
        self._load_measurement(meas)

    # If Local scope, we target the specific measurement number if it exists
    elif (
        reference_scope == instrument.ReferenceScope.LOCAL
        and meas_number in self.measurement_item
    ):
      self._load_measurement(meas_number)

  def set_measurement_on_off(self, meas_number, enable):
    self.data_handler.send('VBS \'app.measure.measureset = "CUST"\'')
    if enable:
      self.data_handler.send("VBS 'app.measure.showmeasure = TRUE'")
    else:
      self.data_handler.send("VBS 'app.measure.showmeasure = FALSE'")

    if enable:
      self.data_handler.send(f"VBS 'app.measure.p{meas_number}.view = TRUE'")
    else:
      self.data_handler.send(f"VBS 'app.measure.p{meas_number}.view = FALSE'")

  def set_measurement_statistics(self, enable):
    if enable:
      self.data_handler.send("VBS 'app.Measure.StatsOn = TRUE'")
    else:
      self.data_handler.send("VBS 'app.Measure.StatsOn = FALSE'")

  def set_measurement(self, channel, meas_number, measurement_type):
    self.data_handler.send(f"VBS 'app.Acquisition.C{channel}.View = True'")
    self.set_measurement_on_off(meas_number, True)
    mtype = util.get_from_dict(MEASUREMENT_TYPE, measurement_type)
    ch_ref = self.measurement_ref.get(f'{meas_number}_ref')

    if ch_ref:
      if ch_ref.reference_scope == instrument.ReferenceScope.LOCAL:
        ref = ch_ref
      else:
        ref = self.measurement_ref['global_ref']
    else:
      ref = self.measurement_ref['global_ref']
    rtype = util.get_from_dict(REFERENCE_TYPE, ref.reference_type)
    if measurement_type == instrument.MeasurementType.RISETIME:
      self.data_handler.send(
          f'PACU {meas_number},{mtype},C{channel},{ref.low}'
          f' {rtype},{ref.high} {rtype}'
      )
    elif measurement_type == instrument.MeasurementType.FALLTIME:
      self.data_handler.send(
          f'PACU {meas_number},{mtype},C{channel},{ref.high}'
          f' {rtype},{ref.low} {rtype}'
      )
    elif (
        measurement_type == instrument.MeasurementType.PULSEWIDTHPOSITIVE
        or measurement_type == instrument.MeasurementType.PULSEWIDTHNEGATIVE
    ):
      self.data_handler.send(
          f'PACU {meas_number},WIDLV,C{channel},{mtype},{ref.mid} {rtype}'
      )
    elif (
        measurement_type == instrument.MeasurementType.RISINGEDGECOUNT
        or measurement_type == instrument.MeasurementType.FALLINGEDGECOUNT
    ):
      self.data_handler.send(
          f'PACU {meas_number},EDLEV,C{channel},{mtype},{ref.mid} {rtype}'
      )
    elif (
        measurement_type == instrument.MeasurementType.DUTYCYCLEPOSITIVE
        or measurement_type == instrument.MeasurementType.DUTYCYCLENEGATIVE
    ):
      self.data_handler.send(
          f'PACU {meas_number},DULEV,C{channel},{mtype},{ref.mid} {rtype}'
      )
    else:
      self.data_handler.send(f'PACU {meas_number},{mtype},C{channel}')

    self.measurement_item[meas_number] = self.MeasurementConfig(
        meas_type='set_measurement',
        meas_args={
            'channel': channel,
            'meas_number': meas_number,
            'measurement_type': measurement_type,
        },
        displayed=False,
    )

  def set_delta_measurement(
      self, meas_number, channel1, channel2, start_edge, end_edge
  ):
    s_slope = util.get_from_dict(DELTA_SLOPE, start_edge)
    e_slope = util.get_from_dict(DELTA_SLOPE, end_edge)
    ch_ref = self.measurement_ref.get(f'{meas_number}_ref')

    if ch_ref:
      if ch_ref.reference_scope == instrument.ReferenceScope.LOCAL:
        ref = ch_ref
      else:
        ref = self.measurement_ref['global_ref']
    else:
      ref = self.measurement_ref['global_ref']
    rtype = util.get_from_dict(REFERENCE_TYPE, ref.reference_type)
    self.data_handler.send(
        f'PACU {meas_number},DTLEV,C{channel1},{s_slope}'
        f',{ref.mid} {rtype},{self.HYSTERESIS} DIV,C{channel2},{e_slope}'
        f',{ref.mid2} {rtype},{self.HYSTERESIS} DIV'
    )
    self.measurement_item[meas_number] = self.MeasurementConfig(
        meas_type='set_delta_measurement',
        meas_args={
            'meas_number': meas_number,
            'channel1': channel1,
            'channel2': channel2,
            'start_edge': start_edge,
            'end_edge': end_edge,
        },
        displayed=False,
    )

  def set_cursor(self, channel, cursor_type, cur1_pos, cur2_pos):
    c_type = util.get_from_dict(CURSOR_TYPE, cursor_type)
    self.data_handler.send(f'CRS {c_type[0]}')
    if c_type[0] == 'VREL':
      tdiv = float(self.data_handler.query(f'C{channel}:VDIV?'))
      trdl = float(self.data_handler.query(f'C{channel}:OFST?'))
      ref = trdl / tdiv + cur1_pos / tdiv
      dif = trdl / tdiv + cur2_pos / tdiv
    else:
      vdiv = float(self.data_handler.query('TDIV?'))
      ofst = float(self.data_handler.query('TRDL?'))
      ref = self.NUM_TIME_DIVISION / 2 + ofst / vdiv + cur1_pos / vdiv
      dif = self.NUM_TIME_DIVISION / 2 + ofst / vdiv + cur2_pos / vdiv
    self.data_handler.send(
        f'C{channel}:CRST {c_type[1]},{ref},{c_type[2]},{dif}'
    )

  def set_infinite_persistence(self, enable):
    if enable:
      self.data_handler.send('PERSIST ON')
      self.data_handler.send('PESU infinite,ALL')
    else:
      self.data_handler.send('PERSIST OFF')

  def clear_persistence(self):
    self.data_handler.send("VBS 'app.Display.ClearSweeps'")

  def wait_acquisition_complete(self, timeout=60):
    time_now = time.time()
    while self.get_acquisition() != '1':
      logging.info('waiting to stop acquisition')
      time.sleep(1)
      if time.time() - time_now > timeout:
        raise RuntimeError('Timeout')

  def get_acquisition(self):
    return self.data_handler.query('INR?')

  def arm_single_trig(self):
    self.data_handler.send('TRMD STOP')
    self.data_handler.send('*CLS')
    self.data_handler.send('ARM')

  def stop_acquisition(self):
    self.data_handler.send('STOP')

  def start_acquisition(self):
    self.data_handler.send('TRMD AUTO')

  def reset_measurement_statistics(self):
    self.data_handler.send("VBS 'app.Measure.ClearSweeps'")

  def get_measurement_statistics(self, meas_number):
    ans = {}
    meas_set = {
        'MyMeasure': 'CUST',
        'StdHorizontal': 'HPAR',
        'StdVertical': 'VPAR',
    }
    if self.data_handler.query("VBS? 'return=app.Measure.ShowMeasure'") != '-1':
      self.data_handler.send("VBS 'app.Measure.ShowMeasure = True'")
    ms = self.data_handler.query("VBS? 'return=app.Measure.MeasureSet'")
    data = self.data_handler.query(
        f"PAST? {meas_set[ms]}, P{meas_number};VBS? 'return=app.Measure."
        + f"P{meas_number}.Out.Result.StatusDescription'"
    ).split(',')
    skip = data[15].find(';')
    ans['current_value'] = float(data[9])
    ans['count'] = float(data[15][:skip])
    ans['max'] = float(data[7])
    ans['mean'] = float(data[5])
    ans['min'] = float(data[11])
    ans['std_dev'] = float(data[13])
    return ans

  def wait_task(self, timeout=30):
    status = self.data_handler.query(
        f"vbs? 'return=app.WaitUntilIdle({timeout})'"
    )
    if status == '0':
      raise RuntimeError('Timeout')

  def wait_trigger_ready(self, timeout=30):
    self.wait_task(timeout)

  def force_trigger(self):
    self.data_handler.send('FORCE_TRIGGER')

  def fetch_delta_measurement(
      self, channel1, channel2, start_edge, end_edge, mid, mid2
  ):
    start_edge = util.get_from_dict(EDGE_TRIGGER_SLOPE, start_edge)
    end_edge = util.get_from_dict(EDGE_TRIGGER_SLOPE, end_edge)
    pacu = self.data_handler.query('PACU? 1')
    skip = pacu.find(',')
    self.data_handler.send(
        f'PACU 1,DTLEV,C{channel1},{start_edge},{mid} PCT,'
        f'C{channel2},{end_edge},{mid2} PCT'
    )
    val = self.data_handler.query('PAVA? CUST1')
    val = val.split(',')[1]
    if val == 'UNDEF':
      val = math.nan
    else:
      val = float(val)
    self.data_handler.send(f'PACU 1,{pacu[skip + 1:]}')
    return val

  def fetch_measurement(self, channel, measurement_type):
    mtype = util.get_from_dict(MEASUREMENT_TYPE, measurement_type)
    pacu = self.data_handler.query('PACU? 1')
    skip = pacu.find(',')
    global_ref = self.measurement_ref['global_ref']
    if (
        measurement_type == instrument.MeasurementType.RISETIME
        or measurement_type == instrument.MeasurementType.FALLTIME
    ):
      self.data_handler.send(
          f'PACU 1,{mtype},C{channel},{global_ref.low}'
          f' PCT,{global_ref.high} PCT'
      )
    elif (
        measurement_type == instrument.MeasurementType.PULSEWIDTHPOSITIVE
        or measurement_type == instrument.MeasurementType.PULSEWIDTHNEGATIVE
    ):
      self.data_handler.send(
          f'PACU 1,WIDLV,C{channel},{mtype},{global_ref.mid} PCT'
      )
    elif (
        measurement_type == instrument.MeasurementType.RISINGEDGECOUNT
        or measurement_type == instrument.MeasurementType.FALLINGEDGECOUNT
    ):
      self.data_handler.send(
          f'PACU 1,EDLEV,C{channel},{mtype},{global_ref.mid} PCT'
      )
    elif (
        measurement_type == instrument.MeasurementType.DUTYCYCLEPOSITIVE
        or measurement_type == instrument.MeasurementType.DUTYCYCLENEGATIVE
    ):
      self.data_handler.send(
          f'PACU 1,DULEV,C{channel},{mtype},{global_ref.mid} PCT'
      )
    else:
      val = self.data_handler.query(f'C{channel}:PAVA? {mtype}').split(',')[1]
      if val == 'UNDEF':
        val = math.nan
      else:
        val = float(val)
      return val
    val = self.data_handler.query('PAVA? CUST1').split(',')[1]
    if val == 'UNDEF':
      val = math.nan
    else:
      val = float(val)
    self.data_handler.send(f'PACU 1,{pacu[skip + 1:]}')
    return val

  def fetch_measure_number(self, measure_number):
    value = self.data_handler.query(
        f"vbs? 'return=app.measure.p{measure_number}.out.result.value'"
    )
    if value == 'No Data Available':
      value = math.nan
    return float(value)

  def fetch_waveform(self, channel):
    self.data_handler.send('COMM_ORDER HI')
    self.data_handler.send('COMM_FORMAT DEF9,WORD,BIN')
    temp = self.data_handler.query(f'C{channel}:INSPECT? WAVEDESC')

    temp_l = [item.split(':') for item in temp.split('\r\n')]
    mydict = {t[0].strip(): t[1].strip() for t in temp_l[1:-1]}

    points = int(mydict['PNTS_PER_SCREEN'])
    xincrement = float(mydict['HORIZ_INTERVAL'])
    xorigin = float(mydict['HORIZ_OFFSET'])
    yincrement = float(mydict['VERTICAL_GAIN'])
    yorigin = float(mydict['VERTICAL_OFFSET'])

    self.data_handler.send(f'C{channel}:WAVEFORM? DAT1')

    raw = self.data_handler.recv_raw()
    flag = raw.find(b'#')
    num = int(raw[flag + 1 : flag + 2])
    raw_data = raw[flag + 2 + num : flag + 2 + num + points * 2]

    yval_l = struct.unpack(f'>{points}h', raw_data)
    data = list(map(lambda x: (yincrement * x) - yorigin, yval_l))

    info_dict = {}
    info_dict['points_number'] = points
    # info_dict['point_size'] = int(info_list[0])
    # info_dict['trace_info'] = info_list[6]
    info_dict['x_increment'] = xincrement
    # info_dict['x_unit'] = info_list[10]
    info_dict['x_origin'] = xorigin
    info_dict['y_increment'] = yincrement
    # info_dict['y_unit'] = info_list[14]
    info_dict['y_origin'] = yorigin

    return info_dict, data

  def set_search_edges_on_off(self, enable: bool):
    self.data_handler.send(f"VBS 'app.WaveScan.Enable = {enable}'")
    if enable:
      # We set it to Absolute to conform to other scopes
      self.data_handler.send("VBS 'app.WaveScan.LevelType = Absolute'")
      # Turn off zoom that is auto enabled when WaveScan is on
      self.data_handler.send("VBS 'app.Zoom.ResetAll'")

  def set_search_edges(
      self,
      channel: int,
      edge: instrument.EdgeTriggerSlope,
      level: float,
  ):
    if edge == instrument.EdgeTriggerSlope.EITHER:
      slope = 'Both'
    self.data_handler.send("VBS 'app.WaveScan.Mode = Edge'")
    self.data_handler.send(f"VBS 'app.WaveScan.Source1 = C{channel}'")
    self.data_handler.send(f'VBS \'app.WaveScan.Slope = "{slope}"\'')
    self.data_handler.send(f"VBS 'app.WaveScan.AbsLevel = {level}'")

  def get_search_edges(
      self, start_index: int = 0, count: int = -1
  ) -> list[float]:
    # we dump the whole array since indexing directly into a non-existing
    # index will cause error on the scope, we will just handle it in here
    return_str = self.data_handler.query(
        "VBS? 'return=join("
        'app.WaveScan.MeasureProc.'
        'Outputs("Out").Result.'
        "ValueArray(-1,0,1),chr(44))'"
    )
    self.data_handler.send("VBS 'app.WaveScan.ScanDecode.View = false'")
    x_list = return_str.split(',')
    # check to make sure it is not just a list of 1 with an empty str due to
    # empty return from scope
    x_list = list(filter(None, x_list))
    if x_list:
      try:
        result = list(map(float, x_list))
        if count == -1:
          return_list = result[start_index:]
        else:
          return_list = result[start_index : start_index + count]
        return return_list
      except IndexError:
        pass
    else:
      return []  # pytype: disable=bad-return-type

  def load_settings_file(self, path):
    # TODO: b/333307803 - transfer setup file from pc to scope.
    self.data_handler.send(
        'VBS \' app.SaveRecall.Setup.PanelFilename = "set1.lss"\''
    )
    self.data_handler.send(
        'VBS \' app.SaveRecall.Setup.PanelDir = "D:\\Setups"\''
    )
    self.data_handler.send("VBS ' app.SaveRecall.Setup.DoRecallPanel'")
    self.wait_task()

  def save_settings_file(self, path):
    self.data_handler.send(
        'VBS \'app.SaveRecall.Setup.PanelFilename = "set1.lss"\''
    )
    self.data_handler.send(
        'VBS \'app.SaveRecall.Setup.PanelDir = "D:\\Setups"\''
    )
    self.data_handler.send("VBS 'app.SaveRecall.Setup.DoSavePanel'")
    self.wait_task()
    data = self.data_handler.query("TRFL? DISK,HDD,FILE,'D:\\Setups\\set1.lss'")
    with open(path, 'w') as f:
      f.write(data)

  def _get_screenshot(self, path):
    # WIP
    self.data_handler.send(
        'HARDCOPY_SETUP DEV,PNG,FORMAT,LANDSCAPE,BCKG,BLACK,DEST,'
        + f'FILE,,DIR,{path},AREA,FULLSCREEN,FILE,test'
    )
    self.data_handler.send('SCREEN_DUMP')

  def save_screenshot(self, path):
    self.data_handler.send(
        'HCSU DEV, PNG, FORMAT,PORTRAIT, BCKG, WHITE, DEST, REMOTE,'
        + ' PORT, NET, AREA,GRIDAREAONLY'
    )
    self.data_handler.send('SCDP')

    with open(path, 'wb+') as f:
      f.write(self.data_handler.recv_raw())

  def auto_set(self):
    self.data_handler.send("VBS 'app.AutoSetup 1'")

  def auto_scale(self, channel):
    pass

  def auto_trigger(self, channel, edge, mode, scale):
    pass

  def set_display_style(self, mode):
    pass

  def get_error_status(self):
    cmr = int(self.data_handler.query('CMR?'))
    exr = int(self.data_handler.query('EXR?'))
    ddr = int(self.data_handler.query('DDR?'))
    if cmr:
      raise AttributeError(f'Command Error: {cmr}')
    if exr:
      raise AttributeError(f'Execution Error: {exr}')
    if ddr:
      raise AttributeError(f'Device Dependent or Device Specific Error: {ddr}')
