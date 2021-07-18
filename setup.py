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
from setuptools.command.sdist import sdist

class SdistI18n(sdist):
    def run(self):
        self.run_command('compile_catalog')
        sdist.run(self)

setup(
    name='agora-results',
    version='20.2.0',
    author='Agora Voting SL',
    author_email='contact@nvotes.com',
    packages=['agora_results', 'agora_results.pipes'],
    scripts=['agora-results'],
    url='http://pypi.python.org/pypi/agora_results/',
    license='AGPL-3.0',
    description='agora results processing system',
    long_description=open('README.md').read(),
    setup_requires=['Babel'],
    cmdclass={'sdist': SdistI18n},
    install_requires=[
        'reportlab==3.3.0',
        'requests==2.20.0',
        'Babel==2.9.1',
        'agora-tally @ git+https://github.com/agoravoting/agora-tally.git@review-deps-licenses'
    ]
)
