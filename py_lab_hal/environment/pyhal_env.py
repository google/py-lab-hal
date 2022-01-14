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

"""pyhal_env helps the user to create a connection layer to pyhal.

User construct the EnvConfig to config the runtime env that will needs in pyhal
and provides to the PyhalLayer class. The object of the cominterface,
dut_interface, and the instrument will be created. Use  get_object function to
get the object that is in the pyhal layer in this runtime.
"""

import dataclasses
import logging
from typing import Literal, overload

from py_lab_hal import builder
from py_lab_hal.cominterface import cominterface
from py_lab_hal.dut_interface import interface
from py_lab_hal.instrument import instrument
from py_lab_hal.util import json_dataclass


@dataclasses.dataclass
class PyhalCom(json_dataclass.DataClassJsonCamelMixIn):
  """The pyhal cominterface in pyhal env.

  Attributes:
      name (str): The name of the cominterface.
      config (ConnectConfig): The config for the cominterface.
  """

  name: str
  config: cominterface.ConnectConfig

  def __post__init__(self) -> None:
    self.config.__post_init__()


@dataclasses.dataclass
class PyhalDut(json_dataclass.DataClassJsonCamelMixIn):
  """The pyhal dut_interface in pyhal env.

  Attributes:
      name (str): The name of the dut_interface.
      config (DUTConnectConfig): The config for the dut_interface.
  """

  name: str
  config: interface.DUTConnectConfig


@dataclasses.dataclass
class PyhalInst(json_dataclass.DataClassJsonCamelMixIn):
  """The pyhal instrument in pyhal env.

  Attributes:
    name (str): The name of the instrument.
    com_name (str): The name of the cominterface.
    config: (InstrumentInfo): The instrument config.
  """

  name: str
  com_name: str
  instrument_type: str
  module_name: str
  config: instrument.InstrumentConfig


@dataclasses.dataclass
class EnvConfig(json_dataclass.DataClassJsonCamelMixIn):
  """The env config in pyhal env.

  Attributes:
    cominterface (list[PyhalCom]): The list of the pyhal_env cominterface.
    dut_interface (list[PyhalDut]): The list of the pyhal_env dut_interface.
    instrument (list[PyhalInst]): The list of the pyhal_env instrument.
  """

  cominterface: list[PyhalCom]
  dut_interface: list[PyhalDut]
  instrument: list[PyhalInst]


def prepare_com(
    full_data: list[PyhalCom],
) -> dict[str, cominterface.ComInterfaceClass]:
  """Init the cominterface based on the config.

  Args:
      full_data (list[PyhalCom]): The config for cominterface.

  Returns:
      dict[str, cominterface.ComInterfaceClass]: The dict for cominterface.
  """
  ans = {}
  for item in full_data:
    ans[item.name] = cominterface.select(connect_config=item.config)
    ans[item.name].open()
  return ans


def prepare_dut(
    full_data: list[PyhalDut],
) -> dict[str, interface.InterfaceClass]:
  """Init the dut_interface based on the config.

  Args:
      full_data (list[PyhalDut]): The config for dut_interface.

  Returns:
      dict[str, interface.InterfaceClass]: The dict for dut_interface.
  """
  ans = {}
  for item in full_data:
    ans[item.name] = interface.select(connect_config=item.config)
  return ans


def prepare_inst(
    full_data: list[PyhalInst],
    com_dict: dict[str, cominterface.ComInterfaceClass],
) -> dict[str, instrument.Instrument]:
  """Init the Instrument based on the config.

  Args:
      full_data (list[PyhalInst]): The config for Instrument.
      com_dict (dict[str, cominterface.ComInterfaceClass]): The dict for
        cominterface.

  Returns:
      dict[str, instrument.Instrument]: The dict for Instrument.
  """
  build = builder.PyHALBuilder()
  ans = {}
  for item in full_data:
    build.cominterface = com_dict[item.com_name]
    build.instrument_config = item.config
    ans[item.name] = build.build_instrument(
        f'{item.instrument_type}.{item.module_name}'
    )
  return ans


class PyhalLayer:
  """The layer connects to PyHAL."""

  def __init__(
      self,
      env_config: EnvConfig,
  ) -> None:
    try:
      self._com = prepare_com(env_config.cominterface)
      self._dut = prepare_dut(env_config.dut_interface)
      self._inst = prepare_inst(env_config.instrument, self.com)
    except:
      logging.exception('Get Error while setup connection or instrument.')
      raise

  @property
  def com(self) -> dict[str, cominterface.ComInterfaceClass]:
    return self._com

  @property
  def dut(self) -> dict[str, interface.InterfaceClass]:
    return self._dut

  @property
  def inst(self) -> dict[str, instrument.Instrument]:
    return self._inst

  @overload
  def get_object(
      self, layer_type: Literal['cominterface'], name: str
  ) -> cominterface.ComInterfaceClass:
    ...

  @overload
  def get_object(
      self, layer_type: Literal['dut_interface'], name: str
  ) -> interface.InterfaceClass:
    ...

  @overload
  def get_object(
      self, layer_type: Literal['instrument'], name: str
  ) -> instrument.Instrument:
    ...

  def get_object(self, layer_type, name):
    """Get the object in the pyhal layer.

    Args:
        layer_type (str): The type of the object.
        name (_type_): The name of the object.

    Returns:
        The object in the pyhal layer.
    """
    interface_mapping = {
        'cominterface': self.com,
        'dut_interface': self.dut,
        'instrument': self.inst,
    }
    interface_dict = interface_mapping[layer_type]
    return interface_dict[name]
