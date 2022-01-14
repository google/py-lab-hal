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

"""Child DCpsu Module of atticpx4000dp."""

import logging

from py_lab_hal.cominterface import cominterface
from py_lab_hal.instrument import instrument
from py_lab_hal.instrument.dcpsu import dcpsu

# Per programming guide, max OCP default is 22A
OCP_MAX_CURR = 20
OVP_MAX_VOLT = 40


class Aimtticpx4000dp(dcpsu.DCpsu):
  """Child DCpsu Class of atticpx4000dp."""

  def __init__(
      self,
      com: cominterface.ComInterfaceClass,
      inst_config: instrument.InstrumentConfig,
  ) -> None:
    super().__init__(com, inst_config)
    self._ocp_flag = {1: False, 2: False}

  def enable_OCP(self, channel, enable):
    self._ocp_flag[channel] = enable
    if enable:
      set_current = self.data_handler.query(f'I{channel}?').replace(
          f'I{channel}', ''
      )
      self.set_OCP_value(channel, float(set_current.strip()))
    else:
      self.set_OCP_value(channel, OCP_MAX_CURR)

  def enable_OVP(self, channel, enable):
    if enable:
      logging.warning('The OVP is auto enable after set OVP value.')
    else:
      logging.warning(
          'This instrument does not support OVP disable. Therefore set it to'
          ' the maximum voltage output.'
      )
      self.set_OVP_value(channel, OVP_MAX_VOLT)

  def set_OCP_value(self, channel, set_current):
    self.data_handler.send(f'OCP{channel} {set_current}')
    logging.warning('The OCP is auto enable after set OCP value.')

  def set_OVP_value(self, channel, ovp_voltage):
    self.data_handler.send(f'OVP{channel} {ovp_voltage:.2f}')
    logging.warning('The OVP is auto enable after set OVP value.')

  def set_sequence(self, channel, voltage, current, delay):
    raise NotImplementedError(
        'The Aimtti CPX4000DP does not support sequence output mode'
    )

  def set_range(self, channel, range_type, value):
    logging.warning(
        'Range selection on the CPX4000DP is set by the front panel only!'
    )

  def enable_remote_sense(self, enable):
    logging.warning(
        'Sense selection on the CPX4000DP is set at the terminal only!'
    )

  def set_NPLC(self, channel, power_line_freq, nplc):
    logging.warning('The CPX4000DP does not support configurable NPLC!')

  def measure_current(self, channel) -> float:
    # Returns unit so we need to strip it
    return float(self.data_handler.query(f'I{channel}O?').replace('A', ''))

  def measure_voltage(self, channel) -> float:
    # Returns unit so we need to strip it
    return float(self.data_handler.query(f'V{channel}O?').replace('V', ''))

  def set_output(self, channel, voltage, current):
    super().set_output(channel, voltage, current)
    if self._ocp_flag[channel]:
      self.enable_OCP(channel, True)

  def enable_output(self, channel, enable):
    self.data_handler.send(f'OP{channel} {int(enable)}')

  def set_output_voltage(self, channel, voltage):
    self.data_handler.send(f'V{channel} {voltage:.2f}')

  def set_output_current(self, channel, current):
    self.data_handler.send(f'I{channel} {current:.2f}')
