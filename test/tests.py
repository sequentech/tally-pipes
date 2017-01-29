#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# This file is part of agora-results.
# Copyright (C) 2017  Agora Voting SL <agora@agoravoting.com>

# agora-results is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License.

# agora-results  is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with agora-results.  If not, see <http://www.gnu.org/licenses/>.

import unittest
from agora_results.utils import file_helpers
import test.desborda_test
import os
import sys
import subprocess
import copy

tally_config = [
    [
        "agora_results.pipes.results.do_tallies",
        {
            "ignore_invalid_votes": True
        }
    ],
    [
        "agora_results.pipes.desborda.podemos_desborda",
        {
            "women_names": [
            ]
        }
    ]
]

class TestDesBorda(unittest.TestCase):

    def do_test(self, test_data=None):
        if test_data is None:
            return
        print("\nTest name: %s" % test_data["name"])
        agora_results_bin_path = "python3 agora-results"
        tally_path = test.desborda_test.create_desborda_test(test_data)
        try:
            tally_targz_path = os.path.join(tally_path, "tally.tar.gz")
            config_results_path = os.path.join(tally_path, "12345.config.results.json")
            results_path = os.path.join(tally_path, "12345.results.json")
            cmd = "%s -t %s -c %s -s -o json" % (
                agora_results_bin_path,
                tally_targz_path,
                config_results_path)
            with open(results_path, mode='w', encoding="utf-8", errors='strict') as f:
                print(cmd)
                subprocess.check_call(cmd, stdout=f, stderr=sys.stderr, shell=True)
            results = test.desborda_test.create_simple_results(results_path)
            file_helpers.write_file(os.path.join(tally_path, "output"), results)
            shouldresults = test_data["output"]
            check_results = test.desborda_test.check_results(results, shouldresults)
            self.assertTrue(check_results)
        except:
            # remove the temp test folder if there's an error
            file_helpers.remove_tree(tally_path)
            raise
        # remove the temp test folder also in a successful test
        file_helpers.remove_tree(tally_path)

    def test_all(self):
        desborda_tests_path = os.path.join("test", "desborda_tests")
        test_files = [ os.path.join(desborda_tests_path, f) for f in os.listdir(desborda_tests_path) if os.path.isfile(os.path.join(desborda_tests_path, f)) ]
        for testfile_path in test_files:
            data = test.desborda_test.read_testfile(testfile_path)
            data["config"] = copy.deepcopy(tally_config)
            self.do_test(test_data=data)

if __name__ == '__main__':
  unittest.main()