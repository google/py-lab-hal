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

# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: py_lab_hal/proto/cominterface/aqvisa.proto
# Protobuf Python Version: 5.26.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n*py_lab_hal/proto/cominterface/aqvisa.proto\x12\x06\x61qvisa\"!\n\x0eViWriteRequest\x12\x0f\n\x07\x63ommand\x18\x01 \x01(\x0c\"[\n\x0fViWriteResponse\x12\x13\n\x06job_id\x18\x01 \x01(\x0cH\x00\x88\x01\x01\x12(\n\x0bstatus_code\x18\x02 \x01(\x0e\x32\x13.aqvisa.AQVI_STATUSB\t\n\x07_job_id\"/\n\x19ViGetCommandResultRequest\x12\x0e\n\x06job_id\x18\x01 \x01(\x0c:\x02\x18\x01\"J\n\x1aViGetCommandResultResponse\x12(\n\x0bstatus_code\x18\x01 \x01(\x0e\x32\x13.aqvisa.AQVI_STATUS:\x02\x18\x01\"2\n\rViReadRequest\x12\x12\n\x06job_id\x18\x01 \x01(\x0c\x42\x02\x18\x01\x12\r\n\x05\x63ount\x18\x02 \x01(\x03\"\x94\x01\n\x0eViReadResponse\x12(\n\x0bstatus_code\x18\x01 \x01(\x0e\x32\x13.aqvisa.AQVI_STATUS\x12\x1d\n\x10\x63ommand_response\x18\x02 \x01(\x0cH\x00\x88\x01\x01\x12\x16\n\tret_count\x18\x03 \x01(\x03H\x01\x88\x01\x01\x42\x13\n\x11_command_responseB\x0c\n\n_ret_count*\xae\t\n\x0b\x41QVI_STATUS\x12\x11\n\rAQVI_NO_ERROR\x10\x00\x12 \n\x1c\x41QVI_APPLICATION_NOT_STARTED\x10\x02\x12\x17\n\x13\x41QVI_NO_RETURN_DATA\x10\x07\x12\x1e\n\x1a\x41QVI_DATA_BUFFER_TOO_SMALL\x10\t\x12 \n\x1c\x41QVI_PREVIOUS_CMD_PROCESSING\x10\x0c\x12 \n\x1c\x41QVI_INPUT_PARAMETER_UNKNOWN\x10\r\x12$\n AQVI_INPUT_PARAMETER_INCOMPLETED\x10\x0e\x12\x17\n\x12\x41QVI_NOT_SUPPORTED\x10\xe8\x07\x12\x1c\n\x17\x41QVI_INCOMPLETE_COMMAND\x10\xe9\x07\x12\x18\n\x13\x41QVI_SUBWND_INVALID\x10\xea\x07\x12\x1b\n\x16\x41QVI_SUBWND_CNT_EXCEED\x10\xeb\x07\x12\x11\n\x0c\x41QVI_SW_BUSY\x10\xec\x07\x12\x1a\n\x15\x41QVI_LASUBWND_INVALID\x10\xed\x07\x12\x1a\n\x15\x41QVI_PASUBWND_INVALID\x10\xee\x07\x12\x1f\n\x1a\x41QVI_DECODE_REPORT_INVALID\x10\xef\x07\x12\x1f\n\x1a\x41QVI_TIMING_REPORT_INVALID\x10\xf0\x07\x12\x1e\n\x19\x41QVI_COMMAND_FORMAT_ERROR\x10\xf1\x07\x12 \n\x1b\x41QVI_INPUT_FILE_DIR_INVALID\x10\xf2\x07\x12!\n\x1c\x41QVI_CAPTURE_ALREADY_RUNNING\x10\xf3\x07\x12\x1d\n\x18\x41QVI_CAPTURE_NOT_RUNNING\x10\xf4\x07\x12\x1f\n\x1a\x41QVI_ROW_COL_INDEX_INVALID\x10\xf5\x07\x12\x1e\n\x19\x41QVI_SELECT_INDEX_INVALID\x10\xf6\x07\x12!\n\x1c\x41QVI_INPUT_PARAMETER_INVALID\x10\xf7\x07\x12)\n$AQVI_INPUT_SETTING_FILE_FORMAT_ERROR\x10\xf8\x07\x12\x1b\n\x16\x41QVI_FILE_ACCESS_ERROR\x10\xf9\x07\x12#\n\x1e\x41QVI_TRANSITION_REPORT_INVALID\x10\xfa\x07\x12$\n\x1f\x41QVI_MEASUREMENT_REPORT_INVALID\x10\xfb\x07\x12\x1e\n\x19\x41QVI_SELECT_LABEL_INVALID\x10\xfc\x07\x12\x1c\n\x17\x41QVI_SELECT_RANGE_ERROR\x10\xfd\x07\x12%\n AQVI_SELECT_CHANNEL_NAME_INVALID\x10\xfe\x07\x12\x1e\n\x19\x41QVI_CURSOR_SEARCH_FAILED\x10\xff\x07\x12\x1c\n\x17\x41QVI_WAVEFORM_NOT_READY\x10\x80\x08\x12\x18\n\x13\x41QVI_NOT_IN_EV_MODE\x10\x81\x08\x12\x1f\n\x1a\x41QVI_NO_EV_ANALYSIS_RESULT\x10\x82\x08\x12\x1b\n\x16\x41QVI_UNSUPPORT_FEATURE\x10\x8bN\x12\x1c\n\x17\x41QVI_UNFINISHED_FEATURE\x10\x8cN\x12\x1f\n\x1a\x41QVI_UNKNOWN_COMMAND_ERROR\x10\x8dN\x12\x17\n\x12\x41QVI_UNKNOWN_ERROR\x10\x8eN2\xe3\x01\n\x06\x41qVISA\x12<\n\x07ViWrite\x12\x16.aqvisa.ViWriteRequest\x1a\x17.aqvisa.ViWriteResponse\"\x00\x12\x39\n\x06ViRead\x12\x15.aqvisa.ViReadRequest\x1a\x16.aqvisa.ViReadResponse\"\x00\x12`\n\x12ViGetCommandResult\x12!.aqvisa.ViGetCommandResultRequest\x1a\".aqvisa.ViGetCommandResultResponse\"\x03\x88\x02\x01\x42\x1d\n\x05\x61\x63uteB\nAcuteProtoP\x01\xa2\x02\x05\x41\x63uteb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'py_lab_hal.proto.cominterface.aqvisa_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  _globals['DESCRIPTOR']._loaded_options = None
  _globals['DESCRIPTOR']._serialized_options = b'\n\005acuteB\nAcuteProtoP\001\242\002\005Acute'
  _globals['_VIGETCOMMANDRESULTREQUEST']._loaded_options = None
  _globals['_VIGETCOMMANDRESULTREQUEST']._serialized_options = b'\030\001'
  _globals['_VIGETCOMMANDRESULTRESPONSE']._loaded_options = None
  _globals['_VIGETCOMMANDRESULTRESPONSE']._serialized_options = b'\030\001'
  _globals['_VIREADREQUEST'].fields_by_name['job_id']._loaded_options = None
  _globals['_VIREADREQUEST'].fields_by_name['job_id']._serialized_options = b'\030\001'
  _globals['_AQVISA'].methods_by_name['ViGetCommandResult']._loaded_options = None
  _globals['_AQVISA'].methods_by_name['ViGetCommandResult']._serialized_options = b'\210\002\001'
  _globals['_AQVI_STATUS']._serialized_start=511
  _globals['_AQVI_STATUS']._serialized_end=1709
  _globals['_VIWRITEREQUEST']._serialized_start=54
  _globals['_VIWRITEREQUEST']._serialized_end=87
  _globals['_VIWRITERESPONSE']._serialized_start=89
  _globals['_VIWRITERESPONSE']._serialized_end=180
  _globals['_VIGETCOMMANDRESULTREQUEST']._serialized_start=182
  _globals['_VIGETCOMMANDRESULTREQUEST']._serialized_end=229
  _globals['_VIGETCOMMANDRESULTRESPONSE']._serialized_start=231
  _globals['_VIGETCOMMANDRESULTRESPONSE']._serialized_end=305
  _globals['_VIREADREQUEST']._serialized_start=307
  _globals['_VIREADREQUEST']._serialized_end=357
  _globals['_VIREADRESPONSE']._serialized_start=360
  _globals['_VIREADRESPONSE']._serialized_end=508
  _globals['_AQVISA']._serialized_start=1712
  _globals['_AQVISA']._serialized_end=1939
# @@protoc_insertion_point(module_scope)
