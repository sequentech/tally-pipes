#!/usr/bin/env python3

# This file is part of agora-results.
# Copyright (C) 2014-2016  Agora Voting SL <agora@agoravoting.com>

# agora-results is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License.

# agora-results  is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with agora-results.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup
from pip.req import parse_requirements

# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = parse_requirements("requirements.txt")

# reqs is a list of requirement
# e.g. ['django==1.5.1', 'mezzanine==1.4.6']
reqs = [str(ir.req) for ir in install_reqs]

setup(
    name='Agora Results',
    version='103111.1',
    author='Agora Voting Team',
    author_email='agora@agoravoting.com',
    packages=['agora_results', 'agora_results.pipes'],
    scripts=['agora-results'],
    url='http://pypi.python.org/pypi/agora_results/',
    license='LICENSE.AGPL3',
    description='agora results processing system',
    long_description=open('README.md').read(),
    install_requires=reqs,
    dependency_links = [
        'git+https://github.com/agoravoting/openstv.git',
        'git+https://github.com/agoravoting/agora-tally.git'
    ]
)
