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

"""The logger for py_lab_hal."""

import datetime
import logging
import os

LOGGER_FORMATTER = (
    '%(asctime)s -%(levelname)1.1s- %(filename)s:%(lineno)d : %(message)s'
)
LOGGER_DATAFMT = '%Y_%m_%d_%H_%M_%S'
TIME_TXT = datetime.datetime.now().strftime(LOGGER_DATAFMT)


def setup_pylabhal_logger():
  """Setup the logger for Py-Lab-HAL."""

  logger = logging.getLogger()

  if len(logger.handlers) <= 1:
    formatter = logging.Formatter(LOGGER_FORMATTER, datefmt=LOGGER_DATAFMT)

    logger.setLevel(logging.DEBUG)

    if not os.path.exists('logs'):
      os.mkdir('logs')

    log_name = f'logs/{TIME_TXT}.log'

    fh = logging.FileHandler(log_name, 'a', encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)

    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)
    sh.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(sh)
