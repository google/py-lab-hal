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

from collections.abc import Iterable
import csv
import datetime
import logging
import os
import pathlib
from typing import Any


LOGGER_DATAFMT = '%Y_%m_%d_%H_%M_%S'
TIME_TXT = datetime.datetime.now().strftime(LOGGER_DATAFMT)


class DataLogger(object):
  """The Results class provides a interface to writing data."""

  def __init__(
      self, root_folder: str, data_filename: str, headers: list[str]
  ) -> None:
    """The constructor for the DataLogger class.

    Args:
      root_folder (str): The root path of the data file.
      data_filename (str): The file name of data file.
      headers (list[str]): The headers for this data logger.
    """
    self.folder = root_folder
    pathlib.Path(self.folder).mkdir(parents=True, exist_ok=True)
    logging.debug('Creating Folder %s', self.folder)

    self.path = os.path.join(self.folder, f'{data_filename}_{TIME_TXT}.csv')
    self.headers = headers
    self.write_csv([self.headers])
    self.buffer: list[Iterable[Any]] = []

  def clean_data(self) -> None:
    self.buffer = []

  def add_data(self, data: dict[str, Any]) -> None:
    self.buffer.append(self.build_data(data))

  def flush_data(self) -> None:
    self.write_csv(self.buffer)
    self.clean_data()

  def build_data(self, data: dict[str, Any]) -> Iterable[Any]:
    data_build: dict[str, Any] = dict()
    for header in self.headers:
      data_build[header] = data.get(header, '')
    return data_build.values()

  def get_data(self, data: dict[str, Any]) -> None:
    """Input the data from user.

    Args:
      data (dict of Any): The dict with the key as headers from init function
    """
    self.clean_data()
    self.add_data(data)
    self.flush_data()

  def write_csv(self, txtdata: list[Iterable[Any]]) -> None:
    """Write the data to the file.

    Args:
      txtdata (Iterable[Any]): The list of data in the order with headers on
        __init__
    """
    with open(self.path, 'a', newline='') as data_csv:
      writer = csv.writer(data_csv)
      writer.writerows(txtdata)
      logging.debug('Write to %s with %s', self.path, txtdata)
