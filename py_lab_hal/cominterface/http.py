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

"""Child ComInterfaceClass Module of http."""

import logging
from typing import Any, Literal, Optional, TypeAlias

from py_lab_hal.cominterface import cominterface
import requests
from requests import auth

HttpMethodType: TypeAlias = Literal['get', 'put']


class Http(cominterface.ComInterfaceClass):
  """Child ComInterfaceClass Module of http."""

  _session: requests.Session
  _auth_obj: Optional[auth.AuthBase]
  method: HttpMethodType
  data: dict[str, Any] = {}
  headers_dict: dict[str, Any] = {}

  def _open(self) -> None:
    self._auth_obj = None
    self._session = requests.Session()
    self.auth()
    logging.debug('Connecting to %s', self.connect_config.http_config.url)

  def auth(self):
    if self.connect_config.http_config.auth_url:
      auth_function = getattr(
          self._session, self.connect_config.http_config.auth_mode
      )
      response = auth_function(
          f'http://{self.connect_config.http_config.auth_url}',
          data=self.connect_config.http_config.auth_data,
      )
      response.raise_for_status()
    else:
      auth_function = getattr(
          auth, self.connect_config.http_config.http_auth_mode
      )
      self._auth_obj = auth_function(
          self.connect_config.http_config.login,
          self.connect_config.http_config.password,
      )

  def _close(self) -> None:
    try:
      self._session.close()
    except AttributeError:
      pass

  def _send(self, data: bytes) -> None:
    request_func = getattr(self._session, self.method)
    response = request_func(
        data,
        data=self.data,
        headers=self.headers_dict,
        timeout=self.connect_config.timeout.connect,
        auth=self._auth_obj,
    )
    response.raise_for_status()

  def _recv(self) -> bytes:
    raise NotImplementedError('Http did not support read and query.')

  def _query(self, data: bytes) -> bytes:
    raise NotImplementedError('Http did not support read and query.')

  def _set_timeout(self, seconds: int) -> None:
    pass
