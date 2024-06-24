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

"""Demonstrate monsoon power monitor usages."""

from py_lab_hal import builder
from py_lab_hal.cominterface import cominterface
from py_lab_hal.cominterface import usbmonsoon as usbm
from py_lab_hal.instrument.powermeter import monsoon as mon
from py_lab_hal.instrument.powermeter import powermeter as pm


def setup_py_lab_hal():
  """Setup the py_lab_hal."""

  build = builder.PyLabHALBuilder()
  build.connection_config = cominterface.ConnectConfig(
      interface_type='usb',
      usb_config=cominterface.UsbConfig(
          device_type=usbm.MonsoonDeviceType.HIGH_VOLTAGE,
          protocol=usbm.MonsoonUsbProtocol.USB_BACKEND,
      ),
  )

  power_mon = build.build_instrument(builder.PowerMeter.MONSOON_HV)
  meas_cfg = pm.MeasurementTriggerConfig()
  return power_mon, meas_cfg


def setup_monsoon(power_mon: mon.Monsoon) -> None:
  power_mon.initialize(enable_main=True)
  power_mon.set_output_voltage(4.1)
  power_mon.set_powerup_current_limit(1)
  power_mon.set_runtime_current_limit(1.1)
  power_mon.set_json_output('simple_measurement.json')


def simple_measurements(
    power_mon: mon.Monsoon, meas_cfg: pm.MeasurementTriggerConfig
) -> None:
  """Measurement the current and voltage with OneShot Mode.

  Args:
      power_mon (mon.Monsoon): The Monsoon devices.
      meas_cfg (pm.MeasurementTriggerConfig): The Measurement config.
  """
  meas_cfg.numSamples = 10
  meas_cfg.samplingMode = pm.SamplingMode.oneShot

  power_mon.start_sampling(meas_cfg)
  for meas in power_mon.measure_current():
    print(
        f'current:{round(meas.main_current, 2)}mA '
        f'voltage:{round(meas.main_volts, 2)}V'
    )
  power_mon.stop_sampling(meas_cfg)


def periodic_measurements(
    power_mon: mon.Monsoon, meas_cfg: pm.MeasurementTriggerConfig
) -> None:
  """Measurement the current and voltage with Periodic Mode.

  Args:
      power_mon (mon.Monsoon): The Monsoon devices.
      meas_cfg (pm.MeasurementTriggerConfig): The Measurement config.
  """
  meas_cfg.samplingMode = pm.SamplingMode.periodic
  power_mon.start_sampling(meas_cfg)
  for _ in range(10):
    print(power_mon.get_measurements(meas_cfg))
  power_mon.stop_sampling(meas_cfg)


if __name__ == '__main__':
  power_monsoon, meas_config = setup_py_lab_hal()
  setup_monsoon(power_monsoon)
  simple_measurements(power_monsoon, meas_config)
  periodic_measurements(power_monsoon, meas_config)
