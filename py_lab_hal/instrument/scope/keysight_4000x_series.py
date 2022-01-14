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

"""Child Scope Module of Keysight Infiniivision 4000-X."""

# pytype: disable=signature-mismatch

import dataclasses
import re
import time
import warnings

from py_lab_hal.cominterface import cominterface
from py_lab_hal.instrument import instrument
from py_lab_hal.instrument.scope import scope
from py_lab_hal.util import util


class MatchError(ValueError):
  pass


MEASUREMENT_TYPE = {
    instrument.MeasurementType.RISETIME: 'RISetime',
    instrument.MeasurementType.FALLTIME: 'FALLtime',
    instrument.MeasurementType.FREQUENCY: 'FREQuency',
    instrument.MeasurementType.PERIOD: 'PERiod',
    instrument.MeasurementType.AMPLITUDE: 'VAMPlitude',
    instrument.MeasurementType.RMS: 'VRMS',
    instrument.MeasurementType.MAX: 'VMAX',
    instrument.MeasurementType.MIN: 'VMIN',
    instrument.MeasurementType.HIGH: 'VTOP',
    instrument.MeasurementType.LOW: 'VBASe',
    instrument.MeasurementType.PEAKTOPEAK: 'VPP',
    instrument.MeasurementType.AVERAGE: 'VAVerage',
    instrument.MeasurementType.PULSEWIDTHPOSITIVE: 'PWIDth',
    instrument.MeasurementType.PULSEWIDTHNEGATIVE: 'NWIDth',
    instrument.MeasurementType.DUTYCYCLEPOSITIVE: 'DUTYcycle',
    instrument.MeasurementType.DUTYCYCLENEGATIVE: 'NDUTy',
    instrument.MeasurementType.OVERSHOOT: 'OVERshoot',
    instrument.MeasurementType.UNDERSHOOT: 'PREShoot',
    instrument.MeasurementType.AREA: 'AREA',
    instrument.MeasurementType.RISINGEDGECOUNT: 'PPULses',
    instrument.MeasurementType.FALLINGEDGECOUNT: 'NPULses',
}


CHANNEL_COUPLING = {
    instrument.ChannelCoupling.AC: 'AC',
    instrument.ChannelCoupling.DC: 'DC',
}

EDGE_TRIGGER_COUPLING = {
    instrument.EdgeTriggerCoupling.DC: 'DC',
    instrument.EdgeTriggerCoupling.DCREJECT: 'AC',
    instrument.EdgeTriggerCoupling.LFREJECT: 'LFReject',
}


EDGE_TRIGGER_SLOPE = {
    instrument.EdgeTriggerSlope.RISE: 'POSitive',
    instrument.EdgeTriggerSlope.FALL: 'NEGative',
    instrument.EdgeTriggerSlope.EITHER: 'EITHer',
}


EDGE_TRIGGER_MODE = {
    instrument.EdgeTriggerMode.AUTO: 'AUTO',
    instrument.EdgeTriggerMode.NORM: 'NORM',
}


PULSE_TRIGGER_MODE = {
    instrument.PulseTriggerMode.LESS: 'LESSthan',
    instrument.PulseTriggerMode.MORE: 'GREaterthan',
    instrument.PulseTriggerMode.WITHIN: 'RANGe',
}


PULSE_TRIGGER_SLOPE = {
    instrument.PulseTriggerSlope.NEG: 'NEGative',
    instrument.PulseTriggerSlope.POS: 'POSitive',
}


CURSOR_TYPE = {
    instrument.CursorType.OFF: 'OFF',
    instrument.CursorType.VER: 'VER',
    instrument.CursorType.HOR: 'HOR',
}


HORIZONTAL_TYPE = {
    instrument.HorizonType.SAMPLESIZE: 'SAMPLESIZE',
    instrument.HorizonType.SAMPLERATE: 'SAMPLERATE',
}


REFERENCE_TYPE = {
    instrument.ReferenceType.PER: 'PERC',
    instrument.ReferenceType.ABS: 'ABS',
}


REFERENCE_SCOPE = {
    instrument.ReferenceScope.GLOBAL: 'GLOBAL',
    instrument.ReferenceScope.LOCAL: 'LOCAL',
}


DELTA_SLOPE = {
    instrument.DeltSlope.RISE: 'RISing',
    instrument.DeltSlope.FALL: 'FALLing',
}

ADDITIONAL_MEASUREMENT_CMD = {
    instrument.MeasurementType.RMS: 'DISPlay, DC, ',
    instrument.MeasurementType.AVERAGE: 'DISPlay,',
    instrument.MeasurementType.AREA: 'DISPlay, ',
}


