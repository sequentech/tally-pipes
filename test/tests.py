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
import test.desborda_test_data
import os
import sys
import subprocess

class TestStringMethods(unittest.TestCase):
    def do_test(self, test_data):
        if test_data is None:
            pass
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
            self.assertEqual(results, shouldresults)
        except:
            # remove the temp test folder if there's an error
            file_helpers.remove_tree(tally_path)
            raise
        # remove the temp test folder also in a successful test
        file_helpers.remove_tree(tally_path)

    def test_desborda_1(self):
        self.do_test(test.desborda_test_data.test_desborda_1)

if __name__ == '__main__':
  unittest.main()