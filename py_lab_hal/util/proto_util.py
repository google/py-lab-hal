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

"""proto util."""

from typing import Any
from google.protobuf import json_format
from py_lab_hal.cominterface import cominterface
from py_lab_hal.datagrame import datagrame
from py_lab_hal.proto import datagrame_pb2  # type: ignore
from py_lab_hal.proto import py_lab_hal_pb2  # type: ignore
from py_lab_hal.util import json_dataclass


DATA2GRPC = {
    datagrame.StringDatagrame: ('stringData', datagrame_pb2.StringDatagrame),
}
GRPC2DATA = {
    datagrame_pb2.StringDatagrame: datagrame.StringDatagrame,
}


def grpc2com(
    request: py_lab_hal_pb2.InstRequest,
) -> cominterface.ConnectConfig:
  mesg_dict = json_format.MessageToDict(
      request, preserving_proto_field_name=True
  )
  mesg_dict['interface_type'] = mesg_dict['py_lab_hal_board_interface_type']
  return cominterface.ConnectConfig.from_dict(mesg_dict)


def com2grpc(connect_config: cominterface.ConnectConfig):
  cc_json: str = connect_config.to_json()
  request = py_lab_hal_pb2.InstRequest()
  return json_format.Parse(cc_json, request, ignore_unknown_fields=True)


def dump_object(obj) -> dict[str, Any]:
  """Dump the proto object to dict format.

  Args:
      obj: The proto object

  Returns:
      dict[str, Any]: The dict format
  """
  ans = {}
  for descriptor in obj.DESCRIPTOR.fields:
    value = getattr(obj, descriptor.name)

    if descriptor.type == descriptor.TYPE_ENUM:
      enum_name = descriptor.enum_type.values[value].name
      ans[json_dataclass.camel2snake(descriptor.name)] = enum_name
    elif descriptor.type != descriptor.TYPE_MESSAGE:
      ans[json_dataclass.camel2snake(descriptor.name)] = value
    else:
      pass
      # if descriptor.label == descriptor.LABEL_REPEATED:
      #   map(dump_object, value)
      # else:
      #   dump_object(value)

  return ans


def _data2grpc(data_g):
  filed_name, construct = DATA2GRPC[type(data_g)]
  data_json = data_g.to_dict()
  data_json.pop('sendTermBytes', '')
  data_json.pop('recvTermBytes', '')
  return {filed_name: construct(**data_json)}


def data2grpc_send(name: str, data_g) -> py_lab_hal_pb2.SendDataRequest:
  return py_lab_hal_pb2.SendDataRequest(name=name, **_data2grpc(data_g))


def data2grpc_recv(data_g) -> py_lab_hal_pb2.RecvDataResponse:
  return py_lab_hal_pb2.RecvDataResponse(**_data2grpc(data_g))


def grpc2data(request):
  data = getattr(request, request.WhichOneof('data'))
  return GRPC2DATA[type(data)](**dump_object(data))
