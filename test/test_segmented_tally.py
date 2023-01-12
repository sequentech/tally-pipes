#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# This file is part of tally-pipes.
# Copyright (C) 2017  Sequent Tech Inc <legal@sequentech.io>

# tally-pipes is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License.

# tally-pipes  is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with tally-pipes.  If not, see <http://www.gnu.org/licenses/>.

import copy
import json
from tally_pipes.utils.segmented_tally import (
    get_public_keys, get_category_primes, is_quadratic_residue,
    process_raw_ballot
)
import os
import unittest

class TestSegmentedTally(unittest.TestCase):
    # test that category primes is calculated correctly
    def test_category_primes(self):
        segmented_election_config_path = os.path.join(
            "test", "segmented_election_config.json"
        )
        election_config = json.loads(open(segmented_election_config_path).read())
        category_names = election_config['configuration']['mixingCategorySegmentation']["categories"]
        pub_keys = get_public_keys(election_config['pks'])

        question_index = 0
        question = election_config['configuration']['questions'][question_index]

        question['pub_keys'] = pub_keys[question_index]
        category_primes = get_category_primes(
            question,
            category_names
        )

        # Ballot encoding for this question with 3 candidates is:
        #            /------------ invalid vote flag
        #            |  /-------- candidate A
        #            |  |  /----- candidate B
        #            |  |  |  /-- candidate C
        #            |  |  |  |
        # bases   = [2, 2, 2, 2]
        # choices = [1, 1, 1, 1]
        # max_encodable ballot => [1, 1, 1, 1] => 1 + 2*(1 + 2*(1 + 2*1)) => 15
        #
        # Next 2 primes after 15 that are a quadratic residue: 17, 19
        self.assertEqual(
            {'Sevilla': 17, 'Madrid': 19},
            category_primes
        )

        # if we remove candidate C, then 
        #            /------------ invalid vote flag
        #            |  /-------- candidate A
        #            |  |  /----- candidate B
        #            |  |  |
        # bases   = [2, 2, 2]
        # choices = [1, 1, 1]
        # max_encodable ballot => [1, 1, 1] => 1 + 2*(1 + 2*1) => 7
        #
        # Next 2 primes after 7 that are a quadratic residue: 13, 17
        question2 = copy.deepcopy(question)
        del question2['answers'][2]

        # the next prime after 7 is 11, but it's not a quadratic residue: check
        p = question2['pub_keys']['p']
        q = question2['pub_keys']['q']
        self.assertFalse(is_quadratic_residue(11, p, q))

        category_primes2 = get_category_primes(
            question2,
            category_names
        )
        self.assertEqual(
            {'Sevilla': 13, 'Madrid': 17},
            category_primes2
        )

    # test that raw ballots are decoded correctly
    def test_process_raw_ballot(self):
        category_primes = {'Sevilla': 17, 'Madrid': 19}
        test_ballots = [
            {"encoded": f"\"{ 17 * 1 }\"\n", "decoded": ("Sevilla", '"1"\n')},
            {"encoded": f"\"{ 17 * 2 }\"\n", "decoded": ("Sevilla", '"2"\n')},
            {"encoded": f"\"{ 19 * 1 }\"\n", "decoded": ("Madrid", '"1"\n')},
            {"encoded": f"\"{ 19 * 3 }\"\n", "decoded": ("Madrid", '"3"\n')},
        ]
        for test_ballot in test_ballots:
            result = process_raw_ballot(test_ballot['encoded'], category_primes)
            self.assertEqual(test_ballot['decoded'], result)

    # test that invalid raw ballots fail
    def test_invalid_process_raw_ballot(self):
        category_primes = {'Sevilla': 13, 'Madrid': 17, 'Barcelona': 19}
        test_ballots = [
            f"\"{ 5 * 1 }\"\n",
            f"\"{ 23 * 1 }\"\n",
            f"\"{ 29 * 1 }\"\n",
        ]
        for test_ballot in test_ballots:
            try:
                process_raw_ballot(test_ballot['encoded'], category_primes)
                raise Exception('This should have raised an exception')
            except:
                continue
