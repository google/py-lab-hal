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

"""Parent abstract class for instrument."""

import dataclasses
import enum
import importlib
import logging
import time
from py_lab_hal.cominterface import cominterface
from py_lab_hal.util import json_dataclass
from py_lab_hal.util import util


class MeasurementType(str, util.InstrumentEnum):
  """Measurement type."""

  RISETIME = enum.auto()
  FALLTIME = enum.auto()
  FREQUENCY = enum.auto()
  PERIOD = enum.auto()
  AMPLITUDE = enum.auto()
  RMS = enum.auto()
  MAX = enum.auto()
  MIN = enum.auto()
  HIGH = enum.auto()
  LOW = enum.auto()
  PEAKTOPEAK = enum.auto()
  AVERAGE = enum.auto()
  PULSEWIDTHPOSITIVE = enum.auto()
  PULSEWIDTHNEGATIVE = enum.auto()
  DUTYCYCLEPOSITIVE = enum.auto()
  DUTYCYCLENEGATIVE = enum.auto()
  OVERSHOOT = enum.auto()
  UNDERSHOOT = enum.auto()
  AREA = enum.auto()
  RISINGEDGECOUNT = enum.auto()
  FALLINGEDGECOUNT = enum.auto()


class ChannelCoupling(str, util.InstrumentEnum):
  AC = enum.auto()
  DC = enum.auto()
  DCREJECT = enum.auto()
  GROUND = enum.auto()


class EdgeTriggerCoupling(str, util.InstrumentEnum):
  AC = enum.auto()
  DC = enum.auto()
  DCREJECT = enum.auto()
  LFREJECT = enum.auto()
  NOISEREJECT = enum.auto()
  HFREJECT = enum.auto()


class EdgeTriggerSlope(str, util.InstrumentEnum):
  RISE = enum.auto()
  FALL = enum.auto()
  EITHER = enum.auto()


class EdgeTriggerMode(str, util.InstrumentEnum):
  AUTO = enum.auto()
  NORM = enum.auto()


class PulseTriggerMode(str, util.InstrumentEnum):
  LESS = enum.auto()
  MORE = enum.auto()
  WITHIN = enum.auto()
  OUT = enum.auto()


class PulseTriggerSlope(str, util.InstrumentEnum):
  NEG = enum.auto()
  POS = enum.auto()


class CursorType(str, util.InstrumentEnum):
  OFF = enum.auto()
  VER = enum.auto()
  HOR = enum.auto()


class HorizonType(str, util.InstrumentEnum):
  SAMPLESIZE = enum.auto()
  SAMPLERATE = enum.auto()


class ReferenceType(str, util.InstrumentEnum):
  PER = enum.auto()
  ABS = enum.auto()


class ReferenceScope(str, util.InstrumentEnum):
  GLOBAL = enum.auto()
  LOCAL = enum.auto()


class TimeoutTrigPolarity(str, util.InstrumentEnum):
  STAYHIGH = enum.auto()
  STAYLOW = enum.auto()
  EITHER = enum.auto()


class DeltSlope(str, util.InstrumentEnum):
  RISE = enum.auto()
  FALL = enum.auto()
  EITHER = enum.auto()


class LayoutStyle(str, util.InstrumentEnum):
  OVERLAY = enum.auto()
  STACK = enum.auto()


class StandardEventStatusRegisterMask(enum.IntEnum):
  """Standard Event Status Register Mask for the instrument support IEEE 488.2."""

  OPC = 0x01
  """0 = Operation is not complete. 1 = operation is complete."""
  QRC = 0x02
  """0 = request control - NOT used always 0."""
  QYE = 0x04
  """0 = No query errors. 1 = A query error has been detected."""
  DDE = 0x08
  """0 = No device-dependent errors. 1 = A device-dependent error has been detected."""
  EXE = 0x10
  """0 = no execution error. 1 = an execution error has been detected."""
  CME = 0x20
  """0 = no command errors. 1 = a command error has been detected."""
  PON = 0x80
  """1 = OFF to ON transition has occurred."""
  ALL = OPC | QRC | QYE | DDE | EXE | CME | PON


class SmuEmulationMode(str, util.InstrumentEnum):
  """The Emulation Mode for different module in Keysight N6705C."""

  PS4Q = enum.auto()
  """4-Quadrant Power Supply.

  4-quadrant operation is only available on Keysight N6784A.
  Operation is allowed in all four output quadrants.
  """
  PS2Q = enum.auto()
  """2-Quadrant Power Supply.

  This operating mode is restricted to two quadrants (+V/+I and +V/-I).
  """
  PS1Q = enum.auto()
  """1-Quadrant Power Supply (unipolar).

  This mode emulates a typical one quadrant or unipolar power supply with limited down-programming.
  """
  BATTERY = enum.auto()
  """Battery Emulator.

  A battery emulator imitates a battery's charging and discharging functions.
  """
  CHARGER = enum.auto()
  """Battery Charger

  A battery charger imitates a battery charger; it cannot sink current like a battery.
  """
  CCLOAD = enum.auto()
  """CC Load.

  The CC Load emulates a constant-current load.
  """
  CVLOAD = enum.auto()
  """CV Load.

  The CV Load emulates a constant-voltage load.
  """
  VMETER = enum.auto()
  """Voltage measurement.

  The voltage measurement emulates a voltmeter.
  """
  AMETER = enum.auto()
  """Current measurement.

  The current measurement emulates a zero-burden ammeter.
  """


