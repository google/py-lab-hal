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

"""Pytype setup file."""

import pathlib
import re

from setuptools import find_packages
from setuptools import setup

ROOT = pathlib.Path(__file__).parent
DIR = ROOT / 'pyhal' / 'dut_interface' / 'adb'
FILES = [str(x) for x in DIR.glob('*')]
REQUIREMENTS = ROOT / 'requirements.txt'

# get the dependencies
with open(REQUIREMENTS, encoding='utf-8') as f:
  ALL_REQS = f.read().split('\n')[:-1]
INSTALL_REQUIRES = [
    x.strip() for x in ALL_REQS if not (re.match(r'(^(#|-))|(git\+)', x))
]
DEPENDENCY_LINKS = [
    x.strip().replace('git+', '') for x in ALL_REQS if 'git+' in x
]

setup(
    name='pyhal',
    version='2.0.20240311',
    description='A test instrument Hardware Abstraction Layer (HAL)',
    packages=find_packages(include=['pyhal', 'pyhal.*']),
    package_data={'pyhal.dut_interface': FILES},
    include_package_data=True,
    install_requires=INSTALL_REQUIRES,
    dependency_links=DEPENDENCY_LINKS,
    python_requires='>=3.9, <3.12',
)