# TODO: b/332626315 - Inspect if we need to add get from dict calls.
class Keysight4000xSeries(scope.Scope):
  """Child Scope Class of model."""

  def __init__(
      self,
      com: cominterface.ComInterfaceClass,
      inst_config: instrument.InstrumentConfig,
  ) -> None:
    super().__init__(com, inst_config)
    scope_name = self.idn.split(',')[1]
    # scope name convention is type model space numberLetter: DSO-X 1234A
    # Last number before the letter indicates number of channels in the scope
    match = re.search(r'[0-9](?=[A-Z])', scope_name)
    if not match:
      raise MatchError(
          '# of Channels cannot be found, please check your model!'
      )
    self.num_ch = match.group(0)

  ############################
  # 4000X Series
  ############################
  def set_channel_position(self, channel, position):
    # """Keysight 4000X-Series:
    #
    # sets the value that is represented at center screen for the selected
    # channel.
    # this function the same as "set_channel_offset"
    # """
    self.data_handler.send(f':CHANnel{channel}:OFFSet {-1 * position}')

  def set_channel_attenuation(self, channel, attenuation_factor):
    # """Keysight 4000X-Series:
    #
    # attenuation_factor: 0.001 to 10000, The probe attenuation factor may
    # be from 0.001 to 10000.
    # """
    self.data_handler.send(f':CHANnel{channel}:PROBe {attenuation_factor}')

  def set_channel_coupling(self, channel, mode, impedance):
    # """Keysight 4000X-Series:
    #
    # mode: AC | DC, The coupling for each analog channel can be set to
    # AC or DC.
    # impedance: ONEMeg | FIFTy, The legal values for this command are
    # ONEMeg(1 MΩ) and FIFTy (50Ω).
    # """
    # TODO: b/332626709 - add error for setting to unsupported coupling mode.
    self.data_handler.send(
        f':CHANnel{channel}:COUPling'
        f' {util.get_from_dict(CHANNEL_COUPLING, mode)}'
    )
    if impedance == 50:
      self.data_handler.send(f':CHANnel{channel}:IMPedance FIFTy')
    elif impedance == 1e6:
      self.data_handler.send(f':CHANnel{channel}:IMPedance ONEMeg')

  def set_channel_offset(self, channel, voffset):
    # """Keysight 4000X-Series:
    #
    # sets the value that is represented at center screen for the selected
    # channel.
    # this function the same as "set_channel_position"
    # """
    self.data_handler.send(f':CHANnel{channel}:OFFSet {-1 * voffset}')

  def set_channel_division(self, channel, vdiv):
    # """Keysight 4000X-Series:
    #
    # sets the vertical scale, or units per division, ofthe selected
    # channel.
    # """
    self.data_handler.send(f':CHANnel{channel}:SCALe {vdiv}')

  def set_channel_on_off(self, channel, enable):
    # """Keysight 4000X-Series:
    #
    # turns the display of the specified channel on or off.
    # """
    self.data_handler.send(f':CHANnel{channel}:DISPlay {int(enable)}')

  def set_channel_bandwidth(self, channel, value, enable):
    """set the bandwidth limit.

    Choose whether or not to enable BW Limit for the selected channel and if
    enabled, the bandwidth limit to set by value.

    Args:
        channel (int): The number of the channel
        value (float): THIS HAS NO EFFECT ON the 4000X Series!
        enable (bool): Enable or not to set the bandwidth limit

    Keysight 4000X-Series: controls an internal low-pass filter.
    if enable=True, turn on the filter, the bandwidth of the specified channel
    is limited to approximately 25 MHz.
    """

    if enable:
      self.data_handler.send(f':CHANnel{channel}:BWLimit ON')
    else:
      self.data_handler.send(f':CHANnel{channel}:BWLimit OFF')

  def set_channel_labels(self, channel, value):
    # """Keysight 4000X-Series:
    #
    # turn on the channel and sets the analog channel label to the string
    # that follows.
    # """
    self.data_handler.send(':DISPlay:LABel ON')
    self.data_handler.send(f":CHANnel{channel}:LABel '{value}'")

  def set_channel_labels_position(self, channel, x, y):
    """Sets the channel label position based on values given in x and y.

    Args:
        channel (int): The number of the channel
        x (float): X position
        y (float): Y position

    Keysight 4000X-Series:

    ***Keysight 4000X-Series does not support this function.
    Calling this function will raise an error***
    """
    raise ValueError('Keysight 4000X-Series does not support this function.')

  def get_channel_labels(self, channel):
    # """Keysight 4000X-Series:
    #
    # query returns the label associated with a particular analog channel.
    # """
    readstr = []

    self.data_handler.send(f':CHANnel{channel}:LABel?')
    readstr.append(self.data_handler.recv().strip('"'))

    return readstr

  def set_vert_range(
      self,
      channel,
      channel_enable,
      vertical_range,
      vertical_offset,
      probe_attenuation,
      vertical_coupling,
  ):
    # """Keysight 4000X-Series:
    #
    # attenuation_factor: 0.001 to 10000, The probe attenuation factor may
    # be from 0.001 to 10000.
    # vertical_coupling: AC | DC, The coupling for each analog channel can
    # be set to AC or DC.
    # """
    # TODO: b/332626709 - add error for setting to unsupported coupling mode.

    self.data_handler.send(f':CHANnel{channel}:DISPlay {int(channel_enable)}')
    self.data_handler.send(f':CHANnel{channel}:RANGe {vertical_range}')
    self.data_handler.send(f':CHANnel{channel}:OFFSet {-1 * vertical_offset}')
    self.data_handler.send(f':CHANnel{channel}:PROBe {probe_attenuation}')
    self.data_handler.send(
        f':CHANnel{channel}:COUPling'
        f' {util.get_from_dict(CHANNEL_COUPLING, vertical_coupling)}'
    )

  def config_edge_trigger(self, channel, level, edge, mode):
    # """Keysight 4000X-Series:
    #
    # edge: NEGative | POSitive | EITHer | ALTernate, specifies the slope
    # of the edge for the trigger.
    # mode: AC | DC, The coupling for each analog channel can be set to AC
    # or DC.
    # """
    # TODO: b/332626709 - add error for setting to unsupported coupling mode.
    self.data_handler.send(':TRIGger:MODE EDGE')
    self.data_handler.send(f':TRIGger:EDGE:SOURce CHANnel{channel}')
    self.data_handler.send(
        ':TRIGger:EDGE:COUPling'
        f' {util.get_from_dict(EDGE_TRIGGER_COUPLING, mode)}'
    )
    self.data_handler.send(f':TRIGger:EDGE:LEVel {level}')
    self.data_handler.send(
        f':TRIGger:EDGE:SLOPE {util.get_from_dict(EDGE_TRIGGER_SLOPE, edge)}'
    )

  def set_aux_trigger(self, enable):
    # """Keysight 4000X-Series:
    #
    # enable=True: triggers on the rear panel EXT TRIG IN signal.
    # """
    if enable:
      self.data_handler.send(':TRIGger:EDGE:SOURce EXTernal')

  def config_continuous_acquisition(self, en_cont_acq, en_auto_trig):
    # """Keysight 4000X-Series:
    #
    # selects the trigger sweep mode
    #     sweep mode: AUTO | NORMal
    # """
    if en_cont_acq and en_auto_trig:
      self.data_handler.send(':TRIGger:SWEep AUTO')
      self.data_handler.send(':RUN')
    elif en_cont_acq and not en_auto_trig:
      self.data_handler.send(':TRIGger:SWEep TRIGgered')
    elif not en_cont_acq and not en_auto_trig:
      self.data_handler.send(':TRIGger:SWEep TRIGgered')
      self.data_handler.send(':SINGle')

  def config_rolling_mode(self, enable):
    # """Keysight 4000X-Series:
    #
    # sets the current time base: MAIN | WINDow | XY | ROLL
    # enable=True: rolling mode
    # enable=False: normal time base mode(default)
    # """
    if enable:
      self.data_handler.send(':TIMebase:MODE ROLL')
    else:
      self.data_handler.send(':TIMebase:MODE MAIN')

  def config_pulse_width_trigger(
      self, channel, mode, slope, level, low_limit, hi_limit
  ):
    # """Keysight 4000X-Series:
    #
    # mode: does not support "OUT (Out of Range)"
    # slope: POSitive | NEGative
    # if mode="WITHIN(In Range)":
    #     low_limit: 15 ns - 10 seconds
    #     hi_limit: 10 ns - 9.99 seconds
    # """
    trigger_par_dict = {
        'LESS': f'{hi_limit}',
        'MORE': f'{low_limit}',
        'WITHIN': f'{low_limit},{hi_limit}',
        'OUT': None,  # Not supported
    }

    trigger = util.get_from_dict(PULSE_TRIGGER_MODE, mode)
    trigger_par = util.get_from_dict(trigger_par_dict, mode)
    if not trigger:
      raise ValueError('Keysight 4000X-Series does not support this function.')

    trigger_slope = util.get_from_dict(PULSE_TRIGGER_SLOPE, slope)
    self.data_handler.send(':TRIGger:MODE GLITch')
    self.data_handler.send(f':TRIGger:GLITch:SOURce CHANnel{channel}')
    self.data_handler.send(f':TRIGger:GLITch:QUALifier {trigger}')
    self.data_handler.send(f':TRIGger:GLITch:{trigger} {trigger_par}')
    self.data_handler.send(f':TRIGger:GLITch:POLarity {trigger_slope}')
    self.data_handler.send(f':TRIGger:GLITch:LEVel {level}')

  def config_timeout_trigger(self, channel, polarity, level, timeout):
    """Sets a timeout (dropout) trigger for the selected channel.

    Sets up a timeout trigger to wait for all defined conditions to be met to
    start acquisition(s).

    Args:
      channel (int): The channel source for the trigger
      polarity (str): Wait for timeout to Stay High, Stay Low, or either
      level (float): The level threshold to trigger
      timeout (float): Timeout time in seconds

    ***Keysight 4000X-Series does not support timeout/dropout triggering and
      will
    raise an error when called.***
    """
    raise ValueError('Keysight 4000X-Series does not support this function.')

  def set_horiz_division(self, hor_div, delay, sample_value, sample_type):
    # """Keysight 4000X-Series:
    #
    # sample_value: AUTO | <sample_rate>, sets the desired acquisition
    # sample rate:
    # sample_type: RTIMe | ETIMe | SEGMented, sets the acquisition mode of
    # the oscilloscope.
    #     RTIMe: In Real Time Normal mode
    #     ETIMe: sets the oscilloscope in equivalent time mode.
    #     SEGMented: sets the oscilloscope in segmented memory mode.
    # """
    self.data_handler.send(':ACQuire:SRATe AUTO')
    self.data_handler.send(':ACQuire:POINts AUTO')
    # Keysight doesn't auto balance between rate or points, so we need to do it
    # Keep scale fixed priority
    # Equation is 10div x time/div x pts/time = pts
    # This only holds for single acq, but for continuous, it halves the memsize
    self.data_handler.send(f':TIMebase:SCALe {hor_div}')
    self.data_handler.send(f':TIMebase:POSition {delay}')
    if sample_type == instrument.HorizonType.SAMPLESIZE:
      srate = sample_value / (10 * hor_div)
      self.data_handler.send(f':ACQuire:SRATe {srate}')
      self.data_handler.send(f':ACQuire:POINts {sample_value}')
    elif sample_type == instrument.HorizonType.SAMPLERATE:
      self.data_handler.send(f':ACQuire:SRATe {sample_value}')
      samples = sample_value * (10 * hor_div)
      self.data_handler.send(f':ACQuire:POINts {samples}')

  def set_horiz_offset(self, hor_offset):
    # """Keysight 4000X-Series:
    #
    # sets the time interval between the trigger event and the display
    # reference point on the screen.
    # """
    self.data_handler.send(f':TIMebase:position {-hor_offset}')

  def _set_meas_reference(self, low, mid, high, r_type, meas):
    chan = self.measurement_item[meas].meas_args['channel']
    self.data_handler.send(
        f':MEASure:DEFine THResholds,{r_type},{high},{mid},{low},CHANnel{chan}'
    )

  def set_measurement_reference(
      self, low, mid, high, mid2, reference_type, reference_scope, meas_number
  ):
    """Configures the reference levels.

    Used for certain timing calculations such as rise time, width, etc.
    Set reference levels in percentage or absolute value
    mid2 reference is reserved for delta measurement against another waveform

    References can be configured as a local (per measurement)
    or global (all measurements) setting.

    The default settings are 10-50-90 percent low, mid, high respectively
    with mid2 = 50 percent with a global scope. By default, all measurements
    are set to global.

    Set scope to global and meas_number to none to set global reference w/o
    toggle measurement scope.

    ***For the Keysight scopes, they do not support setting reference by
    measurement number, but instead by source. The current workaround will check
    what source the measurement is from and set the refs. If multiple meas using
    the same source have different refs, then the last reference programmed
    will take precedence. The dev team will take into consideration other
    workarounds or open up a new option to enable source or measurement based
    referenc assignments***

    Args:
        low (float): Low reference level
        mid (float): Mid reference level
        high (float): High reference level
        mid2 (float): Mid2 reference level
        reference_type (str): Set reference level as percentage or absolute
          value
        reference_scope (str): Set reference scope as local or global
        meas_number (int | None): Measurement number to apply the reference if
          in local. This can also toggle local or global for measurement if
          supplied.
    """
    # Check to see if this is a global or local scope
    # If global we want to target all existing measurements that scoped globally
    r_type = util.get_from_dict(REFERENCE_TYPE, reference_type)
    if reference_scope == instrument.ReferenceScope.GLOBAL:
      for meas, meas_item in self.measurement_item.items():
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
          self._set_meas_reference(low, mid, high, r_type, meas)

    # If Local scope, we only target the specific measurement number
    elif (
        reference_scope == instrument.ReferenceScope.LOCAL
        and meas_number in self.measurement_item
    ):
      if self.measurement_item[meas_number].displayed:
        self._set_meas_reference(low, mid, high, r_type, meas_number)

    if reference_scope == instrument.ReferenceScope.GLOBAL:
      meas = 'global'
    else:
      meas = meas_number
    ref = self.ReferenceLevels(
        low, mid, high, mid2, reference_type, reference_scope, meas_number
    )
    self.measurement_ref[f'{meas}_ref'] = ref

  def set_measurement_on_off(self, meas_number, enable):
    """Enabled or disable the selected measurement number for on screen display.

    Args:
        meas_number (int): measurement number
        enable (bool): enable or disable the Channel

    Keysight 4000X-Series:

    ***Keysight 4000X-Series does not support this function.***
    """
    warnings.warn(
        'Keysight 4000X-Series does not allow turn on/off measurement displays.'
    )

  def set_measurement_statistics(self, enable):
    # """Keysight 4000X-Series:
    #
    # determines the type of information
    # """
    if enable:
      self.data_handler.send(':MEASure:STATistics ON')
      self.data_handler.send(':MEASure:STATistics:DISPlay ON')
    else:
      self.data_handler.send(':MEASure:STATistics CURR')
      self.data_handler.send(':MEASure:STATistics:DISPlay OFF')

  def set_measurement(self, channel, meas_number, measurement_type):
    # """Keysight 4000X-Series:
    #
    # refers to the dict "MEASUREMENT_TYPE"
    # """
    self.measurement_item[meas_number] = self.MeasurementConfig(
        meas_type='set_measurement',
        meas_args={
            'channel': channel,
            'meas_number': meas_number,
            'measurement_type': measurement_type,
        },
        displayed=True,
    )

    mea_type = util.get_from_dict(MEASUREMENT_TYPE, measurement_type)
    if measurement_type in ADDITIONAL_MEASUREMENT_CMD:
      self.data_handler.send(
          f':MEASure:{mea_type} '
          f'{util.get_from_dict(ADDITIONAL_MEASUREMENT_CMD, measurement_type)}CHANnel{channel}'
      )
    else:
      self.data_handler.send(f':MEASure:{mea_type} CHANnel{channel}')

    self.data_handler.query('*OPC?')
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
    # """Keysight 4000X-Series:
    #
    # places the instrument in the continuous measurement mode and starts
    # a delay measurement.
    #     delay = t(<edge_spec_2>) - t(<edge_spec_1>)
    # start_edge: RISing | FALLing
    # end_edge: RISing | FALLing
    # """

    # Check if there is an existing reference and apply it
    # If new measurement, apply global
    ref = self.measurement_ref.get(f'{meas_number}_ref')
    startedge = util.get_from_dict(DELTA_SLOPE, start_edge)
    endedge = util.get_from_dict(DELTA_SLOPE, end_edge)
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
    if ch_ref is None:
      raise RuntimeError('Can not find the channel ref')
    # query current channel setting and preserve it
    # here we make a big assumption that the settings are the same reference
    # type, usually don't change
    # query return is in the format of THR,<TYPE>,<HIGH>,<MID>,<LOW>
    ch1_ref = self.data_handler.query(
        f':MEASure:DEFine? THResholds,CHANnel{channel1}'
    ).split(',')
    ch1_ref = ch1_ref[1:]
    ch2_ref = self.data_handler.query(
        f':MEASure:DEFine? THResholds,CHANnel{channel2}'
    ).split(',')
    ch2_ref = ch2_ref[1:]

    self.data_handler.send(
        f':MEASure:DEFine THResholds {ch1_ref[0]},'
        f'{ch1_ref[1]},{ch_ref.mid},{ch1_ref[3]},CHANnel{channel1}'
    )
    self.data_handler.send(
        f':MEASure:DEFine THResholds {ch2_ref[0]},'
        f'{ch2_ref[0]},{ch_ref.mid2},{ch2_ref[3]},CHANnel{channel2}'
    )

    self.data_handler.send(
        f':MEASure:DELay:DEFine {startedge}, 0, MIDDle, {endedge}, 0, MIDDle'
    )
    self.data_handler.send(f':MEASure:DELay AUTO,CHAN{channel1},CHAN{channel2}')

  def set_cursor(self, channel, cursor_type, cur1_pos, cur2_pos):
    # """Keysight 4000X-Series:
    #
    # if cursor_type=OFF: removes the cursor information from the display.
    # if cursor_type=HOR: enables manual placement of the X cursors.
    # if cursor_type=VER: enables manual placement of the Y cursors.
    # *if cursor_type=WAVeform: the Y1 cursor tracks the voltage value at
    # the X1 cursor of the waveform specified by the X1Y1source,and
    # the Y2 cursor does the same for the X2 cursor and its X2Y2source.
    # """
    if cursor_type == instrument.CursorType.OFF:
      self.data_handler.send(':MARKer:MODE OFF')
    else:
      self.data_handler.send(':MARKer:MODE MANual')
      self.data_handler.send(f':MARKer:X1Y1source CHANnel{channel}')
      self.data_handler.send(f':MARKer:X2Y2source CHANnel{channel}')

      if cursor_type == instrument.CursorType.HOR:
        self.data_handler.send(f':MARKer:X1Position {cur1_pos}')
        self.data_handler.send(f':MARKer:X2Position {cur2_pos}')
      else:
        self.data_handler.send(f':MARKer:Y1Position {cur1_pos}')
        self.data_handler.send(f':MARKer:Y2Position {cur2_pos}')
    # elif self.CURSOR_TYPE[cursor_type] == "WAVeform":
    #     self.data_handler.send(':MARKer:MODE WAVeform')

  def set_infinite_persistence(self, enable):
    # """Keysight 4000X-Series:
    #
    # specifies the persistence setting
    # If enable=True, indicates infinite persistence.
    # If enable=False, indicates zero persistence(default)
    # """
    if enable:
      self.data_handler.send(':DISPlay:PERSistence INFinite')
    else:
      self.data_handler.send(':DISPlay:PERSistence MIN')

  def clear_persistence(self):
    self.data_handler.send(':CDISplay')

  def wait_acquisition_complete(self, timeout):
    # this wait task essentially acts as a delay
    self.wait_task(timeout)
    rnum = 0
    t0 = time.time()
    while time.time() - t0 < timeout:
      time.sleep(1)
      self.data_handler.send(':OPERegister:CONDition?')
      rnum = int(self.data_handler.recv())
      # mask and only look at bit 4 for run bit
      rnum = rnum & 0x8
      if rnum == 0:
        # this wait task essentially acts as a delay
        self.wait_task(timeout)
        break
    else:
      raise RuntimeError('Timeout')

  def get_acquisition(self):
    self.data_handler.send(':RSTate?')
    return self.data_handler.recv()

  def arm_single_trig(self):
    self.data_handler.send(':TRIGger:SWEep TRIGgered')
    self.stop_acquisition()
    self.wait_task(5)
    self.clear()
    self.data_handler.send(':SINGle')

  def stop_acquisition(self):
    self.data_handler.send(':STOP')

  def start_acquisition(self):
    self.data_handler.send(':RUN')

  def reset_measurement_statistics(self):
    self.data_handler.send(':MEASure:STATistics:RESet')

  def get_measurement_statistics(self, meas_number):
    self.data_handler.send(':MEASure:STATistics?')
    rstr_statistics = self.data_handler.recv()

    self.data_handler.send(':MEASure:STATistics ON')
    self.data_handler.send(
        ':MEASure:RESults?'
    )  # Current | Min | Max | Mean | Std Dev | Count
    rstring = self.data_handler.recv()
    rstring = rstring.split(',')
    meas_idx = meas_number - 1
    if rstr_statistics == 'ON':
      # per format from other scope, output dict s/b:
      # 'current_value', 'count', 'max', 'min', 'mean', 'std_dev'
      # name, data
      # Current | Min | Max | Mean | Std Dev | Count
      rstr_curr = [rstring[i + 1 : i + 7] for i in range(0, len(rstring), 7)]
      rdict = {
          'current_value': rstr_curr[meas_idx][0],
          'count': rstr_curr[meas_idx][5],
          'max': rstr_curr[meas_idx][2],
          'mean': rstr_curr[meas_idx][3],
          'min': rstr_curr[meas_idx][1],
          'std_dev': rstr_curr[meas_idx][4],
      }
    else:
      # name, data
      rstr_curr = [rstring[i + 1] for i in range(0, len(rstring), 7)]
      # single data
      rdict = {'current_value': rstr_curr[meas_idx][0]}
      #
      self.data_handler.send(':MEASure:STATistics CURR')

    return rdict

  def wait_task(self, timeout=30):
    self.clear()
    t0 = time.time()
    while time.time() - t0 < timeout:
      time.sleep(1)
      # self.data_handler.send(":PDER?")
      self.data_handler.send('*OPC')
      opc = self.event_status_register(
          instrument.StandardEventStatusRegisterMask.OPC
      )
      if opc:
        break
    else:
      raise ValueError(f'Timeout({timeout}) - wait_task')

  def wait_trigger_ready(self, timeout):
    # """Keysight 4000X-Series:
    #
    # Checking for Armed Status
    # After the Arm Event Register is read, the register is cleared.
    # The returned value 1 indicates a trigger armed event has occurred
    # and 0 indicates a trigger armed has not occurred.
    # Once the AER bit is set, it is cleared only by doing :AER?
    # or by sending a *CLS command.
    # """
    rnum = 0
    t0 = time.time()
    while time.time() * 1000 - t0 * 1000 < timeout:
      time.sleep(0.1)
      self.data_handler.send(':AER?')
      rnum = int(self.data_handler.recv())
      if rnum == 1:
        break
    else:
      raise ValueError(f'Timeout({timeout}) - wait_trigger_ready')

  def force_trigger(self):
    self.data_handler.send(':TRIGger:FORCe')

  def fetch_delta_measurement(
      self, channel1, channel2, start_edge, end_edge, mid, mid2
  ):
    # """Keysight 4000X-Series:
    #
    # start_edge: RISing | FALLing
    # end_edge: RISing | FALLing
    # """

    # query current channel setting and preserve it
    # here we make a big assumption that the settings are the same reference
    # type, usually don't change
    # query return is in the format of THR,<TYPE>,<HIGH>,<MID>,<LOW>
    ch1_ref = self.data_handler.query(
        f':MEASure:DEFine? THResholds,CHANnel{channel1}'
    ).split(',')
    ch1_ref = ch1_ref[1:]
    ch2_ref = self.data_handler.query(
        f':MEASure:DEFine? THResholds,CHANnel{channel2}'
    ).split(',')
    ch2_ref = ch2_ref[1:]

    # reference
    self.data_handler.send(
        f':MEASure:DEFine THResholds, PERC,90,{mid},10,CHANnel{channel1}'
    )
    self.data_handler.send(
        f':MEASure:DEFine THResholds, PERC,90,{mid2},10,CHANnel{channel2}'
    )
    startedge = util.get_from_dict(DELTA_SLOPE, start_edge)
    endedge = util.get_from_dict(DELTA_SLOPE, end_edge)
    # DELTatime measurement
    self.data_handler.send(
        f':MEASure:DELay:DEFine {startedge},0,MIDDle,{endedge},0,MIDDle'
    )
    self.data_handler.send(
        f':MEASure:DELay? AUTO,CHAN{channel1},CHAN{channel2}'
    )
    #
    # read
    rstring = self.data_handler.recv()
    _ = self.data_handler.query('*OPC?')

    # set the references back to their original settings
    self.data_handler.send(
        ':MEASure:DEFine THResholds, '
        f'{ch1_ref[0]},{ch1_ref[1]},{ch1_ref[2]},{ch1_ref[3]},CHANnel{channel1}'
    )
    self.data_handler.send(
        ':MEASure:DEFine THResholds, '
        f'{ch2_ref[0]},{ch2_ref[1]},{ch2_ref[2]},{ch2_ref[3]},CHANnel{channel2}'
    )

    return rstring

  def fetch_measurement(self, channel, measurement_type):
    mea_type = util.get_from_dict(MEASUREMENT_TYPE, measurement_type)
    if measurement_type in ADDITIONAL_MEASUREMENT_CMD:
      additional_cmd = util.get_from_dict(
          ADDITIONAL_MEASUREMENT_CMD, measurement_type
      )
      self.data_handler.send(
          f':MEASure:{mea_type}? {additional_cmd}CHANnel{channel}'
      )
    else:
      self.data_handler.send(f':MEASure:{mea_type}? CHANnel{channel}')

    result = self.data_handler.recv()
    self.data_handler.query('*OPC?')

    return result

  def fetch_measure_number(self, measure_number):
    self.data_handler.send(':MEASure:RESults?')
    rstring = self.data_handler.recv()
    rstring = rstring.split(',')
    rstr_name = [rstring[i] for i in range(0, len(rstring), 7)]
    # Current | Min | Max | Mean | Std Dev | Count
    rstr_curr = [rstring[i + 1 : i + 7] for i in range(0, len(rstring), 7)]
    if measure_number > len(rstr_name) or measure_number <= 0:
      rstring = 'na'
    else:
      rstring = rstr_curr[measure_number - 1][0]
    return rstring

  def fetch_waveform(self, channel):
    self.data_handler.send(':WAVeform:SOURce CHANnel{channel}')
    self.data_handler.send(':WAVeform:FORMat BYTE')
    # Get numeric values for later calculations.
    points = int(self.data_handler.query('WAVeform:POINts?'))
    x_increment = float(self.data_handler.query(':WAVeform:XINCrement?'))
    x_origin = float(self.data_handler.query(':WAVeform:XORigin?'))
    y_increment = float(self.data_handler.query(':WAVeform:YINCrement?'))
    y_origin = float(self.data_handler.query(':WAVeform:YORigin?'))
    # y_reference = float(self.data_handler.query(':WAVeform:YREFerence?'))
    # Get the waveform data.
    s_data = self.data_handler.query_raw(b':WAVeform:DATA?')
    # value = sData
    # dtime = []
    # dvol = []
    # keep for future reference
    # for i in range(0, len(value) - 1):
    #   dtime.append(x_origin + (i * x_increment))
    #   dvol.append((float(value[i] - y_reference) * y_increment) + y_origin)
    # return dtime, dvol
    info_dict = {}
    info_dict['points_number'] = points
    # in byte date, onlye 1 byte per point is transferred
    info_dict['point_size'] = 1
    info_dict['x_increment'] = x_increment
    info_dict['x_origin'] = x_origin
    info_dict['y_increment'] = y_increment
    info_dict['y_origin'] = y_origin
    return info_dict, s_data

  def set_search_edges_on_off(self, enable):
    self.data_handler.send(f':SEARch:STATe {int(enable)}')
    if enable:
      self.data_handler.send(':SEARch:MODE EDGE')

  def set_search_edges(self, channel, edge, level):
    # """Keysight 4000X-Series:
    #
    # edge: NEGative | POSitive | EITHer
    # """
    self.data_handler.send(f':SEARch:EDGE:SOURce CHANnel{channel}')
    self.data_handler.send(
        f':SEARch:EDGE:SLOPe {util.get_from_dict(EDGE_TRIGGER_SLOPE, edge)}'
    )  # NEGative | POSitive | EITHer
    self.data_handler.send(f':TRIGger:EDGE:LEVel {level}')

  def get_search_edges(self, start_index=0, count=-1):
    # query the current position to restore later
    position = self.data_handler.query(':TIMebase:POSition?')
    dcount = int(self.data_handler.query(':SEARch:COUNt?'))
    rstring = []
    for i in range(1, dcount + 1):
      self.data_handler.send(':SEARch:EVENt ' + str(i))
      rstring.append(float(self.data_handler.query(':TIMebase:POSition?')))
    # restore the starting position
    self.data_handler.send(f':TIMebase:POSition {position}')
    result = []
    if count == -1:
      result = rstring
    elif start_index <= dcount and start_index + count - 1 <= dcount:
      for i in range(start_index - 1, start_index - 1 + count):
        result.append(float(rstring[i]))

    return result

  def load_settings_file(self, path):
    with open(path, 'rb') as f:
      setup_bytes = f.read()  # setup.set
    self.data_handler.send_raw(b':SYSTem:SETup ' + setup_bytes)
    self.wait_task()

  def save_settings_file(self, path: str):
    setup_bytes = self.data_handler.query_raw(b'*LRN?')
    with open(path, 'wb') as f:  # setup.set
      f.write(setup_bytes)

  def _get_screenshot(self, path):
    # """Keysight 4000X-Series:
    #
    # save an image file to a connected USB storage device
    # path: file name
    # """
    self.data_handler.send(':SAVE:IMAGe:FORMat PNG')
    # self.data_handler.send(':SAVE:IMAGe:STARt "\\usb\\' + path + '"')
    self.data_handler.send(f':SAVE:IMAGe:STARt {path}')

  def save_screenshot(self, path):
    self.data_handler.send(':HARDcopy:INKSaver OFF')
    self.data_handler.send(':DISPlay:DATA? PNG')
    # read the first 2 characters which is the number of digits for data size
    _, read_size = self.data_handler.recv(size=2)
    data_size = self.data_handler.recv(size=int(read_size))
    img = self.data_handler.recv_raw(size=int(data_size))

    f = open(path, 'wb')  # *.png
    f.write(bytearray(img))
    f.close()
    print('Screen image written to' + path)

  def auto_set(self):
    self.data_handler.send(':AUToscale')

  def set_display_style(self, mode):
    # """Keysight 4000X-Series:
    #
    # Keysight 4000X-Series does not support this functio.
    # Raise error
    # """
    raise ValueError('Keysight 4000X-Series does not support this function.')

  def get_error_status(self):
    # """Keysight 4000X-Series:
    #
    # query outputs the next error number and text from the errorqueue.
    # """
    errstr = self.data_handler.query(':SYSTem:ERRor?')

    return errstr

  def set_measurement_reference_ch(
      self, channel, low, mid, high, reference_type
  ):
    # """Keysight 4000X-Series:
    #
    # sets up the definition for measurements by specifying the
    # threshold(reference) values.
    # Changing these values(reference) may affect the results of other
    # measure commands.
    # """
    ref_type = util.get_from_dict(REFERENCE_TYPE, reference_type)
    self.data_handler.send(
        ':MEASure:DEFine THResholds, '
        f'{ref_type},{high},{mid},{low},CHANnel{channel}'
    )
