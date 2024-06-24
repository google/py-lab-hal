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

"""This file contains all the instrument classes."""

from __future__ import annotations

import re
from typing import Optional, overload

from py_lab_hal.cominterface import cominterface
from py_lab_hal.instrument import instrument
from py_lab_hal.instrument.arm import arm
from py_lab_hal.instrument.battery_emulator import battery_emulator
from py_lab_hal.instrument.dcpsu import dcpsu
from py_lab_hal.instrument.dmm import dmm
from py_lab_hal.instrument.eload import eload
from py_lab_hal.instrument.function_generator import function_generator
from py_lab_hal.instrument.light import light
from py_lab_hal.instrument.powermeter import powermeter
from py_lab_hal.instrument.relay import relay
from py_lab_hal.instrument.remote_power_switch import remote_power_switch
from py_lab_hal.instrument.scope import scope
from py_lab_hal.instrument.smu import smu
from py_lab_hal.instrument.spectro_radio_meter import spectro_radio_meter
from py_lab_hal.instrument.stepper_motor import stepper_motor
from py_lab_hal.instrument.temp_chamber import temp_chamber
from py_lab_hal.util import util


class Arm(str, util.PyLabHalEnum):
  ARCH = 'arm.arch.Arch'
  DEXARM = 'arm.dexarm.Dexarm'


class BatteryEmulator(str, util.PyLabHalEnum):
  KEYSIGHT_66311B = 'battery_emulator.keysight_663xxx.Keysight66300Series'
  KEYSIGHT_66321B = 'battery_emulator.keysight_663xxx.Keysight66300Series'
  KEYSIGHT_66321D = 'battery_emulator.keysight_663xxx.Keysight66300Series'
  KEYSIGHT_66332A = 'battery_emulator.keysight_663xxx.Keysight66300Series'
  KEYSIGHT_66309B = 'battery_emulator.keysight_663xxx.Keysight66300Series'
  KEYSIGHT_66309D = 'battery_emulator.keysight_663xxx.Keysight66300Series'
  KEYSIGHT_66319B = 'battery_emulator.keysight_663xxx.Keysight66300Series'
  KEYSIGHT_66319D = 'battery_emulator.keysight_663xxx.Keysight66300Series'
  KEYSIGHT_N6705C = 'battery_emulator.keysight_n6705c.KeysightN6705c'


class DCPowerSupply(str, util.PyLabHalEnum):
  AIMTTICPX_4000DP = 'dcpsu.aimtticpx_4000dp.Aimtticpx4000dp'
  GWIN_PST3202 = 'dcpsu.gwin_pst3202.GwinPst3202'
  KEYSIGHT_E36311A = 'dcpsu.keysight_e36300_series.KeysightE36300Series'
  KEYSIGHT_E36312A = 'dcpsu.keysight_e36300_series.KeysightE36300Series'
  KEYSIGHT_E36313A = 'dcpsu.keysight_e36300_series.KeysightE36300Series'
  KEYSIGHT_E3632A = 'dcpsu.keysight_e3630_series.KeysightE3630Series'
  KEYSIGHT_E3633A = 'dcpsu.keysight_e3630_series.KeysightE3630Series'
  KEYSIGHT_E3634A = 'dcpsu.keysight_e3630_series.KeysightE3630Series'
  KEYSIGHT_N6705C = 'dcpsu.keysight_n6705c.KeysightN6705c'
  CPX_400D = 'dcpsu.cpx_400d.Cpx400d'


class DMM(str, util.PyLabHalEnum):
  AGILENT_34410A = 'dmm.agilent_34410a.Agilent34410a'
  KEYSIGHT_34970A = 'dmm.keysight_34970a.Keysight34970a'
  AGILENT_34465A = 'dmm.agilent_34465a.Agilent34465a'


