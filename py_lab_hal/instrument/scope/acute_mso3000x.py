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
"""Scope implementation for Acute MSO 3000x models."""

import collections
import pathlib

from py_lab_hal.cominterface import cominterface
from py_lab_hal.instrument import instrument
from py_lab_hal.instrument.scope import scope


class AcuteMso3000x(scope.Scope):
  """Child Scope Class of model."""

  def __init__(
      self,
      com: cominterface.ComInterfaceClass,
      inst_config: instrument.InstrumentConfig,
  ) -> None:
    super().__init__(com, inst_config)
    self.measurement_item: collections.OrderedDict[
        int, scope.Scope.MeasurementConfig
    ]

  def enable_ev(self):
    """Enable Electrical Validation mode on acute DSO."""

  def start_ev_analysis(self):
    """Start EV analysis."""
    self.data_handler.query('EV:ANALYSIS')

  def stop_ev_analysis(self):
    """Stop EV analysis."""
    self.data_handler.query('EV:STOP')

  def get_ev_overview_report(self, report_csv_path: str | pathlib.Path):
    """Get EV overview report and save to csv file."""
    self.data_handler.query(f'EV:OVERVIEWREPORT:EXPORT {report_csv_path}')

  def get_ev_detail_report(self, report_csv_path: str | pathlib.Path):
    """Get EV detailed report and save to csv file."""
    self.data_handler.query(f'EV:DETAILREPORT:EXPORT {report_csv_path}')

  def get_ev_decode_report(self, report_csv_path: str | pathlib.Path):
    """Get EV decoded data report and save to csv file."""
    self.data_handler.query(f'EV:DECODEREPORT:EXPORT {report_csv_path}')

  def clear_ev_report(self):
    """Clear previous EV analysis report."""
    self.data_handler.query('EV:CLEAR')

  def query_ev_report_count(self) -> int:
    """Browse available EV report count.

    Returns:
      int: Number of available EV reports. 0 if not reports available.
    """
    return int(self.data_handler.query('EV:BROWSECOUNT?'))

  def measure(self):
    raise NotImplementedError('Not Yet Implemented')

  def set_channel_position(self, channel: int, position: float) -> None:
    raise NotImplementedError('Not Yet Implemented')

  def set_channel_attenuation(
      self, channel: int, attenuation_factor: int
  ) -> None:
    raise NotImplementedError('Not Yet Implemented')

  def set_channel_coupling(
      self, channel: int, mode: str, impedance: int
  ) -> None:
    raise NotImplementedError('Not Yet Implemented')

  def set_channel_offset(self, channel: int, voffset: float) -> None:
    raise NotImplementedError('Not Yet Implemented')

  def set_channel_division(self, channel: int, vdiv: float) -> None:
    raise NotImplementedError('Not Yet Implemented')

  def set_channel_on_off(self, channel: int, enable: bool) -> None:
    raise NotImplementedError('Not Yet Implemented')

  def set_channel_bandwidth(
      self, channel: int, value: float, enable: bool
  ) -> None:
    raise NotImplementedError('Not Yet Implemented')

  def set_channel_labels(self, channel: int, value: str) -> None:
    raise NotImplementedError('Not Yet Implemented')

  def set_channel_labels_position(
      self, channel: int, x: float, y: float
  ) -> None:
    raise NotImplementedError('Not Yet Implemented')

  def get_channel_labels(self, channel: int) -> list[str]:
    raise NotImplementedError('Not Yet Implemented')

  def set_vert_range(
      self,
      channel: int,
      channel_enable: bool,
      vertical_range: float,
      vertical_offset: float,
      probe_attenuation: int,
      vertical_coupling: str,
  ) -> None:
    raise NotImplementedError('Not Yet Implemented')

  def config_edge_trigger(
      self, channel: int, level: float, edge: str, mode: str
  ) -> None:
    raise NotImplementedError('Not Yet Implemented')

  def set_aux_trigger(self, enable: bool) -> None:
    raise NotImplementedError('Not Yet Implemented')

  def config_continuous_acquisition(
      self, en_cont_acq: bool, en_auto_trig: bool
  ) -> None:
    raise NotImplementedError('Not Yet Implemented')

  def config_rolling_mode(self, enable: bool) -> None:
    raise NotImplementedError('Not Yet Implemented')

  def config_pulse_width_trigger(
      self,
      channel: int,
      mode: str,
      slope: str,
      level: float,
      low_limit: float,
      hi_limit: float,
  ) -> None:
    raise NotImplementedError('Not Yet Implemented')

  def config_timeout_trigger(
      self, channel: int, polarity: str, level: float, timeout: float
  ) -> None:
    raise NotImplementedError('Not Yet Implemented')

  def set_horiz_division(
      self, hor_div: float, delay: float, sample_value: float, sample_type: str
  ) -> None:
    raise NotImplementedError('Not Yet Implemented')

  def set_horiz_offset(self, hor_offset: float) -> None:
    raise NotImplementedError('Not Yet Implemented')

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
    raise NotImplementedError('Not Yet Implemented')

  def set_measurement_on_off(self, meas_number: int, enable: bool) -> None:
    raise NotImplementedError('Not Yet Implemented')

  def set_measurement_statistics(self, enable: bool) -> None:
    raise NotImplementedError('Not Yet Implemented')

  def set_measurement(
      self, channel: int, meas_number: int, measurement_type: str
  ) -> None:
    raise NotImplementedError('Not Yet Implemented')

  def set_delta_measurement(
      self,
      meas_number: int,
      channel1: int,
      channel2: int,
      start_edge: str,
      end_edge: str,
  ) -> None:
    raise NotImplementedError('Not Yet Implemented')

  def set_cursor(
      self, channel: int, cursor_type: str, cur1_pos: float, cur2_pos: float
  ) -> None:
    raise NotImplementedError('Not Yet Implemented')

  def set_infinite_persistence(self, enable: bool) -> None:
    raise NotImplementedError('Not Yet Implemented')

  def clear_persistence(self) -> None:
    raise NotImplementedError('Not Yet Implemented')

  def wait_acquisition_complete(self, timeout: float) -> None:
    raise NotImplementedError('Not Yet Implemented')

  def get_acquisition(self):
    raise NotImplementedError('Not Yet Implemented')

  def arm_single_trig(self):
    raise NotImplementedError('Not Yet Implemented')

  def stop_acquisition(self) -> None:
    raise NotImplementedError('Not Yet Implemented')

  def start_acquisition(self) -> None:
    raise NotImplementedError('Not Yet Implemented')

  def reset_measurement_statistics(self) -> None:
    raise NotImplementedError('Not Yet Implemented')

  def get_measurement_statistics(self, meas_number: int) -> dict[str, float]:
    raise NotImplementedError('Not Yet Implemented')

  def wait_trigger_ready(self, timeout: float) -> None:
    raise NotImplementedError('Not Yet Implemented')

  def force_trigger(self) -> None:
    raise NotImplementedError('Not Yet Implemented')

  def fetch_delta_measurement(
      self,
      channel1: int,
      channel2: int,
      start_edge: str,
      end_edge: str,
      mid: float,
      mid2: float,
  ):
    raise NotImplementedError('Not Yet Implemented')

  def fetch_measurement(self, channel: int, measurement_type: str):
    raise NotImplementedError('Not Yet Implemented')

  def fetch_measure_number(self, measure_number: int):
    raise NotImplementedError('Not Yet Implemented')

  def fetch_waveform(self, channel: int):
    raise NotImplementedError('Not Yet Implemented')

  def set_search_edges_on_off(self, enable: bool):
    raise NotImplementedError('Not Yet Implemented')

  def set_search_edges(self, channel: int, edge: str, level: float):
    raise NotImplementedError('Not Yet Implemented')

  def get_search_edges(
      self, start_index: int = 0, count: int = -1
  ) -> list[float]:
    raise NotImplementedError('Not Yet Implemented')

  def load_settings_file(self, path: str):
    raise NotImplementedError('Not Yet Implemented')

  def save_settings_file(self, path: str):
    raise NotImplementedError('Not Yet Implemented')

  def _get_screenshot(self, path: str) -> None:
    raise NotImplementedError('Not Yet Implemented')

  def save_screenshot(self, path: str):
    raise NotImplementedError('Not Yet Implemented')

  def auto_set(self) -> None:
    raise NotImplementedError('Not Yet Implemented')

  def set_display_style(self, mode: str) -> None:
    raise NotImplementedError('Not Yet Implemented')

  def get_error_status(self):
    raise NotImplementedError('Not Yet Implemented')