class ChannelMode(str, util.InstrumentEnum):
  VOLTAGE_DC = enum.auto()
  VOLTAGE_AC = enum.auto()
  CURRENT_DC = enum.auto()
  CURRENT_AC = enum.auto()
  RESISTANCE = enum.auto()
  RESISTANCE_4WIRE = enum.auto()
  CAPACITANCE = enum.auto()
  TEMPERATURE = enum.auto()
  FREQUENCY = enum.auto()
  POWER = enum.auto()


class TemperatureTransducer(str, util.InstrumentEnum):
  RTD = enum.auto()
  RTD_4WIRE = enum.auto()
  THERMISTOR = enum.auto()
  THERMISTOR_4WIRE = enum.auto()
  THERMO_COUPLE = enum.auto()


class ThermoCouple(str, util.InstrumentEnum):
  E = enum.auto()
  J = enum.auto()
  K = enum.auto()
  N = enum.auto()
  R = enum.auto()
  T = enum.auto()


class ValueRange(str, util.InstrumentEnum):
  MIN = enum.auto()
  MAX = enum.auto()
  DEFFULT = enum.auto()


@dataclasses.dataclass
class InstrumentConfig(json_dataclass.DataClassJsonCamelMixIn):
  """The config for instrument.

  Attributes:
      reset (bool): If it's true, the program will send *RTS
      clear (bool): If it's true, the program will send *CLS
      idn (bool): If it's true, the program will query *IDN?
      auto_init (bool): If it's true, the program will auto inti
  """

  reset: bool = True
  clear: bool = True
  idn: bool = True
  auto_init: bool = True
  channel: int = 1


class Instrument:
  """Parent abstract class for instrument."""

  def __init__(
      self,
      com: cominterface.ComInterfaceClass,
      inst_config: InstrumentConfig,
  ) -> None:
    """The constructor for the class.

    This function will auto select the right instrument model for
    user base on the input information.

    Args:
        com (ComInterfaceClass): The cominterface for the instrument
        inst_config (InstrumentConfig): The config for instrument
    """

    self.inst = com
    self.data_handler = cominterface.DataHandler(self.inst)
    self.inst_config = inst_config

    if self.inst_config.auto_init:
      self.open_instrument()

  def __del__(self) -> None:
    """Close the instrument when deleting the object."""
    self.close()

  def open_instrument(self):
    """Open the instrument and open the interface if needed."""
    if not self.inst.enable:
      self.open_interface()

    logging.info('Opening Instrument')

    if self.inst_config.reset:
      self.reset()
    if self.inst_config.clear:
      self.clear()
    if self.inst_config.idn:
      self.ask_idn()

    logging.debug('Instrument Opened')

  def open_interface(self):
    logging.info('Instrument Opening Interface')
    self.inst.open()

  def self_test(self) -> None:
    """Send to self test command to the instrument."""
    logging.debug('Doing the self testing')
    self.data_handler.send('*TST?')
    time.sleep(10)
    error_code = int(self.data_handler.recv())
    if error_code != 0:
      logging.error('Error Found with Error Code: %d', error_code)
      return
    logging.debug('Self testing completed, No Error Found')

  def clear(self) -> None:
    """Clear Status Command.

    Clears the event registers in all register groups. Also clears the error
    queue.
    """
    self.data_handler.send('*CLS')

  def close(self) -> None:
    """Call the close command of cominterface."""
    self.inst.close()

  def reset(self) -> None:
    """Resets instrument to factory default state."""
    self.data_handler.send('*RST')

  def ask_idn(self) -> None:
    """Identification Query.

    Returns the instrument's identification string.
    """
    self.idn = self.data_handler.query('*IDN?')
    logging.info('Instrument IDN Received %s', self.idn)

  def wait_task(self, timeout: float = 30):
    """Waits for all pending OPC operations are finished.

    This is a blocking function and will timeout based on the duration set in
    timeout (seconds).

    Args:
        timeout (float): The timeout value in seconds.

    Raises:
        RuntimeError: If the timeout is reached.
    """
    time_now = time.time()
    while self.data_handler.query('*OPC?') != '1':
      logging.info('Wait for all pending OPC operations are finished.')
      time.sleep(1)
      if time.time() - time_now > timeout:
        raise RuntimeError('Timeout')

  def event_status_register(
      self,
      mask: StandardEventStatusRegisterMask = StandardEventStatusRegisterMask.ALL,
  ) -> int:
    """Event Status Register for the instrument support IEEE 488.2.

    Send the '*ERS?' to the instrument and return the current value of the Event
    Status Register.

    Args:
        mask (StandardEventStatusRegisterMask): The mask to apply to the
          returned value.

    Returns:
        int: The current value of the Event Status Register.
    """
    esr = int(self.data_handler.query('*ESR?'))
    logging.debug('Standard Event Status Register: %d with maks %d', esr, mask)
    return esr & mask


def select(
    instrument_type: str,
    module_name: str,
    class_name: str,
    com: cominterface.ComInterfaceClass,
    inst_config: InstrumentConfig,
):
  """The select function for instrument.

  This function will auto select the right instrument model for
  user base on the input information.

  Args:
    instrument_type (str): The instrument type to select
    module_name (str): The module name for the Instrument model to select
    class_name (str): The class name for the Instrument model to select
    com (ComInterfaceClass): The cominterface for the instrument
    inst_config (InstrumentConfig): The config for the instrument

  Returns:
    (Instrument): The builded ComInterfaceClass
  """
  logging.debug('Init instrument select')

  # The package argument might need to be updated depending on folder structure
  package_name = f'py_lab_hal.instrument.{instrument_type}.{module_name}'
  model_module = importlib.import_module(name=package_name)

  module = getattr(model_module, class_name)
  instance = module(com=com, inst_config=inst_config)

  logging.debug('Selecting Module %s %s.', instrument_type, module_name)

  return instance
