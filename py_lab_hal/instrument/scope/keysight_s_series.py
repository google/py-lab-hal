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

"""Child Scope Class of model."""

# pytype: disable=signature-mismatch

import collections
import dataclasses
import re
import struct
import time
import warnings
from py_lab_hal.cominterface import cominterface
from py_lab_hal.instrument import instrument
from py_lab_hal.instrument.scope import scope
from py_lab_hal.util import util


# Support Notes from manual:
# This book is your guide to programming Infiniium oscilloscopes that have the
# 5.00 or greater, next-generation user interface software.
# Supported models include:
# • 9000 Series and 9000H Series oscilloscopes.
# • S-Series oscilloscopes.
# • 90000A Series oscilloscopes.
# • 90000 X-Series oscilloscopes.
# • V-Series oscilloscopes.
# • 90000 Q-Series oscilloscopes.
# • Z-Series oscilloscopes.

_KEYSIGHT_MODEL_REGEX = re.compile(r'([M|D]S[O|A][Z|V|X]*)[0-9]+(?=[A-Z])')


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
    instrument.MeasurementType.DUTYCYCLENEGATIVE: 'DUTYcycle',
    instrument.MeasurementType.OVERSHOOT: 'OVERshoot',
    instrument.MeasurementType.UNDERSHOOT: 'UNDershoot',
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
    instrument.PulseTriggerMode.LESS: 'LESS',
    instrument.PulseTriggerMode.MORE: 'MORE',
    instrument.PulseTriggerMode.WITHIN: 'WITHIN',
}

PULSE_TRIGGER_SLOPE = {
    instrument.PulseTriggerSlope.NEG: 'NEGative',
    instrument.PulseTriggerSlope.POS: 'POSitive',
}

CURSOR_TYPE = {
    instrument.CursorType.OFF: 'OFF',
    instrument.CursorType.VER: 'VER',
    instrument.CursorType.HOR: 'XONLy',
}


HORIZONTAL_TYPE = {
    instrument.HorizonType.SAMPLESIZE: 'SAMPLESIZE',
    instrument.HorizonType.SAMPLERATE: 'SAMPLERATE',
}


REFERENCE_TYPE = {
    instrument.ReferenceType.PER: 'PERC',
    instrument.ReferenceType.ABS: 'ABS',
}

rs_enum = instrument.ReferenceScope
REFERENCE_SCOPE = {
    instrument.ReferenceScope.GLOBAL: 'GLOBAL',
    instrument.ReferenceScope.LOCAL: 'LOCAL',
}


TIMEOUT_TRIG_POLARITY = {
    instrument.TimeoutTrigPolarity.STAYHIGH: 'HIGH',
    instrument.TimeoutTrigPolarity.STAYLOW: 'LOW',
    instrument.TimeoutTrigPolarity.EITHER: 'UNCHanged',
}


DELTA_SLOPE = {
    instrument.DeltSlope.RISE: 'RISing',
    instrument.DeltSlope.FALL: 'FALLing',
    instrument.DeltSlope.EITHER: 'EITHer',
}

ADDITIONAL_MEASUREMENT_CMD_PRE = {
    instrument.MeasurementType.RMS: 'DISPlay, DC, ',
    instrument.MeasurementType.AVERAGE: 'DISPlay,',
    instrument.MeasurementType.AREA: 'DISPlay, ',
}
ADDITIONAL_MEASUREMENT_CMD_POST = {
    instrument.MeasurementType.RMS: 'VOLT',
    instrument.MeasurementType.DUTYCYCLEPOSITIVE: 'RISing',
    instrument.MeasurementType.DUTYCYCLENEGATIVE: 'FALLing',
}


class MatchError(ValueError):
  pass