class Eload(str, util.PyLabHalEnum):
  BK_8500B = 'eload.bk_8500b.Bk8500b'
  CHROMA_63600 = 'eload.chroma_63600.Chroma63600'
  CHROMA_63601 = 'eload.chroma_63600.Chroma63600'
  CHROMA_63610 = 'eload.chroma_63600.Chroma63600'
  CHROMA_63630 = 'eload.chroma_63600.Chroma63600'
  CHROMA_63640 = 'eload.chroma_63600.Chroma63600'
  KEYSIGHT_N6705C = 'eload.keysight_n6705c.KeysightN6705c'
  PLZ_205W = 'eload.plz_205w.Plz205w'
  PLZ_405W = 'eload.plz_205w.Plz205w'
  PLZ_1205W = 'eload.plz_205w.Plz205w'


class FunctionGenerator(str, util.PyLabHalEnum):
  KEYSIGHT_N33500B = 'function_generator.keysight_n33500b.KeysightN33500b'


class Light(str, util.PyLabHalEnum):
  ARRI_S120 = 'light.arri_s120.ArriS120'


class PowerMeter(str, util.PyLabHalEnum):
  MONSOON_LV = 'powermeter.monsoon.Monsoon'
  MONSOON_HV = 'powermeter.monsoon.Monsoon'


class Relay(str, util.PyLabHalEnum):
  TIGERTAIL = 'relay.tigertail.Tigertail'
  USBRELAY = 'relay.usbrelay.Usbrelay'


class RemotePowerSwitch(str, util.PyLabHalEnum):
  WEBPOWERSWITCH = 'remote_power_switch.web_power_switch.WebPowerSwitch'
  DIGIPDU_ZDHX = 'remote_power_switch.digipdu_zdhx.DigipduZdhx'


class Scope(str, util.PyLabHalEnum):
  LECROY_MAUI = 'scope.lecroy_maui.LecroyMAUI'
  KEYSIGHT_4000X_SERIES = 'scope.keysight_4000x_series.Keysight4000xSeries'
  KEYSIGHT_S_SERIES = 'scope.keysight_s_series.KeysightSSeries'
  TEKTRONIX_MSO = 'scope.tektronix_mso.TektronixMSO'
  ACUTE_MSO_3000X = 'scope.acute_mso3000x.AcuteMso3000x'


class SMU(str, util.PyLabHalEnum):
  KEYSIGHT_N6705C = 'smu.keysight_n6705c.KeysightN6705c'


class SpectroRadioMeter(str, util.PyLabHalEnum):
  JADAK_PR670 = 'spectro_radio_meter.jadak_pr670.JadakPr670'
  KONICA_CS3000 = 'spectro_radio_meter.konica_cs3000.KonicaCs3000'
  KONICA_CS2000 = 'spectro_radio_meter.konica_cs3000.KonicaCs3000'


class StepperMotor(str, util.PyLabHalEnum):
  THORLABS_HDR50 = 'stepper_motor.thorlabs_hdr50.ThorlabsHdr50'


class TempChamber(str, util.PyLabHalEnum):
  PU3J = 'temp_chamber.pu3j.Pu3j'
  TESTEQUITY_107 = 'temp_chamber.testequity_107.Testequity107'
  GIANT = 'temp_chamber.giant.Giant'


def extract_instrument_name(instrument_model: str) -> re.Match[str]:
  result = re.search(
      r'(?P<categories>[a-zA-z0-9_]+).(?P<module>[a-zA-z0-9_]+)(.(?P<class_name>[a-zA-z0-9_]+))?',
      instrument_model,
  )
  if not result:
    raise RuntimeError(
        f'The instrument model: {instrument_model} is not supported.'
    )

  return result


class _InstrumentEnum(util.PyLabHalEnum):
  """This is the enum for the instrument categories."""

  ARM = Arm
  BATTERY_EMULATOR = BatteryEmulator
  DCPSU = DCPowerSupply
  DMM = DMM
  ELOAD = Eload
  FUNCTION_GEN = FunctionGenerator
  LIGHT = Light
  POWERMETER = PowerMeter
  RELAY = Relay
  REMOTE_POWER_SWITCH = RemotePowerSwitch
  SCOPE = Scope
  SMU = SMU
  SPECTRO_RADIO_METER = SpectroRadioMeter
  STEPPER_MOTOR = StepperMotor
  TEMP_CHAMBER = TempChamber

  @classmethod
  def get_inst(cls, attr):
    instrument_info = extract_instrument_name(attr)
    categories_enum = cls.get(instrument_info['categories']).value
    return categories_enum.get(instrument_info['module'])


