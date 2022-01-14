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

"""Parent Abstract Module of Scope."""

from __future__ import annotations

import abc
import dataclasses
import pathlib
from typing import Any

from py_lab_hal.cominterface import cominterface
from py_lab_hal.instrument import instrument


class Scope(instrument.Instrument, metaclass=abc.ABCMeta):
  """Parent Abstract Class of Scope."""

  @dataclasses.dataclass
  class ReferenceLevels:
    """References level for timing measurements."""

    low: float
    mid: float
    high: float
    mid2: float
    reference_type: instrument.ReferenceType
    reference_scope: instrument.ReferenceScope
    meas_number: int | None

  @dataclasses.dataclass
  class MeasurementConfig:
    meas_type: str
    meas_args: dict[str, Any]
    displayed: bool

  def __init__(
      self,
      com: cominterface.ComInterfaceClass,
      inst_config: instrument.InstrumentConfig,
  ) -> None:
    super().__init__(com, inst_config)
    self.measurement_ref: dict[str, Scope.ReferenceLevels] = {
        'global_ref': Scope.ReferenceLevels(
            10,
            50,
            90,
            50,
            instrument.ReferenceType.PER,
            instrument.ReferenceScope.GLOBAL,
            None,
        )
    }
    self.measurement_item: dict[int, Scope.MeasurementConfig] = {}

  def _load_measurement(self, measurement_number: int) -> None:
    """The helper function for loading the measurement config.

    Args:
        measurement_number (int): The measurement number

    Raises:
        RuntimeError: _description_
    """
    measurement_config = self.measurement_item[measurement_number]
    if measurement_config.meas_type == 'set_measurement':
      self.set_measurement(**measurement_config.meas_args)
    elif measurement_config.meas_type == 'set_delta_measurement':
      self.set_delta_measurement(**measurement_config.meas_args)
    else:
      raise RuntimeError('The type config is wrong')

  @abc.abstractmethod
  def set_channel_position(
      self,
      channel: int,
      position: float,
  ) -> None:
    """Configures Scope channel position.

    Based on given channel number and position (DIV).
    Negative moves down, positive moves up.

    Args:
        channel (int): The number of the channel
        position (float): The position of the channel
    """
    pass

  @abc.abstractmethod
  def set_channel_attenuation(
      self,
      channel: int,
      attenuation_factor: int,
  ) -> None:
    """Configures the selected Scope channel's attenuation_factor.

    Args:
        channel (int): The number of the channel
        attenuation_factor (int): The attenuation factor
    """
    pass

  @abc.abstractmethod
  def set_channel_coupling(
      self,
      channel: int,
      mode: instrument.ChannelCoupling,
      impedance: int,
  ) -> None:
    """Sets the selected channel's coupling.

    Args:
        channel (int): The number of the channel
        mode (instrument.ChannelCoupling): The DC or AC
        impedance (int): The impedance of the channel in ohm
    """
    pass

  @abc.abstractmethod
  def set_channel_offset(
      self,
      channel: int,
      voffset: float,
  ) -> None:
    """Sets the selected channel's vertical offset voltage, voffset.

    Negative moves down, positive moves up.

    Args:
        channel (int): The number of the channel
        voffset (float): The voffset of the channel
    """
    pass

  @abc.abstractmethod
  def set_channel_division(self, channel: int, vdiv: float) -> None:
    """Sets the selected channel's voltager per division verticale scale.

    Args:
        channel (int): The number of the channel
        vdiv (float): The vertical division of the channel
    """
    pass

  @abc.abstractmethod
  def set_channel_on_off(self, channel: int, enable: bool) -> None:
    """Choose whether or not to display the selected channel waveform/trace.

    Args:
        channel (int): The number of the channel
        enable (bool): Enable or not to display
    """
    pass

  @abc.abstractmethod
  def set_channel_bandwidth(
      self,
      channel: int,
      value: float,
      enable: bool,
  ) -> None:
    """set the bandwidth limit.

    Choose whether or not to enable BW Limit for the selected channel and if
    enabled, the bandwidth limit to set by value.

    Args:
        channel (int): The number of the channel
        value (float): value of bandwidth
        enable (bool): Enable or not to set the bandwidth limit
    """
    pass

  @abc.abstractmethod
  def set_channel_labels(self, channel: int, value: str) -> None:
    """Sets the selected channel trace name based on value.

    Args:
        channel (int): The number of the channel
        value (str): Text
    """
    pass

  @abc.abstractmethod
  def set_channel_labels_position(
      self,
      channel: int,
      x: float,
      y: float,
  ) -> None:
    """Sets the channel label position based on values given in x and y.

    Args:
        channel (int): The number of the channel
        x (float): X position
        y (float): Y position
    """
    pass

  @abc.abstractmethod
  def get_channel_labels(self, channel: int) -> list[str]:
    """Returns the list of channel labels as an list of strings.

    Args:
        channel (int): The number of the channel
    """
    pass

  @abc.abstractmethod
  def set_vert_range(
      self,
      channel: int,
      channel_enable: bool,
      vertical_range: float,
      vertical_offset: float,
      probe_attenuation: int,
      vertical_coupling: instrument.ChannelCoupling,
  ) -> None:
    """a multiple channel setting functions.

    This is an all in one setting that combines a multiple channel setting
    functions into one. Keep note that this uses verticale range,not vertical
    division (total range across all division vs single division).

    Args:
        channel (int): Selects the Channel to Configure
        channel_enable (bool): Enable or Disable the Channel
        vertical_range (float):  The total viewable range
        vertical_offset (float):  Offset in volts from the center 0V point
        probe_attenuation (int): Sets the probe attenuation according to the
          scope probes
        vertical_coupling (instrument.ChannelCoupling): Vertical coupling
    """
    pass

  @abc.abstractmethod
  def config_edge_trigger(
      self,
      channel: int,
      level: float,
      edge: instrument.EdgeTriggerSlope,
      mode: instrument.EdgeTriggerCoupling,
  ) -> None:
    """Select a channel to use as trigger.

    Set Positive or Negative Trigger edge, set a trigger level in volts, and
    choose between (AC;DC;LF;HF) Trigger Coupling mode.

    Args:
        channel (int): The number of the channel
        level (float): Trigger level
        edge (instrument.EdgeTriggerSlope): The slope for an edge trigger
        mode (instrument.EdgeTriggerCoupling): Trigger mode
    """
    pass

  @abc.abstractmethod
  def set_aux_trigger(self, enable: bool) -> None:
    """Sets the front AUX connector as an output external trigger.

    This function is disabled by default.

    Args:
        enable (bool): Enable or Disable output external trigger
    """
    pass

  @abc.abstractmethod
  def config_continuous_acquisition(
      self, en_cont_acq: bool, en_auto_trig: bool
  ) -> None:
    """Configures the scope to set triggering mode to coninuous trigger.

    Configures the scope to set triggering mode to coninuous trigger, auto
    trigger, or both
    Continuous Acqusition: T, Auto Trig: T
    -> Auto trigger on and start acquisition, ignores trigger levels
    Continuous Acqusition: T, Auto Trig: F
    -> Normal trigger on most scopes, follows triggering levels and rules
    Continuous Acqusition: F, Auto Trig: T/F
    -> Single Trigger mode, ignores auto trig settings"

    Args:
        en_cont_acq (bool): Continuous Acqusition
        en_auto_trig (bool): Auto Trig
    """
    pass

  @abc.abstractmethod
  def config_rolling_mode(self, enable: bool) -> None:
    """Configures the acquisition to roll or not if function is supported.

    Args:
        enable (bool): enable or disable the rolling mode
    """
    pass

  @abc.abstractmethod
  def config_pulse_width_trigger(
      self,
      channel: int,
      mode: instrument.PulseTriggerMode,
      slope: instrument.PulseTriggerSlope,
      level: float,
      low_limit: float,
      hi_limit: float,
  ) -> None:
    """Sets a pulse width trigger for the selected channel.

    Use mode to selecte between: less than, greater than, In Range, Out of Range
    . When using less than, only hi_limit is valid and when using greater than,
    only low_limit is valid. Use level to set the trigger voltage level and
    slope to set positive or negative edge slope.

    Args:
        channel (int): The number of the channel
        mode (instrument.PulseTriggerMode): Trigger mode
        slope (instrument.PulseTriggerSlope): The slope for an edge trigger
        level (float): Trigger level
        low_limit (float): low limit
        hi_limit (float): high limit
    """
    pass

  @abc.abstractmethod
  def config_timeout_trigger(
      self,
      channel: int,
      polarity: instrument.TimeoutTrigPolarity,
      level: float,
      timeout: float,
  ) -> None:
    """Sets a timeout (dropout) trigger for the selected channel.

    Sets up a timeout trigger to wait for all defined conditions to be met to
    start acquisition(s).

    Args:
      channel (int): The channel source for the trigger
      polarity (instrument.TimeoutTrigPolarity): Wait for timeout to Stay High,
        Stay Low, or either
      level (float): The level threshold to trigger
      timeout (float): Timeout time in seconds

    Ex:
      config_timeout_trigger(channel=1, polarity='STAYLOW', level=1.5, time=0.1)
      This setups the trigger on channel 1, waits for the level to cross
      1.5 and the signal to stay low for 100mS before triggering
    """

  @abc.abstractmethod
  def set_horiz_division(
      self,
      hor_div: float,
      delay: float,
      sample_value: float,
      sample_type: instrument.HorizonType,
  ) -> None:
    """Sets the horizontal timing.

    Args:
        hor_div (float): Timebase Per Division
        delay (float): Horizontal delay in seconds. Negative shifts the waveform
          to the left, positive to the right
        sample_value (float): Sample Size or Sample Rate
        sample_type (instrument.HorizonType): Sample Size or SR priority/lock
    """
    pass

  @abc.abstractmethod
  def set_horiz_offset(self, hor_offset: float) -> None:
    """Summary.

    Args:
        hor_offset (float): Description
    """
    pass

  @abc.abstractmethod
  def set_measurement_reference(
      self,
      low: float,
      mid: float,
      high: float,
      mid2: float,
      reference_type: instrument.ReferenceType,
      reference_scope: instrument.ReferenceScope,
      meas_number: int | None,
  ) -> None:
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
    pass

  @abc.abstractmethod
  def set_measurement_on_off(
      self,
      meas_number: int,
      enable: bool,
  ) -> None:
    """Enabled or disable the selected measurement number for on screen display.

    Args:
        meas_number (int): measurement number
        enable (bool): enable or disable the Channel
    """
    pass

  @abc.abstractmethod
  def set_measurement_statistics(self, enable: bool) -> None:
    """Enable or disable measurement staticstics.

    Args:
        enable (bool):
    """
    pass

  @abc.abstractmethod
  def set_measurement(
      self,
      channel: int,
      meas_number: int,
      measurement_type: instrument.MeasurementType,
  ) -> None:
    """Sets the measurement type.

    Sets the measurement type based on Scope Measurement function, and channel
    source and assigns it to meas_number.

    Args:
        channel (int): The number of the channel
        meas_number (int): measurement number
        measurement_type (instrument.MeasurementType): measurement type
    """
    pass

  @abc.abstractmethod
  def set_delta_measurement(
      self,
      meas_number: int,
      channel1: int,
      channel2: int,
      start_edge: instrument.DeltSlope,
      end_edge: instrument.DeltSlope,
  ) -> None:
    """Set the measurement type called Delta or Delay measurement.

    This is used to compare the time between edges of 2 waveforms, channel1 and
    channel2, starting from Mid Reference to Mid2 Reference.

    Args:
        meas_number (int): Which measurement slot to assign Delta Measurement
        channel1 (int): The ""From"" Waveform
        channel2 (int): The ""To"" Waveform
        start_edge (instrument.DeltSlope): Select to use Rising or Falling edge
          for channel1
        end_edge (instrument.DeltSlope): Select to use Rising or Falling edge
          for channel2
    """
    pass

  @abc.abstractmethod
  def set_cursor(
      self,
      channel: int,
      cursor_type: instrument.CursorType,
      cur1_pos: float,
      cur2_pos: float,
  ) -> None:
    """Summary.

    Args:
        channel (int): The number of the channel
        cursor_type (instrument.CursorType): Cursor type
        cur1_pos (float): first position (second/voltage)
        cur2_pos (float): second position (second/voltage)
    """
    pass

  @abc.abstractmethod
  def set_infinite_persistence(self, enable: bool) -> None:
    """Enables or disables display infinite persistence.

    Args:
        enable (bool):
    """
    pass

  @abc.abstractmethod
  def clear_persistence(self) -> None:
    """Clears the screen of the overlaid persistence waveform."""
    pass

  @abc.abstractmethod
  def wait_acquisition_complete(self, timeout: float) -> None:
    """Checks scope register for waveform acquisition complete flag.

    This is a blocking function and will timeout based on the duration set in
    timeout(ms).

    Args:
        timeout (float): timeout
    """
    pass

  @abc.abstractmethod
  def get_acquisition(self):
    """Acquisition state."""
    pass

  @abc.abstractmethod
  def arm_single_trig(self):
    """Readies a single trigger.

    Readies a single trigger identified by and what was configured in
    config_edge_trigger or config_pulse_width_trigger.
    """
    pass

  @abc.abstractmethod
  def stop_acquisition(self) -> None:
    """Stops the scope acquisition system."""
    pass

  @abc.abstractmethod
  def start_acquisition(self) -> None:
    """Starts the scope acquisition system.

    This arms the trigger into whatever was configured by
    config_continuous_acquisition.
    """
    pass

  @abc.abstractmethod
  def reset_measurement_statistics(self) -> None:
    """Resets all the acquire statistical data."""
    pass

  @abc.abstractmethod
  def get_measurement_statistics(self, meas_number: int) -> dict[str, float]:
    """Reads out the currently acquired statistical data on the meas_number.

    Args:
        meas_number (float):
    """
    pass

  @abc.abstractmethod
  def wait_trigger_ready(self, timeout: float) -> None:
    """See if trigger is armed and ready.

    Check scope status during a given timeout (ms) to see if trigger is armed
    and ready.

    Args:
        timeout (float): timeout
    """
    pass

  @abc.abstractmethod
  def force_trigger(self) -> None:
    """Forces a trigger even if trigger condition has not been met.

    This forces a single acquisition on the scope if the trigger is ready,
    but the condition has not been met. If the trigger is in stopped mode, then
    the command is ignored.
    """
    pass

  @abc.abstractmethod
  def fetch_delta_measurement(
      self,
      channel1: int,
      channel2: int,
      start_edge: instrument.DeltSlope,
      end_edge: instrument.DeltSlope,
      mid: float,
      mid2: float,
  ):
    """Specificly used to read an immediate Delta or Delay measurement.

    This is used to compare the time between edges of 2 waveforms, Source 1 and
    Source 2, starting from Mid Reference to Mid2 Reference.

    Args:
        channel1 (int): The From Waveform.
        channel2 (int): The To Waveform.
        start_edge (instrument.DeltSlope): Select to use Rising or Falling edge
          for channel1.
        end_edge (instrument.DeltSlope): Select to use Rising or Falling edge
          for channel2.
        mid (float): The reference point of channel1 in percentages.
        mid2 (float): The reference point of channel2 in percentages.
    """
    pass

  @abc.abstractmethod
  def fetch_measurement(
      self,
      channel: int,
      measurement_type: instrument.MeasurementType,
  ):
    """Reads back the measurement of selected channel based on measurement type.

    Args:
        channel (int): The number of the channel
        measurement_type (instrument.MeasurementType): measurement type
    """
    pass

  @abc.abstractmethod
  def fetch_measure_number(self, measure_number: int):
    """Reads back the measurement of selected measure number.

    Args:
        measure_number (int): The number of the measure number
    """
    pass

  @abc.abstractmethod
  def fetch_waveform(self, channel: int):
    """Reads back waveform (samples + timing information) on a selected channel.

    Args:
        channel (int): The number of the channel
    """
    pass

  @abc.abstractmethod
  def set_search_edges_on_off(self, enable: bool):
    """Used to enable or disable a waveform edge search.

    Args:
      enable (bool): Turn on or off a waveform edge search
    """
    pass

  @abc.abstractmethod
  def set_search_edges(
      self,
      channel: int,
      edge: instrument.EdgeTriggerSlope,
      level: float,
  ):
    """Used to set up a waveform edge search.

    Args:
      channel (int): Channel to perform the search on
      edge (instrument.EdgeTriggerSlope): Select rising, falling, or both (if
        available)
      level (float): Level the threshold to qualify for search results
    """
    pass

  @abc.abstractmethod
  def get_search_edges(
      self,
      start_index: int = 0,
      count: int = -1,
  ) -> list[float]:
    """Used to retrieve an edge search result.

    Args:
      start_index (int): The starting index of the first result. Default is 0.
      count (int): Number of results to return. Default is -1 for all.

    Returns (list[float[): A list of floating point of x-axis time index. If
      index, size, or search parameters are invalid, returns an empty list.
    """

  @abc.abstractmethod
  def load_settings_file(self, path: str):
    """Load the settings file.

    Args:
        path (str): The path to load the setting file
    """
    pass

  @abc.abstractmethod
  def save_settings_file(self, path: str):
    """Save the settings file.

    Args:
        path (str): The path to store the setting file
    """
    pass

  @abc.abstractmethod
  def _get_screenshot(self, path: str) -> None:
    """Take Screenshot.

    Creates a scope screen (PNG format) at instrument.

    Args:
        path (str): Description
    """
    pass

  @abc.abstractmethod
  def save_screenshot(self, path: str):
    """Save Screenshot.

    Creates a local (on host PC) copy of the current scope screen (PNG format)
    at the given local computer's path.

    Args:
        path (str): Description
    """
    pass

  @abc.abstractmethod
  def auto_set(self) -> None:
    """This command automatically acquire and display the selected waveform."""
    pass

  @abc.abstractmethod
  def set_display_style(self, mode: instrument.LayoutStyle) -> None:
    """Set the waveform layout style used by the display.

    Args:
        mode (instrument.LayoutStyle): Layout style
    """
    pass

  @abc.abstractmethod
  def get_error_status(self):
    """Query the contents of the command error."""
    pass

  def start_ev_analysis(self) -> None:
    """Start EV analysis."""

  def stop_ev_analysis(self) -> None:
    """Stop EV analysis."""

  def get_ev_overview_report(self, report_csv_path: str | pathlib.Path) -> None:
    """Get EV overview report and save to csv file."""

  def get_ev_detail_report(self, report_csv_path: str | pathlib.Path) -> None:
    """Get EV detailed report and save to csv file."""

  def get_ev_decode_report(self, report_csv_path: str | pathlib.Path) -> None:
    """Get EV decoded data report and save to csv file."""

  def clear_ev_report(self) -> None:
    """Clear previous EV analysis report."""

  def query_ev_report_count(self) -> int:
    """Browse available EV report count."""
    raise NotImplementedError('Not yet implemented')
