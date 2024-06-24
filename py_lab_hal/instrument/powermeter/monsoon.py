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

"""PyLabHal Monsoon power monitor class.

Supported Models: FTA22J: Low voltage Power Monitor. AAA10F: high voltage power
monitor.
"""

# pytype: skip-file

from __future__ import annotations

import dataclasses
import itertools
import json
import logging
import pathlib

from Monsoon import sampleEngine
from py_lab_hal.cominterface import cominterface
from py_lab_hal.instrument import instrument
from py_lab_hal.instrument.powermeter import powermeter as pm
from py_lab_hal.util import util

DEFAULT_SAMPLES = sampleEngine.triggers.SAMPLECOUNT_INFINITE


@dataclasses.dataclass
class MonsoonMeasurements(pm.PowerMeasurements):
  """Class to hold monsoon power monitor measurement results."""

  timestamp: float
  main_current: float
  usb_current: float
  aux_current: float
  main_volts: float
  usb_volts: float


class MonsoonUsbPassThrough(util.PyLabHalEnum):
  """Values for setting or retrieving the USB Passthrough mode."""

  off = 0
  on = 1
  auto = 2


class Monsoon(pm.PowerMeter):

  def __init__(
      self,
      com: cominterface.ComInterfaceClass,
      inst_config: instrument.InstrumentConfig,
  ) -> None:
    super().__init__(com, inst_config)
    self.engine = com.engine
    self.monitor = com.monitor
    self.is_sampling = False
    self.measurement_cfg: pm.MeasurementTriggerConfig
    self.measurement_json = None

  def initialize(self, enable_main=False, enable_usb=False, enable_aux=False):
    """initialize Monsoon power sources."""
    if enable_main:
      self.engine.enableChannel(sampleEngine.channels.MainCurrent)
      self.engine.enableChannel(sampleEngine.channels.MainVoltage)
    if enable_usb:
      self.engine.enableChannel(sampleEngine.channels.USBCurrent)
      self.engine.enableChannel(sampleEngine.channels.USBVoltage)
    if enable_aux:
      self.engine.enableChannel(sampleEngine.channels.AuxCurrent)
    try:
      self.monitor.fillStatusPacket()
    except AttributeError:
      raise RuntimeError('Monsoon not connected properly')

  def set_output_voltage(self, voltage: float):
    """Sets given output voltage.

    Source channel is chosen at initialize stage.
    """
    self.monitor.setVout(voltage)

  def set_runtime_current_limit(self, current: float):
    self.monitor.setRunTimeCurrentLimit(current)

  def set_powerup_current_limit(self, current: float):
    self.monitor.setPowerUpCurrentLimit(current)

  def start_sampling(self, measurement_cfg: pm.MeasurementTriggerConfig):
    self._set_measurement_trigger(measurement_cfg)
    if measurement_cfg.samplingMode == pm.SamplingMode.oneShot:
      self.engine.startSampling(measurement_cfg.numSamples)
    else:
      self.engine.periodicStartSampling()
    self.is_sampling = True

  def _set_measurement_trigger(
      self, measurement_cfg: pm.MeasurementTriggerConfig
  ):
    self.measurement_cfg = measurement_cfg
    if measurement_cfg.startTrigger:
      self.engine.setStartTrigger(*measurement_cfg.startTrigger)
      self.engine.setTriggerChannel(measurement_cfg.triggerChannel)
    if measurement_cfg.stopTrigger:
      self.engine.setStopTrigger(*measurement_cfg.stopTrigger)
    self.engine.ConsoleOutput(measurement_cfg.enableConsoleOut)

  @staticmethod
  def _parse_measurements(measurement_list):
    result_list = []
    for measurement in itertools.zip_longest(*measurement_list, fillvalue=''):
      result_list.append(MonsoonMeasurements(*measurement))

    return result_list

  def get_measurements(
      self, trigger_config: pm.MeasurementTriggerConfig
  ) -> list[MonsoonMeasurements]:
    if trigger_config.samplingMode == pm.SamplingMode.oneShot:
      samples = self.engine.getSamples()
    else:
      samples = self.engine.periodicCollectSamples(trigger_config.numSamples)
    if self.measurement_json:
      self._save_measurement_json(samples)
    return self._parse_measurements(samples)

  def _save_measurement_json(self, samples):
    fields = [f.name for f in dataclasses.fields(MonsoonMeasurements)]
    with open(self.measurement_json, 'w') as json_file:
      json.dump(dict(zip(fields, samples)), json_file)

  def measure_current(self) -> list[MonsoonMeasurements]:
    if not self.is_sampling:
      self.start_sampling(pm.MeasurementTriggerConfig(numSamples=1))
    return self.get_measurements(self.measurement_cfg)

  def set_csv_output(self, csv_file: str | pathlib.Path):
    self.engine.enableCSVOutput(csv_file)

  def set_json_output(self, json_file: str | pathlib.Path, enable=True):
    """Enable measurement dump as json and sets json file path.

    Args:
        json_file (str): json file path to dump measurements data.
        enable (bool): Json dump enable/disable.
    """
    if enable:
      self.measurement_json = json_file

  def stop_sampling(self, trigger_config: pm.MeasurementTriggerConfig):
    if self.is_sampling:
      if trigger_config.samplingMode == pm.SamplingMode.periodic:
        self.engine.periodicStopSampling(closeCSV=True)
    else:
      logging.warning('Sampling not started, doing nothing')
    self.is_sampling = False

  def set_usb_passthrough_mode(self, usb_passthrough: MonsoonUsbPassThrough):
    """Sets the USB passthrough mode to On/Off/Auto."""

    return self.monitor.setUSBPassthroughMode(usb_passthrough.value)