class PyLabHALBuilder:
  """This is the builder for py_lab_hal."""

  def __init__(self):
    self.connection_config: cominterface.ConnectConfig | None = None
    self.instrument_config: instrument.InstrumentConfig = (
        instrument.InstrumentConfig()
    )
    self.cominterface: Optional[cominterface.ComInterfaceClass] = None

  @overload
  def build_instrument(self, instrument_model: Arm) -> arm.Arm:
    ...

  @overload
  def build_instrument(
      self, instrument_model: BatteryEmulator
  ) -> battery_emulator.BatteryEmulator:
    ...

  @overload
  def build_instrument(self, instrument_model: DCPowerSupply) -> dcpsu.DCpsu:
    ...

  @overload
  def build_instrument(self, instrument_model: DMM) -> dmm.DMM:
    ...

  @overload
  def build_instrument(self, instrument_model: Eload) -> eload.Eload:
    ...

  @overload
  def build_instrument(
      self, instrument_model: FunctionGenerator
  ) -> function_generator.FunctionGenerator:
    ...

  @overload
  def build_instrument(self, instrument_model: Light) -> light.Light:
    ...

  @overload
  def build_instrument(
      self, instrument_model: PowerMeter
  ) -> powermeter.PowerMeter:
    ...

  @overload
  def build_instrument(self, instrument_model: Relay) -> relay.Relay:
    ...

  @overload
  def build_instrument(
      self, instrument_model: RemotePowerSwitch
  ) -> remote_power_switch.RemotePowerSwitch:
    ...

  @overload
  def build_instrument(self, instrument_model: Scope) -> scope.Scope:
    ...

  @overload
  def build_instrument(self, instrument_model: SMU) -> smu.Smu:
    ...

  @overload
  def build_instrument(
      self, instrument_model: SpectroRadioMeter
  ) -> spectro_radio_meter.SpectroRadioMeter:
    ...

  @overload
  def build_instrument(
      self, instrument_model: StepperMotor
  ) -> stepper_motor.StepperMotor:
    ...

  @overload
  def build_instrument(
      self, instrument_model: TempChamber
  ) -> temp_chamber.TempChamber:
    ...

  @overload
  def build_instrument(self, instrument_model: str):
    ...

  def build_instrument(self, instrument_model):
    """This is the function to build the instrument.

    Args:
          instrument_model: The instrument model.

    Raises:
        RuntimeError: Didn't set the connection_config or instrument_model is
        not supported.

    Returns:
          The instrument object.
    """

    if isinstance(instrument_model, util.PyLabHalEnum):
      instrument_info = extract_instrument_name(instrument_model.value)
    elif isinstance(instrument_model, str):
      instrument_info = extract_instrument_name(
          _InstrumentEnum.get_inst(instrument_model)
      )
    else:
      raise RuntimeError(
          f'The type of the instrument_model: {type(instrument_model)} is not'
          ' supported.',
      )

    if self.cominterface is None:
      if self.connection_config is None:
        raise RuntimeError(
            'Please add the connection config to the builder first.'
        )

      self.cominterface = cominterface.select(self.connection_config)

    built_instrument = instrument.select(
        instrument_info.group('categories'),
        instrument_info.group('module'),
        instrument_info.group('class_name'),
        self.cominterface,
        self.instrument_config,
    )
    self.cominterface = None

    return built_instrument


if __name__ == '__main__':
  pylabhal_builder = PyLabHALBuilder()
  pylabhal_builder.connection_config = cominterface.ConnectConfig(
      network=cominterface.NetworkConfig(host='127.0.0.1', port=5025),
      # serial_config=cominterface.SerialConfig(baud_rate=115200),
  )
  pylabhal_builder.instrument_config = instrument.InstrumentConfig(
      auto_init=True
  )

  # pylabhal_builder.cc = cominterface.ConnectConfig.from_json('')

  inst = pylabhal_builder.build_instrument(Relay.USBRELAY)
  # inst = pylabhal_builder.build_instrument('relay.usbrelay')

  print(type(inst))
  # inst.
  try:
    inst.enable(1, False)
    inst.enable(1, True)
  finally:
    inst.close()
