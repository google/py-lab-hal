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

"""Module of Client Side Agent."""

from __future__ import annotations

import grpc
from py_lab_hal.cominterface import cominterface
from py_lab_hal.proto import py_lab_hal_pb2  # type: ignore
from py_lab_hal.proto import py_lab_hal_pb2_grpc  # type: ignore
from py_lab_hal.util import proto_util


class ClientAgent(object):
  """Handle the communication between gRPC and PyLabHAL."""

  _instance = None
  _channel: grpc.Channel
  _basicsystem_stub: py_lab_hal_pb2_grpc.BasicSystemStub
  _inst_stub: py_lab_hal_pb2_grpc.InstrumentStub

  def __init__(self) -> None:
    ClientAgent._instance = self
    self.connected = False

  @staticmethod
  def get_instance() -> ClientAgent:
    if not ClientAgent._instance:
      return ClientAgent()
    return ClientAgent._instance

  def set_connection(self, ip: str) -> None:
    """Steup the connection."""

    self._channel = grpc.insecure_channel(ip)
    self._basicsystem_stub = py_lab_hal_pb2_grpc.BasicSystemStub(self._channel)
    self._inst_stub = py_lab_hal_pb2_grpc.InstrumentStub(self._channel)
    self.connected = True

  def close_connection(self, name: str) -> bool:
    """Steup the connection."""
    request = py_lab_hal_pb2.CloseRequest(name=name)
    response: py_lab_hal_pb2.CloseResponse = self._inst_stub.Close(request)
    return response.status

  def basic_system(self, action: str) -> py_lab_hal_pb2.SystemResponse:
    """gRPC Basic command."""

    request = py_lab_hal_pb2.SystemRequest(action=action)
    return self._basicsystem_stub.BasicSystem(request)

  def inst_init(
      self, connect_config: cominterface.ConnectConfig
  ) -> py_lab_hal_pb2.InstResponse:
    """gRPC instrument init."""

    request = proto_util.com2grpc(connect_config)
    response: py_lab_hal_pb2.InstResponse = self._inst_stub.Init(request)
    if not response.result:
      raise RuntimeError
    return response

  def send(self, name: str, data: bytes) -> None:
    """gRPC command init."""

    request = py_lab_hal_pb2.SendRequest(name=name, send=data)
    self._inst_stub.Send(request)
    return None

  def recv(self, name: str) -> bytes:
    """gRPC command init."""

    request = py_lab_hal_pb2.RecvRequest(name=name)
    response: py_lab_hal_pb2.RecvResponse = self._inst_stub.Recv(request)
    return response.read

  def query(self, name: str, data: bytes) -> bytes:
    """gRPC command init."""

    request = py_lab_hal_pb2.SendRequest(name=name, send=data)
    response: py_lab_hal_pb2.RecvResponse = self._inst_stub.Query(request)
    return response.read

  def send_data(self, name: str, data_g):
    """gRPC command init."""

    self._inst_stub.SendData(proto_util.data2grpc_send(name, data_g))
    return None

  def recv_data(self, name: str):
    """gRPC command init."""

    request = py_lab_hal_pb2.RecvRequest(name=name)
    response: py_lab_hal_pb2.RecvDataResponse = self._inst_stub.RecvData(
        request
    )
    return proto_util.grpc2data(response)
