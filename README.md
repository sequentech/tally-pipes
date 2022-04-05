# tally-pipes [![tests_badge]][tests_link]

[tests_badge]: https://github.com/sequentech/tally-pipes/workflows/Test%20python/badge.svg
[tests_link]: https://github.com/sequentech/tally-pipes/actions?query=workflow%3A%22Test+python%22

## Introduction
 
Piece of software that processes a tally and given a pipeline it modifies the results. This is useful for example to post-process a tally to:
 - resolve tie-breaks (there can be many different algorithms to do that)
 - apply egalitarian criteria for men and women (sometimes this is even legaly mandated)
 - sort the winners of stv (which by default doesn't sort winners, just elect them)
 - other complex post-processing, like using the result of question 1 to select the first winner and then using the results of question 2 to sort the rest of the winners

## Installation

Just execute this (no stable release yet):

    $ mkvirtualenv tally-pipes -p $(which python3)
    $ workon tally-pipes
    $ pip install git+https://github.com/sequentech/tally-pipes.git

## Usage

    $ tally-pipes --tally tally.tar.gz --config tally_pipes.test_config

Or the same shorter:

    $ tally-pipes -t tally.tar.gz -c config.json

## Configuration file

Configuration file specifies the pipeline of functions to be applied to the results. This is an example configuration file (yes just one variable for the pipeline, at least for now):

    [
        [
          "tally_pipes.pipes.results.do_tallies",
          {}
        ]
    ]

## Testing

Execute the unit tests with:

    $ python3 -m unittest

## Available pipes

Available pipes are documented in python, in the tally_pipes/pipes directory.

## Development

You can of course take a look at the available pipes in the tally_pipes/pipes/ subdirectory and see how to develop your own pipe. Be careful, you might cook the results in an unexpected way!

This software is in development state, that's why we haven't released any stable version yet. Patches and new pipes are welcome. We will review the pipe so that it does what is expected.

## Internationalization

Some of these pipes uses gettext for internationalization, like the PDF generation pipes. We use Babel and
mainly followed the guide here: https://www.mattlayman.com/blog/2015/i18n/

## More

You can see all the available commands with:

    $ tally-pipes --help

You can contact us at sequent-voting@googlegroups.com mailing list or at #sequent freenode.net channel.

## License

Copyright (C) 2015 Sequent Tech Inc and/or its subsidiary(-ies).
Contact: legal@sequentech.io

This file is part of the sequent-core-view module of the Sequent Tech project.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU General Public License for more details.

Commercial License Usage
Licensees holding valid commercial Sequent Tech project licenses may use this
file in accordance with the commercial license agreement provided with the
Software or, alternatively, in accordance with the terms contained in
a written agreement between you and Sequent Tech Inc. For licensing terms and
conditions and further information contact us at legal@sequentech.io .

GNU Affero General Public License Usage
Alternatively, this file may be used under the terms of the GNU Affero General
Public License version 3 as published by the Free Software Foundation and
appearing in the file LICENSE.AGPL3 included in the packaging of this file, or
alternatively found in <http://www.gnu.org/licenses/>.

External libraries
This program distributes libraries from external sources. If you follow the
compilation process you'll download these libraries and their respective
licenses, which are compatible with our licensing.
