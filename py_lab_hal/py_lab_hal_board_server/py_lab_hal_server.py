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

"""PyLabHAL Board Server Side Entry Point."""

from concurrent import futures
import time

from google.protobuf import empty_pb2  # type: ignore
import grpc
from py_lab_hal.proto import py_lab_hal_pb2  # type: ignore
from py_lab_hal.proto import py_lab_hal_pb2_grpc  # type: ignore
from py_lab_hal.py_lab_hal_board_server import server_agent
from py_lab_hal.util import proto_util


class InstInitServicer(py_lab_hal_pb2_grpc.InstrumentServicer):
  """gRPC InstInitServicer."""

  def __init__(self) -> None:
    self.inst = server_agent.ServerAgent.get_instance()

  def Init(
      self, request: py_lab_hal_pb2.InstRequest, context
  ) -> py_lab_hal_pb2.InstResponse:
    return py_lab_hal_pb2.InstResponse(
        result=self.inst.reg_device(request.name, proto_util.grpc2com(request)),
        name=request.name,
    )

  def Close(
      self, request: py_lab_hal_pb2.CloseRequest, context
  ) -> py_lab_hal_pb2.CloseResponse:
    return py_lab_hal_pb2.CloseResponse(status=self.inst.close(request.name))

  def Send(
      self, request: py_lab_hal_pb2.SendRequest, context
  ) -> empty_pb2.Empty:
    self.data_handler.send(request.name, request.send)
    return empty_pb2.Empty()

  def Recv(
      self, request: py_lab_hal_pb2.RecvRequest, context
  ) -> py_lab_hal_pb2.RecvResponse:
    return py_lab_hal_pb2.RecvResponse(read=self.inst.read(request.name))

  def Query(
      self, request: py_lab_hal_pb2.SendRequest, context
  ) -> py_lab_hal_pb2.RecvResponse:
    self.data_handler.send(request.name, request.send)
    return py_lab_hal_pb2.RecvResponse(read=self.inst.read(request.name))

  def SendData(
      self, request: py_lab_hal_pb2.SendDataRequest, context
  ) -> empty_pb2.Empty:
    self.data_handler.send_data(request.name, proto_util.grpc2data(request))
    return empty_pb2.Empty()

  def RecvData(
      self, request: py_lab_hal_pb2.RecvRequest, context
  ) -> py_lab_hal_pb2.RecvDataResponse:
    return proto_util.data2grpc_recv(self.data_handler.recv_data(request.name))


class BasicSystemServicer(py_lab_hal_pb2_grpc.BasicSystemServicer):
  """gRPC BasicSystemServicer."""

  def BasicSystem(
      self, request: py_lab_hal_pb2.SystemRequest, context
  ) -> py_lab_hal_pb2.SystemResponse:
    response = py_lab_hal_pb2.SystemResponse()
    self.inst = server_agent.ServerAgent.get_instance()

    if request.action == py_lab_hal_pb2.SYSTEM_QUER:
      response.response_command = py_lab_hal_pb2.SYSTEM_SUCC
    elif request.action == py_lab_hal_pb2.SYSTEM_CONN:
      self.inst.reg_sys()
      response.response_command = py_lab_hal_pb2.SYSTEM_SUCC
    elif request.action == py_lab_hal_pb2.SYSTEM_FCON:
      self.inst.del_sys()
      self.inst.reg_sys()
      response.response_command = py_lab_hal_pb2.SYSTEM_SUCC
    elif request.action == py_lab_hal_pb2.SYSTEM_DISC:
      self.inst.del_sys()
    elif request.action == py_lab_hal_pb2.SYSTEM_SCAN:
      response.scan_info = self.inst.scan()
      response.response_command = py_lab_hal_pb2.SYSTEM_SUCC
    else:
      pass

    if self.inst.is_busy:
      response.response_status = py_lab_hal_pb2.SYSTEM_BUSY
    else:
      response.response_status = py_lab_hal_pb2.SYSTEM_IDLE

    return response


def serve() -> None:
  """Serve Function."""

  server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
  py_lab_hal_pb2_grpc.add_InstrumentServicer_to_server(
      InstInitServicer(), server
  )
  py_lab_hal_pb2_grpc.add_BasicSystemServicer_to_server(
      BasicSystemServicer(), server
  )

  server.add_insecure_port('[::]:50051')
  server.start()
  try:
    while True:
      time.sleep(86400)
  except KeyboardInterrupt:
    server.stop(0)


if __name__ == '__main__':
  serve()
