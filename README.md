# Introduction

Piece of software that processes a tally and given a pipeline it modifies the results. This is useful for example to post-process a tally to:
 - resolve tie-breaks (there can be many different algorithms to do that)
 - apply egalitarian criteria for men and women (sometimes this is even legaly mandated)
 - sort the winners of stv (which by default doesn't sort winners, just elect them)
 - other complex post-processing, like using the result of question 1 to select the first winner and then using the results of question 2 to sort the rest of the winners

# Installation

Just execute this (no stable release yet):

    $ mkvirtualenv agora-results -p $(which python3)
    $ workon agora-results
    $ pip install git+https://github.com/agoravoting/agora-results.git

# Usage

    $ agora-results --tally tally.tar.gz --config agora_tongo.test_config

Or the same shorter:

    $ agora-results -t tally.tar.gz -c config.json

# Configuration file

Configuration file specifies the pipeline of functions to be applied to the results. This is an example configuration file (yes just one variable for the pipeline, at least for now):

    [
        [
          "agora_results.pipes.results.do_tallies",
          {"ignore_invalid_votes": true}
        ]
    ]

# Available pipes

Available pipes are documented in python, in the agora_results/pipes directory.

# Development

You can of course take a look at the available pipes in the agora_results/pipes/ subdirectory and see how to develop your own pipe. Be careful, you might cook the results in an unexpected way!

This software is in development state, that's why we haven't released any stable version yet. Patches and new pipes are welcome. We will review the pipe so that it does what is expected.

# More

You can see all the available commands with:

    $ agora-results --help

You can contact us at agora-voting@googlegroups.com mailing list or at #agoravoting freenode.net channel.

# License

Copyright (C) 2015 Agora Voting SL and/or its subsidiary(-ies).
Contact: legal@agoravoting.com

This file is part of the agora-core-view module of the Agora Voting project.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU General Public License for more details.

Commercial License Usage
Licensees holding valid commercial Agora Voting project licenses may use this
file in accordance with the commercial license agreement provided with the
Software or, alternatively, in accordance with the terms contained in
a written agreement between you and Agora Voting SL. For licensing terms and
conditions and further information contact us at legal@agoravoting.com .

GNU Affero General Public License Usage
Alternatively, this file may be used under the terms of the GNU Affero General
Public License version 3 as published by the Free Software Foundation and
appearing in the file LICENSE.AGPL3 included in the packaging of this file, or
alternatively found in <http://www.gnu.org/licenses/>.

External libraries
This program distributes libraries from external sources. If you follow the
compilation process you'll download these libraries and their respective
licenses, which are compatible with our licensing.