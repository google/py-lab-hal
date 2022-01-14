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

"""Child ComInterfaceClass Module of acute."""
import logging

import grpc
from py_lab_hal.cominterface import cominterface as com
from py_lab_hal.proto.cominterface import aqvisa_pb2  # type: ignore
from py_lab_hal.proto.cominterface import aqvisa_pb2_grpc  # type: ignore


AcuteErrorCodes = com.PyLabHalErrorCodes({
    aqvisa_pb2.AQVI_NO_ERROR: ("AQVI_NO_ERROR", "No error"),
    aqvisa_pb2.AQVI_APPLICATION_NOT_STARTED: (
        "AQVI_APPLICATION_NOT_STARTED",
        "Error: The main software application was not started",
    ),
    aqvisa_pb2.AQVI_NO_RETURN_DATA: (
        "AQVI_NO_RETURN_DATA",
        "Warn: There's no any data returned.",
    ),
    aqvisa_pb2.AQVI_DATA_BUFFER_TOO_SMALL: (
        "AQVI_DATA_BUFFER_TOO_SMALL",
        "Warn: Input data buffer size is too small",
    ),
    aqvisa_pb2.AQVI_PREVIOUS_CMD_PROCESSING: (
        "AQVI_PREVIOUS_CMD_PROCESSING",
        "Warn: Previous command still processing",
    ),
    aqvisa_pb2.AQVI_INPUT_PARAMETER_UNKNOWN: (
        "AQVI_INPUT_PARAMETER_UNKNOWN",
        "Error: Input parameter unknown or not supported",
    ),
    aqvisa_pb2.AQVI_INPUT_PARAMETER_INCOMPLETED: (
        "AQVI_INPUT_PARAMETER_INCOMPLETED",
        "Error: Input parameter incompleted",
    ),
    aqvisa_pb2.AQVI_NOT_SUPPORTED: (
        "AQVI_NOT_SUPPORTED",
        "Error: Not supported in current software",
    ),
    aqvisa_pb2.AQVI_INCOMPLETE_COMMAND: (
        "AQVI_INCOMPLETE_COMMAND",
        "Error: Command incomplete",
    ),
    aqvisa_pb2.AQVI_SUBWND_INVALID: (
        "AQVI_SUBWND_INVALID",
        "Error: Input command requires exist SubWindow",
    ),
    aqvisa_pb2.AQVI_SUBWND_CNT_EXCEED: (
        "AQVI_SUBWND_CNT_EXCEED",
        "Error: Exceed maximum page count as requested",
    ),
    aqvisa_pb2.AQVI_SW_BUSY: (
        "AQVI_SW_BUSY",
        "Error: Input command ignored while software busy",
    ),
    aqvisa_pb2.AQVI_LASUBWND_INVALID: (
        "AQVI_LASUBWND_INVALID",
        "Error: Input command requires exist Logic Analyzer SubWindow",
    ),
    aqvisa_pb2.AQVI_PASUBWND_INVALID: (
        "AQVI_PASUBWND_INVALID",
        (
            "Command Error: Input command requires exist Protocol Analyzer"
            " SubWindow"
        ),
    ),
    aqvisa_pb2.AQVI_DECODE_REPORT_INVALID: (
        "AQVI_DECODE_REPORT_INVALID",
        "Error: Input command requires existing Decode Report",
    ),
    aqvisa_pb2.AQVI_TIMING_REPORT_INVALID: (
        "AQVI_TIMING_REPORT_INVALID",
        "Error: Input commands requires exist Timing Report",
    ),
    aqvisa_pb2.AQVI_COMMAND_FORMAT_ERROR: (
        "AQVI_COMMAND_FORMAT_ERROR",
        "Error: Command formate error",
    ),
    aqvisa_pb2.AQVI_INPUT_FILE_DIR_INVALID: (
        "AQVI_INPUT_FILE_DIR_INVALID",
        "Error: Incorrect input file",
    ),
    aqvisa_pb2.AQVI_CAPTURE_ALREADY_RUNNING: (
        "AQVI_CAPTURE_ALREADY_RUNNING",
        "Error: Sending Capture Start command while capture already running",
    ),
    aqvisa_pb2.AQVI_CAPTURE_NOT_RUNNING: (
        "AQVI_CAPTURE_NOT_RUNNING",
        "Error: Sending Capture Stop command while capture is not running",
    ),
    aqvisa_pb2.AQVI_ROW_COL_INDEX_INVALID: (
        "AQVI_ROW_COL_INDEX_INVALID",
        "Error: Input Row or Column index invalid",
    ),
    aqvisa_pb2.AQVI_SELECT_INDEX_INVALID: (
        "AQVI_SELECT_INDEX_INVALID",
        "Error: Input index selection invalid",
    ),
    aqvisa_pb2.AQVI_INPUT_PARAMETER_INVALID: (
        "AQVI_INPUT_PARAMETER_INVALID",
        "Error: Missing input parametes or not enough input parameter",
    ),
    aqvisa_pb2.AQVI_INPUT_SETTING_FILE_FORMAT_ERROR: (
        "AQVI_INPUT_SETTING_FILE_FORMAT_ERROR",
        "Error: Input settings file format error",
    ),
    aqvisa_pb2.AQVI_FILE_ACCESS_ERROR: (
        "AQVI_FILE_ACCESS_ERROR",
        "Error: Unable to reach select file directory",
    ),
    aqvisa_pb2.AQVI_TRANSITION_REPORT_INVALID: (
        "AQVI_TRANSITION_REPORT_INVALID",
        "Error: Input commands requires exist Transition Report",
    ),
    aqvisa_pb2.AQVI_MEASUREMENT_REPORT_INVALID: (
        "AQVI_MEASUREMENT_REPORT_INVALID",
        "Error: Input commands requires existint measurement report",
    ),
    aqvisa_pb2.AQVI_SELECT_LABEL_INVALID: (
        "AQVI_SELECT_LABEL_INVALID",
        "Error: Selected Label Name not valid",
    ),
    aqvisa_pb2.AQVI_SELECT_RANGE_ERROR: (
        "AQVI_SELECT_RANGE_ERROR",
        (
            "Error: Selected Range Condition Error, can't mix Line and Cursor"
            " Range condition"
        ),
    ),
    aqvisa_pb2.AQVI_SELECT_CHANNEL_NAME_INVALID: (
        "AQVI_SELECT_CHANNEL_NAME_INVALID",
        "Error: Selected Channel Name in Cursor Search is not valid",
    ),
    aqvisa_pb2.AQVI_CURSOR_SEARCH_FAILED: (
        "AQVI_CURSOR_SEARCH_FAILED",
        "Error: Cursor Search failed, unable to find more valid match",
    ),
    aqvisa_pb2.AQVI_WAVEFORM_NOT_READY: (
        "AQVI_WAVEFORM_NOT_READY",
        "Error: Waveform data not ready",
    ),
    aqvisa_pb2.AQVI_NOT_IN_EV_MODE: (
        "AQVI_NOT_IN_EV_MODE",
        "Error: Software is not configured in EV mode",
    ),
    aqvisa_pb2.AQVI_NO_EV_ANALYSIS_RESULT: (
        "AQVI_NO_EV_ANALYSIS_RESULT",
        "Error: Software doesn't have any valid EV analysis result",
    ),
    aqvisa_pb2.AQVI_UNSUPPORT_FEATURE: (
        "AQVI_UNSUPPORT_FEATURE",
        "Error: Unsupported feature",
    ),
    aqvisa_pb2.AQVI_UNFINISHED_FEATURE: (
        "AQVI_UNFINISHED_FEATURE",
        "Error: Unfinished Feature",
    ),
    aqvisa_pb2.AQVI_UNKNOWN_COMMAND_ERROR: (
        "AQVI_UNKNOWN_COMMAND_ERROR",
        "Error: Unknown command",
    ),
    aqvisa_pb2.AQVI_UNKNOWN_ERROR: (
        "AQVI_UNKNOWN_ERROR",
        "Error: Unknown Error",
    ),
})

_ACUTE_RESPONSE_COUNT = 200_000_000


class Acute(com.ComInterfaceClass):
  """Child ComInterfaceClass Module of acute."""

  _aqvisa_stub: aqvisa_pb2_grpc.AqVISAStub

  def _open(self) -> None:
    channel = grpc.insecure_channel(self.connect_config.network.address)
    self._aqvisa_stub = aqvisa_pb2_grpc.AqVISAStub(channel)

  def _close(self) -> None:
    pass

  def _send(self, data: bytes) -> None:
    request = aqvisa_pb2.ViWriteRequest(command=data)
    _ = self._aqvisa_stub.ViWrite(request)

  def _recv(self, size=-1) -> bytes:
    response: aqvisa_pb2.ViReadResponse = self._aqvisa_stub.ViRead(
        aqvisa_pb2.ViReadRequest(count=_ACUTE_RESPONSE_COUNT)
    )
    if response.status_code:
      logging.error("Acute %s", AcuteErrorCodes.get_error(response.status_code))
    return response.command_response

  def _query(self, data: bytes, size=-1) -> bytes:
    self.send_raw(data)
    return self.recv_raw()

  def _set_timeout(self, seconds: int) -> None:
    pass
