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
import time
import random
import re

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

tally_config_desborda2 = [
    [
        "agora_results.pipes.results.do_tallies",
        {
            "ignore_invalid_votes": True
        }
    ],
    [
        "agora_results.pipes.desborda2.podemos_desborda2",
        {
            "women_names": [
            ]
        }
    ]
]

tally_config_desborda3 = [
    [
        "agora_results.pipes.results.do_tallies",
        {
            "ignore_invalid_votes": True
        }
    ],
    [
        "agora_results.pipes.desborda3.podemos_desborda3",
        {
            "women_names": [
            ]
        }
    ]
]

tally_config_borda = [
  [
    "agora_results.pipes.results.do_tallies",
    {
      "ignore_invalid_votes": True
    }
  ],
  [
    "agora_results.pipes.withdraw_candidates.withdraw_candidates",
    {
      "questions": [
        {
          "question_index": 0,
          "policy": "minimum-ballots-percent",
          "min_percent": 40.05
        }
      ]
    }
  ],
  [
    "agora_results.pipes.sort.sort_non_iterative",
    {
      "question_indexes": [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15
      ]
    }
  ]
]

class TestBorda(unittest.TestCase):
    def do_test(self, test_data=None, num_questions=1, women_in_urls=False):
        if test_data is None:
            return
        print("\nTest name: %s" % test_data["name"])
        agora_results_bin_path = "python3 agora-results"
        tally_path = test.desborda_test.create_desborda_test(test_data,
            tally_type = "borda",
            num_questions = num_questions,
            women_in_urls = women_in_urls)
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
            for question_index in range(0, num_questions):
                results = test.desborda_test.create_simple_results(results_path, question_index=question_index)
                output_name = "output_%i" % question_index
                file_helpers.write_file(os.path.join(tally_path, output_name), results)
                shouldresults = test_data["output"]
                check_results = test.desborda_test.check_results(results, shouldresults)
                if not check_results:
                    print("question index: %i\n" % question_index)
                    print("results:\n" + results)
                    print("shouldresults:\n" + shouldresults)
                self.assertTrue(check_results)
        except:
            # remove the temp test folder if there's an error
            file_helpers.remove_tree(tally_path)
            raise
        # remove the temp test folder also in a successful test
        file_helpers.remove_tree(tally_path)

    def test_all(self):
        borda_tests_path = os.path.join("test", "borda_tests")
        # only use tests that end with a number (ie "test_5" )
        test_files = [
          os.path.join(borda_tests_path, f) 
          for f in os.listdir(borda_tests_path) 
          if os.path.isfile(os.path.join(borda_tests_path, f)) and
          re.match("^test_([0-9]*)$", f) is not None]
        for testfile_path in test_files:
            data = test.desborda_test.read_testfile(testfile_path)
            data["config"] = copy.deepcopy(tally_config_borda)
            self.do_test(test_data=data)

    def test_ties(self):
        testfile_path = os.path.join("test", "borda_tests", "test_ties")
        # we test draws 20 times to test the stability of the ties
        for i in range(0, 20):
            data = test.desborda_test.read_testfile(testfile_path)
            data["config"] = copy.deepcopy(tally_config_borda)
            self.do_test(test_data=data)

class TestDesBorda3(unittest.TestCase):
    def do_test(self, test_data=None, num_questions=1, women_in_urls=False):
        if test_data is None:
            return
        print("\nTest name: %s" % test_data["name"])
        agora_results_bin_path = "python3 agora-results"
        tally_path = test.desborda_test.create_desborda_test(test_data,
            tally_type = "desborda3",
            num_questions = num_questions,
            women_in_urls = women_in_urls)
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
            for question_index in range(0, num_questions):
                results = test.desborda_test.create_simple_results(results_path, question_index=question_index)
                output_name = "output_%i" % question_index
                file_helpers.write_file(os.path.join(tally_path, output_name), results)
                shouldresults = test_data["output"]
                check_results = test.desborda_test.check_results(results, shouldresults)
                if not check_results:
                    print("question index: %i\n" % question_index)
                    print("results:\n" + results)
                    print("shouldresults:\n" + shouldresults)
                self.assertTrue(check_results)
        except:
            # remove the temp test folder if there's an error
            file_helpers.remove_tree(tally_path)
            raise
        # remove the temp test folder also in a successful test
        file_helpers.remove_tree(tally_path)

    def test_all(self):
        desborda_tests_path = os.path.join("test", "desborda3_tests")
        # only use tests that end with a number (ie "test_5" )
        test_files = [
          os.path.join(desborda_tests_path, f) 
          for f in os.listdir(desborda_tests_path) 
          if os.path.isfile(os.path.join(desborda_tests_path, f)) and
          re.match("^test_([0-9]*)$", f) is not None]
        for testfile_path in test_files:
            data = test.desborda_test.read_testfile(testfile_path)
            data["config"] = copy.deepcopy(tally_config_desborda3)
            self.do_test(test_data=data)

    def test_ties(self):
        testfile_path = os.path.join("test", "desborda3_tests", "test_ties")
        # we test draws 20 times to test the stability of the ties
        for i in range(0, 20):
            data = test.desborda_test.read_testfile(testfile_path)
            data["config"] = copy.deepcopy(tally_config_desborda3)
            self.do_test(test_data=data)

    def test_multi_women(self):
        testfile_path = os.path.join("test", "desborda3_tests", "test_multi_women")
        data = test.desborda_test.read_testfile(testfile_path)
        data["config"] = copy.deepcopy(tally_config_desborda3)
        self.do_test(test_data=data, num_questions=3, women_in_urls=True)

