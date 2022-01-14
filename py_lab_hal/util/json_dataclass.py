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

"""Json_dataclass."""

import re

import dataclasses_json


class DataClassJsonCamelMixIn(dataclasses_json.DataClassJsonMixin):
  dataclass_json_config = dataclasses_json.config(
      letter_case=dataclasses_json.LetterCase.CAMEL,
      undefined=dataclasses_json.Undefined.EXCLUDE,
  )['dataclasses_json']


def camel2snake(value: str) -> str:
  """Convert value from CamelCase to snake_case."""
  return (
      re.sub(pattern=r'([A-Z]+)', repl=r'_\1', string=value).lower().lstrip('_')
  )
