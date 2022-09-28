#!/usr/bin/env python3

# This file is part of tally-pipes.
# Copyright (C) 2014-2016  Sequent Tech Inc <legal@sequentech.io>

# tally-pipes is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License.

# tally-pipes  is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with tally-pipes.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup
from setuptools.command.sdist import sdist

class SdistI18n(sdist):
    def run(self):
        self.run_command('compile_catalog')
        sdist.run(self)

setup(
    name='tally-pipes',
    version='6.1.6',
    author='Sequent Tech Inc',
    author_email='contact@sequentech.io',
    packages=['tally_pipes', 'tally_pipes.pipes'],
    scripts=['tally-pipes'],
    url='https://github.com/sequentech/tally-pipes',
    license='AGPL-3.0',
    description='sequent results processing system',
    long_description=open('README.md').read(),
    setup_requires=['Babel'],
    cmdclass={'sdist': SdistI18n},
    install_requires=[
        'reportlab==3.5.55',
        'requests==2.20.0',
        'Babel==2.9.1',
        'pytz==2021.3',
        'tally-methods @ git+https://github.com/sequentech/tally-methods.git@6.1.6'
    ]
)