class TestDesBorda2(unittest.TestCase):
    def do_test(self, test_data=None, num_questions=1, women_in_urls=False):
        if test_data is None:
            return
        print("\nTest name: %s" % test_data["name"])
        agora_results_bin_path = "python3 agora-results"
        tally_path = test.desborda_test.create_desborda_test(test_data,
            tally_type = "desborda2",
            num_questions = num_questions,
            women_in_urls = women_in_urls)
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
            for question_index in range(0, num_questions):
                results = test.desborda_test.create_simple_results(results_path, question_index=question_index)
                output_name = "output_%i" % question_index
                file_helpers.write_file(os.path.join(tally_path, output_name), results)
                shouldresults = test_data["output"]
                check_results = test.desborda_test.check_results(results, shouldresults)
                if not check_results:
                    print("question index: %i\n" % question_index)
                    print("results:\n" + results)
                    print("shouldresults:\n" + shouldresults)
                self.assertTrue(check_results)
        except:
            # remove the temp test folder if there's an error
            file_helpers.remove_tree(tally_path)
            raise
        # remove the temp test folder also in a successful test
        file_helpers.remove_tree(tally_path)

    def test_all(self):
        desborda_tests_path = os.path.join("test", "desborda2_tests")
        # only use tests that end with a number (ie "test_5" )
        test_files = [
          os.path.join(desborda_tests_path, f) 
          for f in os.listdir(desborda_tests_path) 
          if os.path.isfile(os.path.join(desborda_tests_path, f)) and
          re.match("^test_([0-9]*)$", f) is not None]
        for testfile_path in test_files:
            data = test.desborda_test.read_testfile(testfile_path)
            data["config"] = copy.deepcopy(tally_config_desborda2)
            self.do_test(test_data=data)

    def test_ties(self):
        testfile_path = os.path.join("test", "desborda2_tests", "test_ties")
        # we test draws 20 times to test the stability of the ties
        for i in range(0, 20):
            data = test.desborda_test.read_testfile(testfile_path)
            data["config"] = copy.deepcopy(tally_config_desborda2)
            self.do_test(test_data=data)

    def test_multi_women(self):
        testfile_path = os.path.join("test", "desborda2_tests", "test_multi_women")
        data = test.desborda_test.read_testfile(testfile_path)
        data["config"] = copy.deepcopy(tally_config_desborda2)
        self.do_test(test_data=data, num_questions=3, women_in_urls=True)

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

    def test_100k_votes_same(self):
        start_time = time.time()
        vote_a = "A1f,A2m,A3f,A4m,A5f,A6m,A7f,A8m,A9f,A10m,A11f,A12m,A13f,A14m,A15f,A16m,A17f,A18m,A19f,A20m,A21f,A22m,A23f,A24m,A25f,A26m,A27f,A28m,A29f,A30m,A31f,A32m,A33f,A34m,A35f,A36m,A37f,A38m,A39f,A40m,A41f,A42m,A43f,A44m,A45f,A46m,A47f,A48m,A49f,A50m,A51f,A52m,A53f,A54m,A55f,A56m,A57f,A58m,A59f,A60m,A61f,A62m\n"
        vote_b = "B1f,B2m,B3f,B4m,B5f,B6m,B7f,B8m,B9f,B10m,B11f,B12m,B13f,B14m,B15f,B16m,B17f,B18m,B19f,B20m,B21f,B22m,B23f,B24m,B25f,B26m,B27f,B28m,B29f,B30m,B31f,B32m,B33f,B34m,B35f,B36m,B37f,B38m,B39f,B40m,B41f,B42m,B43f,B44m,B45f,B46m,B47f,B48m,B49f,B50m,B51f,B52m,B53f,B54m,B55f,B56m,B57f,B58m,B59f,B60m,B61f,B62m\n"
        list_a = ["A1f","A2m","A3f","A4m","A5f","A6m","A7f","A8m","A9f","A10m","A11f","A12m","A13f","A14m","A15f","A16m","A17f","A18m","A19f","A20m","A21f","A22m","A23f","A24m","A25f","A26m","A27f","A28m","A29f","A30m","A31f","A32m","A33f","A34m","A35f","A36m","A37f","A38m","A39f","A40m","A41f","A42m","A43f","A44m","A45f","A46m","A47f","A48m","A49f","A50m","A51f","A52m","A53f","A54m","A55f","A56m","A57f","A58m","A59f","A60m"]
        print("creating 100k votes")
        total_votes = int(1e5)
        num_votes_a = int(total_votes * 0.95)
        num_votes_b = total_votes - num_votes_a
        ballots = vote_a * num_votes_a + vote_b * num_votes_b
        # create results
        results = "B1f, %i\nB2m, %i\n" % (80 * num_votes_b, 79 * num_votes_b)
        for index, el in enumerate(list_a):
            results += "%s, %i\n" % (el, ((80 - index) * num_votes_a) )
        data = {
            "input": ballots,
            "output": results,
            "config": copy.deepcopy(tally_config),
            "name": "test 100k votes. 95% to A, 5% to B. All ballots for each team are the same"
        }
        # do tally
        self.do_test(test_data=data)
        end_time = time.time()
        print("test_100k_votes_same elapsed time: %f secs" % (end_time - start_time))

    def test_100k_votes_rand(self):
        start_time = time.time()
        vote_a = "A1f,A2m,A3f,A4m,A5f,A6m,A7f,A8m,A9f,A10m,A11f,A12m,A13f,A14m,A15f,A16m,A17f,A18m,A19f,A20m,A21f,A22m,A23f,A24m,A25f,A26m,A27f,A28m,A29f,A30m,A31f,A32m,A33f,A34m,A35f,A36m,A37f,A38m,A39f,A40m,A41f,A42m,A43f,A44m,A45f,A46m,A47f,A48m,A49f,A50m,A51f,A52m,A53f,A54m,A55f,A56m,A57f,A58m,A59f,A60m,A61f,A62m\n"
        vote_b = "B1f,B2m,B3f,B4m,B5f,B6m,B7f,B8m,B9f,B10m,B11f,B12m,B13f,B14m,B15f,B16m,B17f,B18m,B19f,B20m,B21f,B22m,B23f,B24m,B25f,B26m,B27f,B28m,B29f,B30m,B31f,B32m,B33f,B34m,B35f,B36m,B37f,B38m,B39f,B40m,B41f,B42m,B43f,B44m,B45f,B46m,B47f,B48m,B49f,B50m,B51f,B52m,B53f,B54m,B55f,B56m,B57f,B58m,B59f,B60m,B61f,B62m\n"
        list_a = ["A1f","A2m","A3f","A4m","A5f","A6m","A7f","A8m","A9f","A10m","A11f","A12m","A13f","A14m","A15f","A16m","A17f","A18m","A19f","A20m","A21f","A22m","A23f","A24m","A25f","A26m","A27f","A28m","A29f","A30m","A31f","A32m","A33f","A34m","A35f","A36m","A37f","A38m","A39f","A40m","A41f","A42m","A43f","A44m","A45f","A46m","A47f","A48m","A49f","A50m","A51f","A52m","A53f","A54m","A55f","A56m","A57f","A58m","A59f","A60m","A61f","A62m"]
        list_a_counts = [0] * len(list_a)
        print("creating 100k votes")
        total_votes = int(1e5)
        num_votes_a = int(total_votes * 0.95)
        num_votes_b = total_votes - num_votes_a
        ballots = vote_b * num_votes_b
        bnum = 0
        base_vote = [a for a in range(62)]
        while bnum < num_votes_a:
            vote = copy.deepcopy(base_vote)
            random.shuffle(vote)
            line = ""
            for index, el in enumerate(vote):
                line += "%s," % list_a[el]
                list_a_counts[el] += (80 - index)
            ballots += line[:-1] + "\n"
            bnum += 1
        # create results
        results = "B1f, %i\nB2m, %i\n" % (80 * num_votes_b, 79 * num_votes_b)
        results_list_a = [(list_a[i], list_a_counts[i]) for i in base_vote]
        results_list_a_sorted = sorted(
            results_list_a,
            key = lambda x: x[1],
            reverse = True)
        winners_list_a = results_list_a_sorted[:-2]
        for el, votes in winners_list_a:
            results += "%s, %i\n" % (el, votes )
        data = {
            "input": ballots,
            "output": results,
            "config": copy.deepcopy(tally_config),
            "name": "test 100k votes. 95% to A, 5% to B. All ballots for each team are the same"
        }
        end_time = time.time()
        print("test_100k_votes_rand create ballots elapsed time: %f secs" % (end_time - start_time))
        start_time = time.time()
        self.do_test(test_data=data)
        end_time = time.time()
        print("test_100k_votes_rand tally elapsed time: %f secs" % (end_time - start_time))
        # do tally
        self.assertTrue(True)

if __name__ == '__main__':
  unittest.main()