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

"""Data Logger Demo."""

from py_lab_hal.data_logger import test_logger


def func(index):
  data = dict()
  data['one'] = 'Test'
  if index != 5:
    data['two'] = index + 2

  data['three'] = index

  return data


if __name__ == '__main__':
  log = test_logger.TestitemLogger('demo_testitem')
  t = log.gen_data_logger('test', ['one', 'two', 'three'])
  for i in range(10):
    t.get_data(func(i))
