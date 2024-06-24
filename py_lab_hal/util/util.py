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

"""util."""

from __future__ import annotations

import enum
import logging
import re
from typing import Any, TypeVar, overload

KEYTYPE = TypeVar('KEYTYPE', bound='str')
VALUETYPE = TypeVar('VALUETYPE')
ENUMINPUTTYPE = TypeVar('ENUMINPUTTYPE', bound='PyLabHalEnum')


class PyLabHalEnum(enum.Enum):
  """The enum class that used in PyLabHAL."""

  @overload
  @classmethod
  def get(cls: VALUETYPE, attr: str) -> VALUETYPE:
    ...

  @overload
  @classmethod
  def get(cls, attr: ENUMINPUTTYPE) -> ENUMINPUTTYPE:
    ...

  @classmethod
  def get(cls, attr):
    if not attr:
      return

    if isinstance(attr, str):
      if hasattr(cls, attr):
        return getattr(cls, attr)
      if hasattr(cls, attr.upper()):
        return getattr(cls, attr.upper())

    if isinstance(attr, cls):
      return attr.value

    raise ValueError(
        f'Invalid attribute {attr} for {cls.__name__}, The attr that is'
        f' available: {cls.__members__.keys()}'
    )


class InstrumentEnum(PyLabHalEnum):
  """The enum class that used in py-lab-hal."""

  @staticmethod
  def _generate_next_value_(name, start, count, last_values):
    return name.upper()


@overload
def _make_list(channel: int, *args) -> list[Any]:
  ...


@overload
def _make_list(channel: list[int], *args) -> list[list[Any]]:
  ...


def _make_list(channel, *args):
  """The helper function of the multiple channel.

  Args:
    channel (int or list of int): The channel number
    *args: The parameters of channel

  Returns:
    (list of list):  The channel and parameters for each channels
  """

  ans = []
  ans.append(channel)

  if isinstance(channel, list):
    for item in args:
      if isinstance(item, list):
        if len(channel) != len(item):
          raise ValueError(
              'The length of each args and channel must be the same.'
          )
        ans.append(item)
      else:
        ans.append([item] * len(channel))
    return list(map(list, zip(*ans)))

  for item in args:
    if isinstance(item, list):
      raise ValueError(
          'If channel is not the list, then args must not the list.'
      )
    ans.append(item)
  return [ans]


def loop_channel(func, channel, *args):
  return [
      func(channel, *each_args)
      for channel, *each_args in _make_list(channel, *args)
  ]


def get_from_dict(
    dict_in: dict[KEYTYPE, VALUETYPE], key_in: KEYTYPE
) -> VALUETYPE:
  """The helper function of get item in the dict."""

  try:
    val = dict_in[re.sub('[^a-zA-Z0-9_]', '', key_in).upper()]  # type: ignore
  except KeyError:
    logging.exception(
        'Key %s not found in dict, You can use %s',
        key_in,
        list(dict_in.keys()),
    )
    raise
  return val


def find_the_nearest(list_in, value_in):
  """Get the nearest value in the list."""

  difference = lambda list_in: abs(list_in - value_in)
  res = min(list_in, key=difference)
  return res