class KeysightSSeries(scope.Scope):
  """Child Scope Class of model."""

  PERC_10_90 = 'T1090'
  PERC_20_80 = 'T2080'

  def __init__(
      self,
      com: cominterface.ComInterfaceClass,
      inst_config: instrument.InstrumentConfig,
  ) -> None:
    super().__init__(com, inst_config)
    self.model_type_90k = False
    self.scope_name = self.idn.split(',')[1]
    # scope name convention is type model space numberLetter: DSO-X 1234A
    # 90000A Series, 90000 X-Series, V-Series, 90000 Q-Series, and Z-Series
    match = _KEYSIGHT_MODEL_REGEX.search(self.scope_name)
    global EDGE_TRIGGER_COUPLING
    global CHANNEL_COUPLING
    if match:
      # redefine some dicts:
      self.model_type_90k = True
      EDGE_TRIGGER_COUPLING = {}
    else:
      # 9000 Series, 9000H Series, and S-Series oscilloscopes
      match = re.search(r'([M|D]S[O|A]S*)[0-9]+(?=[A-Z])', self.scope_name)
      if match:
        CHANNEL_COUPLING = {
            instrument.ChannelCoupling.DC: 'DC',
        }
        EDGE_TRIGGER_COUPLING = {
            instrument.EdgeTriggerCoupling.DC: 'DC',
            instrument.EdgeTriggerCoupling.DCREJECT: (
                'AC'
            ),  # S/B the same as AC coupling
            instrument.EdgeTriggerCoupling.LFREJECT: 'LFReject',
        }
      else:
        raise MatchError(
            '# of Channels cannot be found, please check your model!'
        )
    # this is an empty dict, just reinit as ordereddict for keeping meas
    # order with scope
    self.measurement_item: collections.OrderedDict[
        int, self.MeasurementConfig
    ] = collections.OrderedDict()

  ####################################################################################
  # S Series
  ####################################################################################
  def set_channel_position(self, channel, position):
    # """Configures Scope channel position.

    # Based on given channel number and position (DIV).
    # Negative moves down, positive moves up.

    # Args:
    #     channel (int): The number of the channel
    #     position (float): The position of the channel

    # Keysight S-Series:
    #     sets the value that is represented at center screen for the selected
    # channel.
    #     this function the same as "set_channel_offset"
    # """
    self.data_handler.send(f':CHANnel{channel}:OFFSet {-1 * position}')

  def set_channel_attenuation(self, channel, attenuation_factor):
    # """Configures the selected Scope channel's attenuation_factor.

    # Args:
    #     channel (int): The number of the channel
    #     attenuation_factor (int): The attenuation factor

    # Keysight S-Series:
    #     attenuation_factor: 0.0001 to 1000, A real number from 0.0001 to 1000
    # for the RATio attenuation units or from -80 dB to 60 dB for the DECibel
    # attenuation units.
    # """
    self.data_handler.send(f':CHANnel{channel}:PROBe {attenuation_factor}')

  def set_channel_coupling(self, channel, mode, impedance):
    # """Keysight S-Series:

    # input coupling & impedance: AC | DC | DC50 | LFR1|LFR2, selects the input
    # coupling, impedance, and LF/HF reject for the specified channel.
    #     DC — DC coupling, 1 MΩ impedance
    #     DC50 | DCFifty — DC coupling, 50Ω impedance
    #     AC — AC coupling, 1 MΩ impedance
    #     LFR1 | LFR2 — AC 1MΩ input impedance
    # """
    if (
        mode == instrument.ChannelCoupling.DC
        and impedance == 1_000_000
        and not self.model_type_90k
    ):
      par_imp = 'DC'
    elif mode == instrument.ChannelCoupling.DC and impedance == 50:
      par_imp = 'DCFifty'
    elif (
        mode == instrument.ChannelCoupling.AC
        and impedance == 1_000_000
        and not self.model_type_90k
    ):
      par_imp = 'AC'
    else:
      raise ValueError(
          'The Keysight Infiniium '
          f'{self.scope_name} does not support this '
          'coupling combination.'
      )
    self.data_handler.send(f':CHANnel{channel}:INPut {par_imp}')

  def set_channel_offset(self, channel, voffset):
    # """Keysight S-Series:

    # sets the value that is represented at center screen for the selected
    # channel.
    # this function the same as "set_channel_position"
    # """
    self.data_handler.send(f':CHANnel{channel}:OFFSet {-1 * voffset}')

  def set_channel_division(self, channel, vdiv):
    # """Keysight S-Series:

    # sets the vertical scale, or units per division, ofthe selected channel.
    # """
    self.data_handler.send(f':CHANnel{channel}:SCALe {vdiv}')

  def set_channel_on_off(self, channel, enable):
    # """Keysight S-Series:

    # turns the display of the specified channel on or off.
    # """
    self.data_handler.send(f':CHANnel{channel}:DISPlay {int(enable)}')

  def set_channel_bandwidth(self, channel, value, enable):
    # """Keysight S-Series: controls an internal low-pass filter.

    # value: The maximum value is the sample rate / 2. The minimum value is 1000
    # Hz.
    # """
    if enable:
      if value == 20_000_000 or value == 20_000_000:
        self.data_handler.send(f':CHANnel{channel}:BWLimit {value}')
      else:
        self.data_handler.send(f':CHANnel{channel}:ISIM:BWLimit ON')
        self.data_handler.send(f':CHANnel{channel}:ISIM:BANDwidth {value}')
    else:
      self.data_handler.send(f':CHANnel{channel}:BWLimit OFF')

  def set_channel_labels(self, channel, value):
    self.data_handler.send(':DISPlay:LABel ON')
    self.data_handler.send(f":CHANnel{channel}:LABel '{value}'")

  def set_channel_labels_position(self, channel, x, y):
    """Sets the channel label position based on values given in x and y.

    Args:
        channel (int): The number of the channel
        x (float): X position
        y (float): Y position

    ***Keysight S-Series does not support this function.
    Calling this function will raise an error***
    """
    raise ValueError('Keysight S-Series does not support this function. ')

  def get_channel_labels(self, channel):  # -> list[str]
    # """Keysight S-Series:

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
    # """Keysight S-Series:

    # attenuation_factor: 0.0001 to 1000, A real number from 0.0001 to 1000 for
    # the RATio attenuation units or from -80 dB
    #     to 60 dB for the DECibel attenuation units.
    # vertical_coupling: AC | DC, The coupling for each analog channel can be
    # set to AC or DC.
    # input coupling & impedance: AC | DC | DC50 | LFR1|LFR2, selects the input
    # coupling, impedance, and LF/HF reject for the specified channel.
    #     DC — DC coupling, 1 MΩ impedance
    #     DC50 | DCFifty — DC coupling, 50Ω impedance
    #     AC — AC coupling, 1 MΩ impedance
    #     LFR1 | LFR2 — AC 1MΩ input impedance
    # """
    self.data_handler.send(f':CHANnel{channel}:DISPlay {int(channel_enable)}')
    self.data_handler.send(f':CHANnel{channel}:RANGe {vertical_range}')
    self.data_handler.send(f':CHANnel{channel}:OFFSet {-1 * vertical_offset}')
    self.data_handler.send(f':CHANnel{channel}:PROBe {probe_attenuation}')
    input_type = util.get_from_dict(CHANNEL_COUPLING, vertical_coupling)
    if (
        self.model_type_90k
        and vertical_coupling == instrument.ChannelCoupling.DC
    ):
      input_type = 'DC50'

    self.data_handler.send(f':CHANnel{channel}:INPut {input_type}')

  def config_edge_trigger(self, channel, level, edge, mode):
    """Select a channel to use as trigger.

    Set Positive or Negative Trigger edge, set a trigger level in volts, and
    choose between (AC;DC;LF;HF) Trigger Coupling mode.

    Args:
        channel (int): The number of the channel
        level (float): Trigger level
        edge (instrument.EdgeTriggerSlope): The slope for an edge trigger
        mode (instrument.EdgeTriggerCoupling): Trigger mode

    ***Coupling is only support on Keysight Infiniium 9000 Series, 9000H Series,
    and S-Series. Setting this for other series will NOT raise an error, but
    will be ignored.***
    """
    self.data_handler.send(':TRIGger:MODE EDGE')
    self.data_handler.send(f':TRIGger:EDGE:SOURce CHANnel{channel}')
    if not self.model_type_90k:
      self.data_handler.send(
          ':TRIGger:EDGE:COUPling'
          f' {util.get_from_dict(EDGE_TRIGGER_COUPLING, mode)}'
      )
    self.data_handler.send(f':TRIGger:LEVel CHANnel{channel},{level}')
    self.data_handler.send(
        f':TRIGger:EDGE:SLOPE {util.get_from_dict(EDGE_TRIGGER_SLOPE, edge)}'
    )

  def set_aux_trigger(self, enable):
    # """Keysight S-Series:

    # enable=True: triggers on the rear panel EXT TRIG IN signal.
    # """
    if enable:
      self.data_handler.send(':TRIGger:EDGE:SOURce AUX')

  def config_continuous_acquisition(self, en_cont_acq, en_auto_trig):
    # """Keysight S-Series:

    # selects the trigger sweep mode
    #     sweep mode: AUTO | TRIGgered | SINGle
    # """
    if en_cont_acq and en_auto_trig:  # Auto trigger
      self.data_handler.send(':TRIGger:SWEep AUTO')
      self.data_handler.send(':RUN')
    elif en_cont_acq and not en_auto_trig:  # Normal trigger
      self.data_handler.send(':TRIGger:SWEep TRIGgered')
      self.data_handler.send(':RUN')
    elif not en_cont_acq:  # Single trigger
      self.data_handler.send(':TRIGger:SWEep TRIGgered')
      self.data_handler.send(':SINGle')

  def config_rolling_mode(self, enable):
    # """Keysight S-Series:

    # sets the current time base: MAIN | WINDow | XY | ROLL
    # enable=True: rolling mode
    # enable=False: normal time base mode(default)
    # """
    self.data_handler.send(f':TIMebase:ROLL:ENABLE {int(enable)}')

  def config_pulse_width_trigger(
      self, channel, mode, slope, level, low_limit, hi_limit
  ):
    # """Keysight S-Series:

    # mode: does not support "OUT (Out of Range)"
    # slope: NEGative | POSitive
    # if mode="WITHIN(In Range)":
    #     low_limit: 250ps to 30ns
    #     hi_limit: 250ps to 10s
    # """

    def _config_pulse_width(
        direction: str,
        number: str = '',
    ) -> None:
      limit_maps = {
          'LTHan': hi_limit,
          'GTHan': low_limit,
      }
      polarity = util.get_from_dict(PULSE_TRIGGER_SLOPE, slope)
      if number:
        self.data_handler.send(f':TRIGger:SEQuence:TERM{number} PWIDth{number}')

      self.data_handler.send(f':TRIGger:PWIDth{number}:SOURce CHANnel{channel}')
      self.data_handler.send(f':TRIGger:PWIDth{number}:DIRection {direction}')
      self.data_handler.send(f':TRIGger:PWIDth{number}:POLarity {polarity}')
      self.data_handler.send(
          f':TRIGger:PWIDth{number}:WIDTh {limit_maps[direction]}'
      )

    if mode not in PULSE_TRIGGER_MODE:
      raise ValueError('Keysight S-Series does not support this function. ')

    if mode == instrument.PulseTriggerMode.WITHIN:
      self.data_handler.send(':TRIGger:MODE SEQuence')
      _config_pulse_width('LTHan', '1')
      _config_pulse_width('GTHan', '2')
    else:
      self.data_handler.send(':TRIGger:MODE PWIDth')

      if mode == instrument.PulseTriggerMode.LESS:
        _config_pulse_width('LTHan')

      elif mode == instrument.PulseTriggerMode.MORE:
        _config_pulse_width('GTHan')

    self.data_handler.send(f':TRIGger:LEVel CHANnel{channel},{level}')

  def config_timeout_trigger(self, channel, polarity, level, timeout):
    pol = util.get_from_dict(TIMEOUT_TRIG_POLARITY, polarity)
    self.data_handler.send(':TRIGger:MODE TIMeout')
    self.data_handler.send(f':TRIGger:TIMeout:CONDition {pol}')
    self.data_handler.send(f':TRIGger:TIMeout:SOURce CHAN{channel}')
    self.data_handler.send(f':TRIGger:TIMeout:TIME {timeout}')
    self.data_handler.send(f':TRIGger:LEVel CHANnel{channel},{level}')

  def set_horiz_division(self, hor_div, delay, sample_value, sample_type):
    # """Keysight S-Series:

    # sample_value: AUTO | MAX | <sample_rate>, sets the desired acquisition
    # sample rate:
    # sample_type: SRATe | POINts
    #     if sample_type=SRATe(SAMPLERATE) : POINts(SAMPLESIZE) set to AUTO
    #     if sample_type=POINts(SAMPLESIZE) : SRATe(SAMPLERATE) set to AUTO
    # """
    self.data_handler.send(f':TIMebase:SCALe {hor_div}')
    self.data_handler.send(f':TIMebase:POSition {delay}')
    if sample_type == instrument.HorizonType.SAMPLESIZE:
      self.data_handler.send(':ACQuire:SRATe AUTO')
      self.data_handler.send(f':ACQuire:POINts {sample_value}')
    elif sample_type == instrument.HorizonType.SAMPLERATE:
      self.data_handler.send(':ACQuire:POINts AUTO')
      self.data_handler.send(f':ACQuire:SRATe {sample_value}')

  def set_horiz_offset(self, hor_offset):
    # """Keysight S-Series:

    # sets the time interval between the trigger event and the display reference
    # point on the screen.
    # """
    self.data_handler.send(f':TIMebase:position {hor_offset}')

  def _set_meas_reference(self, low, mid, high, r_type, meas):
    """Internal function for issuing measurement thresholds.

    Args:
      low (float): Low reference level
      mid (float): Mid reference level
      high (float): High reference level
      r_type (str): Set reference level as percentage or absolute value
      meas (int): The measurement number
    """
    chan = self.measurement_item[meas].meas_args['channel']
    # General
    self.data_handler.send(
        f':MEASure:THResholds:GENeral:METHod CHAN{chan}, {r_type}'
    )
    self.data_handler.send(
        f':MEASure:THResholds:GENeral:{r_type} CHAN{chan},{high},{mid},{low}'
    )
    # Rise/Fall
    self.data_handler.send(
        f':MEASure:THResholds:RFALl:METHod CHAN{chan}, {r_type}'
    )
    self.data_handler.send(
        f':MEASure:THResholds:RFALl:{r_type} CHAN{chan},{high},{mid},{low}'
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
    reference assignments***

    Args:
        low (float): Low reference level
        mid (float): Mid reference level
        high (float): High reference level
        mid2 (float): Mid2 reference level
        reference_type (instrument.ReferenceType): Set reference level as
          percentage or absolute value
        reference_scope (instrument.ReferenceScope): Set reference scope as
          local or global
        meas_number (int | None): Measurement number to apply the reference if
          in local. This can also toggle local or global for measurement if
          supplied.
    """
    # Check to see if this is a global or local scope
    # If global we want to target all existing measurements that scoped globally
    r_type = util.get_from_dict(REFERENCE_TYPE, reference_type)
    if reference_scope == instrument.ReferenceScope.GLOBAL:
      for meas, meas_item in self.measurement_item.items():
        # m_type = meas_item.meas_type
        # Check to see if there is an existing reference setup in local scope
        # If not, assumes measurement is in default state which is Global
        ref = self.measurement_ref.get(f'{meas}_ref')

        if ref:
          if ref.reference_scope == instrument.ReferenceScope.LOCAL:
            if meas_number != meas:
              continue
          else:
            ref.reference_scope = instrument.ReferenceScope.GLOBAL
        channels = []
        for reference in self.measurement_ref.values():
          if reference.reference_scope == instrument.ReferenceScope.LOCAL:
            channels.append(
                self.measurement_item[reference.meas_number].meas_args[
                    'channel'
                ]
            )
        if (
            meas_item.displayed
            and meas_item.meas_args['channel'] not in channels
        ):
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
    # """Keysight S-Series:

    # if enable=False and meas_number=0, all measurements and markers on the
    # screen will be cleared
    # if enable=False and meas_number>0, only selected measurements and markers
    # on the screen will be cleared
    # """
    try:
      meas = self.measurement_item[meas_number]
      if enable:
        if not meas.displayed:
          self.set_measurement(
              meas.meas_args['channel'],
              meas_number,
              meas.meas_args['measurement_type'],
          )
        return

      if meas_number < 0:
        raise RuntimeError('The measurement number should larger than 0')

      if meas_number == 0:
        self.data_handler.send(':MEASure:CLEar')
        for setting in self.measurement_item.values():
          setting.displayed = False
        return

      self.data_handler.send(f':MEASurement{meas.meas_args["pos"]}:CLEar')
      self.measurement_item[meas_number].displayed = False
      for setting in self.measurement_item.values():
        if setting.meas_args['pos'] > meas.meas_args['pos']:
          setting.meas_args['pos'] = setting.meas_args['pos'] - 1
      count = 1
      for setting in self.measurement_item.values():
        meas_disp = setting.meas_args['pos']
        if setting.displayed:
          self.data_handler.send(f':MEASurement{meas_disp}:POSition {count}')
          self.wait_task(3)
          count += 1

    except KeyError:
      pass

  def set_measurement_statistics(self, enable):
    """Enable or disable measurement statistics.

    Args:
        enable (bool):

    ***The Infiniium Series Does not allow the GUI to turn off
    the statistic display via remote command.***
    """
    warnings.warn(
        'The Keysight Infiniium Series does not allow the statistical display'
        'to be turned off via remote command'
    )

  def set_measurement(self, channel, meas_number, measurement_type):
    # """Keysight S-Series:

    # refers to the dict "MEASUREMENT_TYPE"
    # """
    try:
      if self.measurement_item[meas_number]:
        measurement = self.measurement_item[meas_number]
        if measurement.meas_args['measurement_type'] != measurement_type:
          self.set_measurement_on_off(meas_number, False)
    except KeyError:
      pass
    self.measurement_item[meas_number] = self.MeasurementConfig(
        meas_type='set_measurement',
        meas_args={
            'channel': channel,
            'meas_number': meas_number,
            'measurement_type': measurement_type,
            # this is the positioned store in the scope,
            # not necessary the display
            'pos': 1,
        },
        displayed=True,
    )

    for meas in self.measurement_item.values():
      if meas.meas_args['meas_number'] != meas_number:
        meas.meas_args['pos'] += 1

    mea_type = util.get_from_dict(MEASUREMENT_TYPE, measurement_type)
    pre_command = util.get_from_dict(
        ADDITIONAL_MEASUREMENT_CMD_PRE, measurement_type
    )
    post_command = util.get_from_dict(
        ADDITIONAL_MEASUREMENT_CMD_POST, measurement_type
    )
    self.data_handler.send(
        f':MEASure:{mea_type} {pre_command}CHANnel{channel}, {post_command}'
    )
    self.data_handler.query('*OPC?')

    count = 1
    for _, setting in self.measurement_item.items():
      meas = setting.meas_args['pos']
      if setting.displayed:
        self.data_handler.send(f':MEASurement{meas}:POSition {count}')
        self.wait_task(3)
        count += 1

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
    # """Keysight S-Series:

    # places the instrument in the continuous measurement mode and starts a
    # delay measurement.
    # start_edge: RISing | FALLing | EITHer
    # end_edge: RISing | FALLing | EITHer
    # """

    try:
      if self.measurement_item[meas_number]:
        measurement = self.measurement_item[meas_number]
        if measurement.meas_args['measurement_type'] == 'DELTatime':
          pass
        else:
          self.set_measurement_on_off(meas_number, False)
    except KeyError:
      pass
    self.measurement_item[meas_number] = scope.Scope.MeasurementConfig(
        meas_type='set_delta',
        meas_args={
            'channel': channel1,
            'meas_number': meas_number,
            'measurement_type': 'DELTatime',
            # this is the positioned store in the scope,
            # not necessary the display
            'pos': 1,
        },
        displayed=True,
    )
    for meas in self.measurement_item.values():
      if meas.meas_args['meas_number'] != meas_number:
        meas.meas_args['pos'] += 1

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
    ch1_meth = self.data_handler.query(
        f':MEASure:THResholds:GENeral:METHod? CHAN{channel1}'
    )
    if ch1_meth == self.PERC_10_90 or ch1_meth == self.PERC_20_80:
      ch1_meth = 'PERC'
    ch1_high, _, ch1_low, *_ = self.data_handler.query(
        f':MEASure:THResholds:GENeral:{ch1_meth}? CHANnel{channel1}'
    ).split(',')
    ch2_meth = self.data_handler.query(
        f':MEASure:THResholds:GENeral:METHod? CHAN{channel2}'
    )
    if ch2_meth == self.PERC_10_90 or ch1_meth == self.PERC_20_80:
      ch2_meth = 'PERC'
    ch2_high, _, ch2_low, *_ = self.data_handler.query(
        f':MEASure:THResholds:GENeral:{ch2_meth}? CHANnel{channel2}'
    ).split(',')

    self.data_handler.send(
        f':MEASure:THResholds:GENeral:METHod CHAN{channel1}, {ch1_meth}'
    )
    self.data_handler.send(
        f':MEASure:THResholds:GENeral:{ch1_meth} CHAN{channel1},'
        f'{ch1_high},{ch_ref.mid},{ch1_low}'
    )
    self.data_handler.send(
        f':MEASure:THResholds:GENeral:METHod CHAN{channel2}, {ch2_meth}'
    )
    self.data_handler.send(
        f':MEASure:THResholds:GENeral:{ch2_meth} CHAN{channel2},'
        f'{ch2_high},{ch_ref.mid2},{ch2_low}'
    )
    self.data_handler.send(
        f':MEASure:DELTatime:DEFine {startedge},1,MIDDLE,{endedge},1,MIDDLE'
    )
    self.data_handler.send(f':MEASure:DELTatime CHAN{channel1},CHAN{channel2}')

    self.data_handler.query('*OPC?')

    count = 1
    for _, setting in self.measurement_item.items():
      meas = setting.meas_args['pos']
      if setting.displayed:
        self.data_handler.send(f':MEASurement{meas}:POSition {count}')
        self.wait_task(3)
        count += 1

  def set_cursor(self, channel, cursor_type, cur1_pos, cur2_pos):
    # """Keysight S-Series:

    # cursor_type: OFF | MANual | WAVeform | MEASurement | XONLy | YONLy
    #     *OFF — Removes the marker information from the display
    #     HOR — Enables manual placement of X (horizontal) markers
    #     VER — Enables manual placement of Y (vertical) markers
    #     *WAVeform — Tracks the current waveform
    # """
    if cursor_type == instrument.CursorType.OFF:
      self.data_handler.send(
          f':MARKer:MODE {util.get_from_dict(CURSOR_TYPE, cursor_type)}'
      )

    else:
      self.data_handler.send(f':MARKer:X1Y1source CHANnel{channel}')
      self.data_handler.send(f':MARKer:X2Y2source CHANnel{channel}')
      self.data_handler.send(
          f':MARKer:MODE {util.get_from_dict(CURSOR_TYPE, cursor_type)}'
      )

      if cursor_type == instrument.CursorType.HOR:
        self.data_handler.send(f':MARKer:X1Position {cur1_pos}')
        self.data_handler.send(f':MARKer:X2Position {cur2_pos}')
        self.data_handler.send(f':MARKer:Y1Position {cur1_pos}')
        self.data_handler.send(f':MARKer:Y2Position {cur2_pos}')
      elif cursor_type == instrument.CursorType.VER:
        self.data_handler.send(f':MARKer:X1Position {cur1_pos}')
        self.data_handler.send(f':MARKer:X2Position {cur2_pos}')
        self.data_handler.send(f':MARKer:Y1Position {cur1_pos}')
        self.data_handler.send(f':MARKer:Y2Position {cur2_pos}')
    # else:
    #     self.data_handler.send(':MARKer:X1Y1source CHANnel' + str(channel))
    #     self.data_handler.send(':MARKer:X2Y2source CHANnel' + str(channel))
    #     self.data_handler.send(':MARKer:MODE WAVeform')
    #     self.data_handler.send(':MARKer:X1Position ' + str(cur1_pos))
    #     self.data_handler.send(':MARKer:X2Position ' + str(cur2_pos))
    #     self.data_handler.send(':MARKer:Y1Position ' + str(cur1_pos))
    #     self.data_handler.send(':MARKer:Y2Position ' + str(cur2_pos))

  def set_infinite_persistence(self, enable):
    # """Keysight S-Series:

    # specifies the persistence setting, mode: MINimum | INFinite | <time>
    # If enable=True, indicates infinite persistence.
    # If enable=False, indicates zero persistence(default)
    # """
    if enable:
      self.data_handler.send(':DISPlay:PERSistence INFinite')
    else:
      self.data_handler.send(':DISPlay:PERSistence MIN')

  def clear_persistence(self):
    # """Keysight S-Series:

    # Clear the display
    # """
    self.data_handler.send(':CDISplay')

  def wait_acquisition_complete(self, timeout):
    rnum = 0
    t0 = time.time()
    while time.time() * 1000 - t0 * 1000 < timeout:
      time.sleep(0.1)
      self.data_handler.send(':ADER?')
      rnum = int(self.data_handler.recv())
      if rnum == 1:
        break
    else:
      raise ValueError(f'Timeout({timeout}) - wait_acquisition_complete')

  def get_acquisition(self):
    # """Keysight S-Series:

    # query returns the run state (RUN | STOP | SING)
    # """
    self.data_handler.send(':RSTate?')
    readstr = self.data_handler.recv()

    return readstr

  def arm_single_trig(self):
    # self.data_handler.send (":TRIGger:SWEep SINGle")
    # AUTO | TRIGgered | SINGle
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
    # """Keysight S-Series:

    # clears the measurement results from the screen and disables all previously
    # enabled measurements
    # """
    self.data_handler.send(':MEASure:CLEar')
    for item, setting in self.measurement_item.items():
      # because using Measure:Clear actually doesn't set
      # the displayed key, we need to set it to false first
      setting.displayed = False
      self.set_measurement_on_off(item, True)

  def get_measurement_statistics(self, meas_number):
    self.data_handler.send(':MEASure:STATistics?')
    rstr_statistics = self.data_handler.recv()

    self.data_handler.send(':MEASure:STATistics ON')
    self.data_handler.send(
        ':MEASure:RESults? GORDered'
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
    # """Keysight 4000X-Series:

    # clears all selected measurements and markers from the screen.
    # """
    rnum = 0
    t0 = time.time()
    while time.time() - t0 < timeout:
      time.sleep(1)
      self.data_handler.send(':PDER?')
      rnum = int(self.data_handler.recv())
      if rnum == 1:
        break
    else:
      raise ValueError(f'Timeout({timeout}) - wait_task')

  def wait_trigger_ready(self, timeout):
    # """Keysight S-Series:

    # Checking for Armed Status
    # The Armed Event Register bit goes low (0) when it is read using
    # :AER? or when a *CLS command is issued.
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
      raise ValueError('Timeout({timeout}) - wait_trigger_ready')

  def force_trigger(self):
    self.data_handler.send(':TRIGger:FORCe')

  def fetch_delta_measurement(
      self, channel1, channel2, start_edge, end_edge, mid, mid2
  ):
    # query current channel setting and preserve it
    # here we make a big assumption that the settings are the same reference
    # type, usually don't change
    # query return is in the format of THR,<TYPE>,<HIGH>,<MID>,<LOW>
    ch1_meth = self.data_handler.query(
        f':MEASure:THResholds:GENeral:METHod? CHAN{channel1}'
    )
    if ch1_meth == self.PERC_10_90 or ch1_meth == self.PERC_20_80:
      ch1_meth = 'PERC'
    ch1_high, ch1_mid, ch1_low, *_ = self.data_handler.query(
        f':MEASure:THResholds:GENeral:{ch1_meth}? CHANnel{channel1}'
    ).split(',')
    ch2_meth = self.data_handler.query(
        f':MEASure:THResholds:GENeral:METHod? CHAN{channel2}'
    )
    if ch2_meth == self.PERC_10_90 or ch2_meth == self.PERC_20_80:
      ch2_meth = 'PERC'
    ch2_high, ch2_mid, ch2_low, *_ = self.data_handler.query(
        f':MEASure:THResholds:GENeral:{ch2_meth}? CHANnel{channel2}'
    ).split(',')

    self.data_handler.send(
        f':MEASure:THResholds:GENeral:METHod CHAN{channel1}, PERC'
    )
    self.data_handler.send(
        f':MEASure:THResholds:GENeral:{ch1_meth} CHAN{channel1},'
        f'{ch1_high},{mid},{ch1_low}'
    )
    self.data_handler.send(
        f':MEASure:THResholds:GENeral:METHod CHAN{channel2}, PERC'
    )
    self.data_handler.send(
        f':MEASure:THResholds:GENeral:{ch2_meth} CHAN{channel2},'
        f'{ch2_high},{mid2},{ch2_low}'
    )
    startedge = util.get_from_dict(DELTA_SLOPE, start_edge)
    endedge = util.get_from_dict(DELTA_SLOPE, end_edge)
    self.data_handler.send(
        f':MEASure:DELTatime:DEFine {startedge},1,MIDDLE,{endedge},1,MIDDLE'
    )
    self.data_handler.send(f':MEASure:DELTatime CHAN{channel1},CHAN{channel2}')

    self.data_handler.send(
        ':MEASure:THResholds:GENeral:METHod CHANnel' + str(channel1) + ', PERC'
    )
    self.data_handler.send(
        f':MEASure:DELTatime? CHANnel{channel1},CHAN{channel2}'
    )
    # read
    rstring = self.data_handler.recv()
    self.data_handler.query('*OPC?')
    # set the references back to their original settings
    self.data_handler.send(
        f':MEASure:THResholds:GENeral:METHod CHAN{channel1}, {ch1_meth}'
    )
    self.data_handler.send(
        f':MEASure:THResholds:GENeral:{ch1_meth} CHAN{channel1},'
        f'{ch1_high},{ch1_mid},{ch1_low}'
    )
    self.data_handler.send(
        f':MEASure:THResholds:GENeral:METHod CHAN{channel2}, {ch2_meth}'
    )
    self.data_handler.send(
        f':MEASure:THResholds:GENeral:{ch2_meth} CHAN{channel2},'
        f'{ch2_high},{ch2_mid},{ch2_low}'
    )

    return rstring

  def fetch_measurement(self, channel, measurement_type):
    mea_type = util.get_from_dict(MEASUREMENT_TYPE, measurement_type)
    pre_command = ADDITIONAL_MEASUREMENT_CMD_PRE.get(measurement_type, '')
    post_command = ADDITIONAL_MEASUREMENT_CMD_POST.get(measurement_type, '')
    self.data_handler.send(
        f':MEASure:{mea_type}? {pre_command}CHANnel{channel}, {post_command}'
    )
    result = self.data_handler.recv()
    return result

  def fetch_measure_number(self, measure_number):
    self.data_handler.send(':MEASure:STATistics CURR')
    rstring = self.data_handler.send(':MEASure:RESults?')
    rstring = self.data_handler.recv()
    rstring = rstring.split(',')
    if measure_number > len(rstring) or measure_number <= 0:
      rstring = 'na'
    else:
      rstring = rstring[measure_number - 1]

      # reverse
      # rstring= rstring[len(rstring) - measure_number]

    return rstring

  def fetch_waveform(self, channel):
    self.data_handler.send(f':WAVeform:SOURce CHANnel{channel}')
    self.data_handler.send(
        ':WAVeform:FORMat BYTE'
    )  # BYTE | BINary | BYTE | WORD | FLOat, default WORD
    # Get numeric values for later calculations.
    x_increment = float(self.data_handler.query(':WAVeform:XINCrement?'))
    x_origin = float(self.data_handler.query(':WAVeform:XORigin?'))
    y_increment = float(self.data_handler.query(':WAVeform:YINCrement?'))
    y_origin = float(self.data_handler.query(':WAVeform:YORigin?'))
    # Get the waveform data.
    self.data_handler.send(':WAVeform:STReaming OFF')
    s_data = self.data_handler.query_raw(b':WAVeform:DATA?')
    value = struct.unpack('%db' % len(s_data), s_data)
    #
    dtime = []
    dvol = []
    #
    for i in range(0, len(value) - 1):
      dtime.append(x_origin + (i * x_increment))
      dvol.append((float(value[i]) * y_increment) + y_origin)

    return dtime, dvol

  # ===========================================================================================

  def set_search_edges_on_off(self, enable):
    """Used to enable or disable a waveform edge search.

    Args:
      enable (bool): Turn on or off a waveform edge search

    Keysight S-Series:
            Keysight S-Series does not support this function.
    """
    raise ValueError('Keysight S-Series does not support this function. ')

  def set_search_edges(self, channel, edge, level):
    """Used to set up a waveform edge search.

    Args:
      channel (int): Channel to perform the search on
      edge (instrument.EdgeTriggerSlope): Select rising, falling, or both (if
        available)
      level (float): Level the threshold to qualify for search results

    Keysight S-Series:
            Keysight S-Series does not support this function.
    """
    raise ValueError('Keysight S-Series does not support this function. ')

  def get_search_edges(self, start_index=0, count=-1):
    """Used to retrieve an edge search result.

    Args:
      start_index (int): The starting index of the first result. Default is 0.
      count (int): Number of results to return. Default is -1 for all.

    Returns (list[float[): A list of floating point of x-axis time index. If
        index, size, or search parameters are invalid, returns an empty list.

    Keysight S-Series:
            Keysight S-Series does not support this function.
    """
    raise ValueError('Keysight S-Series does not support this function. ')

  # ===========================================================================================

  def load_settings_file(self, path):
    with open(path, 'rb') as f:
      setup_bytes = f.read()  # setup.set

    self.data_handler.query_raw(b':SYSTem:SETup ' + setup_bytes)
    self.wait_task()

  def save_settings_file(self, path):
    setup_bytes = self.data_handler.query_raw(b'*LRN?')
    with open(path, 'wb') as f:  # setup.set
      # f.write(bytearray(setup_bytes))
      f.write(setup_bytes)

  def _get_screenshot(self, path):
    # """exampel : path= :DISK:SAVE:IMAGe "D:\S_image2.png", PNG."""
    self.data_handler.send(f':DISK:SAVE:IMAGe {path}, PNG')

  def save_screenshot(self, path):
    self.data_handler.send(':DISPlay:DATA? PNG')
    _, read_size = self.data_handler.recv(size=2)
    data_size = self.data_handler.recv(size=int(read_size))
    img = self.data_handler.recv_raw(size=int(data_size))
    with open(path, 'wb') as f:
      f.write(bytearray(img))
    print('Screen image written to' + path)

  def auto_set(self):
    self.data_handler.send(':AUToscale')

  def set_display_style(self, mode):
    # """Keysight S-Series:
    #         mode: TAB | SVERtical | SHORizontal
    #             TAB (or CUSTom) — Tabbed window layout
    #             SVERtical — Stack windows vertically
    #             SHORizontal — Stack windows horizontally.
    #     """
    self.data_handler.send('%s' % ':DISPlay:Layout ' + str(mode))

  def get_error_status(self):
    errstr = self.data_handler.query(':SYSTem:ERRor? STRing')
    return errstr

  def set_measurement_reference_ch(
      self, channel, low, mid, high, reference_type
  ):
    ref_type = util.get_from_dict(REFERENCE_TYPE, reference_type)
    # Genral
    self.data_handler.send(
        f':MEASure:THResholds:GENeral:METHod CHANnel{channel},{ref_type}'
    )
    self.data_handler.send(
        f':MEASure:THResholds:GENeral:{ref_type}CHANnel{channel},{high},{mid},{low}'
    )
    # Rise/Fall
    self.data_handler.send(
        f':MEASure:THResholds:RFALl:METHod CHANnel{channel},{ref_type}'
    )
    self.data_handler.send(
        f':MEASure:THResholds:RFALl:{ref_type} CHANnel{channel},{high},{mid},{low}'
    )  # offset
