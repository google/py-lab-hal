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

"""The data logger to help the user."""

from __future__ import annotations

import datetime
import logging
import os
import pathlib

from py_lab_hal.data_logger import data_logger


DEFAULT_FOLDER_NAME = 'collect_data'
LOGGER_DATAFMT = '%Y_%m_%d_%H_%M_%S'
TIME_TXT = datetime.datetime.now().strftime(LOGGER_DATAFMT)


class TestitemLogger(object):
  """The Results class provides a interface to writing data."""

  def __init__(
      self, testitem_name: str, folder_layer: list[str] | None = None
  ) -> None:
    """The constructor for the TestitemLogger class.

    Args:
      testitem_name (str): The testitem name.
      folder_layer (list[str] | None, optional): The folder layer that you want
        to storage the file in the test logger folder. Defaults to None.
    """
    self.testitem_name = testitem_name
    self._timestamp = TIME_TXT
    self.folder_name = f'{testitem_name}_{self._timestamp}'
    if folder_layer:
      self.folder = os.path.join(
          DEFAULT_FOLDER_NAME, *folder_layer, testitem_name, self.folder_name
      )
    else:
      self.folder = os.path.join(
          DEFAULT_FOLDER_NAME, testitem_name, self.folder_name
      )

    self.gen_folder()

  @property
  def timestamp(self) -> str:
    return self._timestamp

  def gen_folder(self, folder_layer: list[str] | None = None) -> None:
    """Generate the folder in the test logger folder.

    Args:
        folder_layer (list[str] | None, optional): The folder layer that you
          want to storage the file in the test logger folder. Defaults to None.
    """
    if folder_layer:
      folder_path = pathlib.Path(self.folder, *folder_layer)
    else:
      folder_path = pathlib.Path(self.folder)
    logging.debug('Creating Folder %s', str(folder_path))
    folder_path.mkdir(parents=True, exist_ok=True)

  def gen_path(self, folder_layer: list[str] | None = None) -> str:
    """Generate the file path in the test logger folder.

    Args:
      folder_layer (list[str] | None, optional): The folder layer that you want
        to storage the file in the test logger folder. Defaults to None.

    Returns:
        str: The path of the file.
    """
    if folder_layer:
      if len(folder_layer) > 1:
        self.gen_folder(folder_layer[:-1])
      return os.path.join(self.folder, *folder_layer)
    return self.folder

  def gen_data_logger(
      self,
      data_filename: str,
      headers: list[str],
      folder_layer: list[str] | None = None,
  ) -> data_logger.DataLogger:
    """Generate the DataLogger instance based on the test logger folfer.

    Args:
      data_filename (str): The file name of the data
      headers (list[str]): The headers for this data logger.
      folder_layer (list[str] | None, optional): The folder layer that you want
        to storage the file in the test logger folder. Defaults to None.

    Returns:
        DataLogger: The DataLogger instance.
    """
    folder_root = self.gen_path(folder_layer)
    return data_logger.DataLogger(folder_root, data_filename, headers)
