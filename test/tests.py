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

import unittest
from unittest.mock import patch
import json
from tally_pipes.utils import file_helpers
from tally_pipes.main import main, VERSION
import test.desborda_test
import os
import sys
import copy
import time
import random
import re

class Capturing:
    def __init__(self, *args, **kwargs):
        self.file_obj = open(*args, **kwargs)

    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self.file_obj
        return self.file_obj

    def __exit__(self, *args, **kwargs):
        self.file_obj.close()
        sys.stdout = self._stdout


class MockArgs:
    def __init__(self, options):
        self.options = options

    def __getattr__(self, key):
        try:
            return self.options[key]
        except:
            return self.default(key)

    def default(self, key):
        if key == 'tally':
            return []
        if key == 'election_config':
            return []
        if key == 'output_format':
            return 'json'

        return None


tally_config_desborda1 = dict(
    version=VERSION,
    pipes=[
        dict(type="tally_pipes.pipes.results.do_tallies", params={}),
        dict(
            type="tally_pipes.pipes.desborda.podemos_desborda",
            params={
                "women_names": []
            }
        )
    ]
)

tally_config_desborda2 = dict(
    version=VERSION,
    pipes=[
        dict(type="tally_pipes.pipes.results.do_tallies", params={}),
        dict(
            type="tally_pipes.pipes.desborda2.podemos_desborda2",
            params={
                "women_names": [
                ]
            }
        )
    ]
)

tally_config_desborda3 = dict(
    version=VERSION,
    pipes=[
        dict(type="tally_pipes.pipes.results.do_tallies", params={}),
        dict(
            type="tally_pipes.pipes.desborda3.podemos_desborda3",
            params={
                "women_names": []
            }
        )
    ]
)

tally_config_borda = dict(
    version=VERSION,
    pipes=[
        dict(type="tally_pipes.pipes.results.do_tallies", params={}),
        dict(
            type="tally_pipes.pipes.withdraw_candidates.withdraw_candidates",
            params={
                "questions": [
                    {
                        "question_index": 0,
                        "policy": "minimum-ballots-percent",
                        "min_percent": 40.05
                    }
                ]
            }
        ),
        dict(type="tally_pipes.pipes.sort.sort_non_iterative", params={})
    ]
)

tally_config_cumulative = dict(
    version=VERSION,
    pipes=[
        dict(type="tally_pipes.pipes.results.do_tallies", params={}),
    ]
)

def check_ballots(test_data, tally_results_dir_path, question_index):
    if len(test_data['output_ballots_csv']) > 0:
        # import pdb; pdb.set_trace()
        ballots_csv = file_helpers.read_file(
            os.path.join(tally_results_dir_path, 'ballots.csv')
        )
        check_ballots_csv = test.desborda_test.check_ballots(
            ballots_csv,
            test_data['output_ballots_csv']
        )
        if not check_ballots_csv:
            print("question index: %i\n" % question_index)
            print("ballots_csv:\n" + ballots_csv)
            print("what it should be:\n" + test_data['output_ballots_csv'])
        assert check_ballots_csv

    if len(test_data['output_ballots_json']) > 0:
        ballots_json = file_helpers.read_file(
            os.path.join(tally_results_dir_path, 'ballots.json')
        )
        check_ballots_json = test.desborda_test.check_ballots(
            ballots_json,
            test_data['output_ballots_json']
        )
        if not check_ballots_json:
            print("question index: %i\n" % question_index)
            print("ballots_json:\n" + ballots_json)
            print("what it should be:\n" + test_data['output_ballots_json'])
        assert check_ballots_json

class TestPluralityTallySheets(unittest.TestCase):
    def do_test(self, test_data=None, num_questions=1, women_in_urls=False):
        if test_data is None:
            return
        print("\nTest name: %s" % test_data["name"])
        tally_pipes_bin_path = "python3 tally-pipes"
        tally_path = test.desborda_test.create_desborda_test(test_data,
            tally_type = "plurality-at-large",
            num_questions = num_questions,
            women_in_urls = women_in_urls)
        try:
            tally_targz_path = os.path.join(tally_path, "tally.tar.gz")
            config_results_path = os.path.join(tally_path, "12345.config.results.json")
            pipes_whitelist = os.path.join("test", "pipes-whitelist.txt")
            results_path = os.path.join(tally_path, "12345.results.json")
            cmd = "%s -t %s -c %s -p %s -s -o json" % (
                tally_pipes_bin_path,
                tally_targz_path,
                config_results_path,
                pipes_whitelist)

            args = MockArgs({
                "tally": [tally_targz_path],
                "config": config_results_path,
                "pipes_whitelist": pipes_whitelist,
                "stdout": True,
                "output_format": "json",
            })
            print(cmd)
            with Capturing(results_path, mode='w', encoding="utf-8", errors='strict') as f:
                main(args)

            for question_index in range(0, num_questions):
                results = test.desborda_test.create_simple_results(
                    results_path,
                    question_index=question_index)

                output_name = "output_%i" % question_index
                file_helpers.write_file(os.path.join(tally_path, output_name), results)
                shouldresults = test_data["output"]
                check_results = test.desborda_test.check_results(results, shouldresults)

                if not check_results:
                    print("question index: %i\n" % question_index)
                    print("results:\n" + results)
                    print("shouldresults:\n" + shouldresults)
                self.assertTrue(check_results)

                # check ballots output
                check_ballots(test_data, tally_path, question_index)
        finally:
            # remove the temp test folder also in a successful test
            file_helpers.remove_tree(tally_path)

    def test_all(self):
        borda_tests_path = os.path.join("test", "plurality_tally_sheets")
        # only use tests that end with a number (ie "test_5" )
        test_files = [
          os.path.join(borda_tests_path, f)
          for f in os.listdir(borda_tests_path)
          if os.path.isfile(os.path.join(borda_tests_path, f)) and
          re.match("^test_([0-9]*)$", f) is not None]
        for testfile_path in test_files:
            data = test.desborda_test.read_testfile(testfile_path)
            self.do_test(test_data=data)

class TestBorda(unittest.TestCase):
    def do_test(self, test_data=None, num_questions=1, women_in_urls=False):
        if test_data is None:
            return
        print("\nTest name: %s" % test_data["name"])
        tally_pipes_bin_path = "python3 tally-pipes"
        tally_path = test.desborda_test.create_desborda_test(test_data,
            tally_type = "borda",
            num_questions = num_questions,
            women_in_urls = women_in_urls
        )
        try:
            tally_targz_path = os.path.join(tally_path, "tally.tar.gz")
            config_results_path = os.path.join(tally_path, "12345.config.results.json")
            results_path = os.path.join(tally_path, "12345.results.json")
            tally_results_dir_path = os.path.join(tally_path, 'results-1')
            os.mkdir(tally_results_dir_path)
            cmd = "%s -t %s -c %s -x %s -eid 12345 -s -o json" % (
                tally_pipes_bin_path,
                tally_targz_path,
                config_results_path,
                tally_path
            )

            args = MockArgs({
                "tally": [tally_targz_path],
                "config": config_results_path,
                "tar": tally_path,
                "election_id": 12345,
                "stdout": True,
                "output_format": "json",
            })
            print(cmd)
            with Capturing(results_path, mode='w', encoding="utf-8", errors='strict') as f:
                main(args)

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

                # check ballots output
                check_ballots(test_data, tally_results_dir_path, question_index)
        finally:
            # remove the temp test folder if there's an error
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
            data["results_config"] = copy.deepcopy(tally_config_borda)
            self.do_test(test_data=data)

    def test_ties(self):
        testfile_path = os.path.join("test", "borda_tests", "test_ties")
        # we test draws 20 times to test the stability of the ties
        for i in range(0, 20):
            data = test.desborda_test.read_testfile(testfile_path)
            data["results_config"] = copy.deepcopy(tally_config_borda)
            self.do_test(test_data=data)


class TestDesBorda4(unittest.TestCase):
    def do_test(self, test_data=None, num_questions=1, women_in_urls=True):
        if test_data is None:
            return
        print("\nTest name: %s" % test_data["name"])
        tally_pipes_bin_path = "python3 tally-pipes"
        tally_path = test.desborda_test.create_desborda_test(test_data,
            tally_type = "desborda2",
            num_questions = num_questions,
            women_in_urls = women_in_urls)
        try:
            tally_targz_path = os.path.join(tally_path, "tally.tar.gz")
            config_results_path = os.path.join(tally_path, "12345.config.results.json")
            pipes_whitelist = os.path.join("test", "pipes-whitelist.txt")
            results_path = os.path.join(tally_path, "12345.results.json")
            cmd = "%s -t %s -c %s -p %s -s -o json" % (
                tally_pipes_bin_path,
                tally_targz_path,
                config_results_path,
                pipes_whitelist)

            args = MockArgs({
                "tally": [tally_targz_path],
                "config": config_results_path,
                "pipes_whitelist": pipes_whitelist,
                "stdout": True,
                "output_format": "json",
            })
            print(cmd)
            with Capturing(results_path, mode='w', encoding="utf-8", errors='strict') as f:
                main(args)

            shouldresults = test_data["output"].split('###\n')
            for question_index in range(0, num_questions+1):
                results = test.desborda_test.create_simple_results(results_path, question_index=question_index)
                output_name = "output_%i" % question_index
                file_helpers.write_file(os.path.join(tally_path, output_name), results)
                check_results = test.desborda_test.check_ordered_results(
                    results, shouldresults[question_index])
                if not check_results:
                    print("question index: %i\n" % question_index)
                    print("results:\n" + results)
                    print("shouldresults:\n" + shouldresults[question_index])
                    print("config:\n" + json.dumps(test_data["results_config"], indent=4))
                self.assertTrue(check_results)

                # check ballots output
                check_ballots(test_data, tally_path, question_index)
        finally:
            # remove the temp test folder if there's an error
            file_helpers.remove_tree(tally_path)

    def test_all(self):
        desborda_tests_path = os.path.join("test", "desborda4_tests")
        # only use tests that end with a number (ie "test_5" )
        test_files = [
          os.path.join(desborda_tests_path, f)
          for f in os.listdir(desborda_tests_path)
          if os.path.isfile(os.path.join(desborda_tests_path, f)) and
          re.match("^test_([0-9]*)$", f) is not None]
        for testfile_path in test_files:
            data = test.desborda_test.read_testfile(testfile_path)
            self.do_test(test_data=data)

class TestDesBorda3(unittest.TestCase):
    def do_test(self, test_data=None, num_questions=1, women_in_urls=False):
        if test_data is None:
            return
        print("\nTest name: %s" % test_data["name"])
        tally_pipes_bin_path = "python3 tally-pipes"
        tally_path = test.desborda_test.create_desborda_test(test_data,
            tally_type = "desborda3",
            num_questions = num_questions,
            women_in_urls = women_in_urls)
        try:
            tally_targz_path = os.path.join(tally_path, "tally.tar.gz")
            config_results_path = os.path.join(tally_path, "12345.config.results.json")
            pipes_whitelist = os.path.join("test", "pipes-whitelist.txt")
            results_path = os.path.join(tally_path, "12345.results.json")
            cmd = "%s -t %s -c %s -p %s -s -o json" % (
                tally_pipes_bin_path,
                tally_targz_path,
                config_results_path,
                pipes_whitelist)

            args = MockArgs({
                "tally": [tally_targz_path],
                "config": config_results_path,
                "pipes_whitelist": pipes_whitelist,
                "election_id": 12345,
                "stdout": True,
                "output_format": "json",
            })
            print(cmd)
            with Capturing(results_path, mode='w', encoding="utf-8", errors='strict') as f:
                main(args)

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

                # check ballots output
                check_ballots(test_data, tally_path, question_index)

        finally:
            # remove the temp test folder if there's an error
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
            data["results_config"] = copy.deepcopy(tally_config_desborda3)
            self.do_test(test_data=data)

    def test_ties(self):
        testfile_path = os.path.join("test", "desborda3_tests", "test_ties")
        # we test draws 20 times to test the stability of the ties
        for i in range(0, 20):
            data = test.desborda_test.read_testfile(testfile_path)
            data["results_config"] = copy.deepcopy(tally_config_desborda3)
            self.do_test(test_data=data)

    def test_multi_women(self):
        testfile_path = os.path.join("test", "desborda3_tests", "test_multi_women")
        data = test.desborda_test.read_testfile(testfile_path)
        data["results_config"] = copy.deepcopy(tally_config_desborda3)
        self.do_test(test_data=data, num_questions=3, women_in_urls=True)

class TestDesBorda2(unittest.TestCase):
    def do_test(self, test_data=None, num_questions=1, women_in_urls=False):
        if test_data is None:
            return
        print("\nTest name: %s" % test_data["name"])
        tally_pipes_bin_path = "python3 tally-pipes"
        tally_path = test.desborda_test.create_desborda_test(test_data,
            tally_type = "desborda2",
            num_questions = num_questions,
            women_in_urls = women_in_urls)
        try:
            tally_targz_path = os.path.join(tally_path, "tally.tar.gz")
            config_results_path = os.path.join(tally_path, "12345.config.results.json")
            pipes_whitelist = os.path.join("test", "pipes-whitelist.txt")
            results_path = os.path.join(tally_path, "12345.results.json")
            cmd = "%s -t %s -c %s -p %s -s -o json" % (
                tally_pipes_bin_path,
                tally_targz_path,
                config_results_path,
                pipes_whitelist)

            args = MockArgs({
                "tally": [tally_targz_path],
                "config": config_results_path,
                "pipes_whitelist": pipes_whitelist,
                "stdout": True,
                "output_format": "json",
            })
            print(cmd)
            with Capturing(results_path, mode='w', encoding="utf-8", errors='strict') as f:
                main(args)

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

                # check ballots output
                check_ballots(test_data, tally_path, question_index)
        finally:
            # remove the temp test folder if there's an error
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
            data["results_config"] = copy.deepcopy(tally_config_desborda2)
            self.do_test(test_data=data)

    def test_ties(self):
        testfile_path = os.path.join("test", "desborda2_tests", "test_ties")
        # we test draws 20 times to test the stability of the ties
        for i in range(0, 20):
            data = test.desborda_test.read_testfile(testfile_path)
            data["results_config"] = copy.deepcopy(tally_config_desborda2)
            self.do_test(test_data=data)

    def test_multi_women(self):
        testfile_path = os.path.join("test", "desborda2_tests", "test_multi_women")
        data = test.desborda_test.read_testfile(testfile_path)
        data["results_config"] = copy.deepcopy(tally_config_desborda2)
        self.do_test(test_data=data, num_questions=3, women_in_urls=True)

class TestDesBorda(unittest.TestCase):

    def do_test(self, test_data=None):
        if test_data is None:
            return
        print("\nTest name: %s" % test_data["name"])
        tally_pipes_bin_path = "python3 tally-pipes"
        tally_path = test.desborda_test.create_desborda_test(test_data)
        try:
            tally_targz_path = os.path.join(tally_path, "tally.tar.gz")
            config_results_path = os.path.join(tally_path, "12345.config.results.json")
            pipes_whitelist = os.path.join("test", "pipes-whitelist.txt")
            results_path = os.path.join(tally_path, "12345.results.json")
            cmd = "%s -t %s -c %s -p %s -s -o json" % (
                tally_pipes_bin_path,
                tally_targz_path,
                config_results_path,
                pipes_whitelist)

            args = MockArgs({
                "tally": [tally_targz_path],
                "config": config_results_path,
                "pipes_whitelist": pipes_whitelist,
                "stdout": True,
                "output_format": "json",
            })
            print(cmd)
            with Capturing(results_path, mode='w', encoding="utf-8", errors='strict') as f:
                main(args)

            results = test.desborda_test.create_simple_results(results_path)
            file_helpers.write_file(os.path.join(tally_path, "output"), results)
            shouldresults = test_data["output"]
            check_results = test.desborda_test.check_results(results, shouldresults)
            if not check_results:
                print("results:\n" + results)
                print("shouldresults:\n" + shouldresults)
                import pdb; pdb.set_trace()
            self.assertTrue(check_results)

            # check ballots output
            check_ballots(test_data, tally_path, question_index=0)
        finally:
            # remove the temp test folder if there's an error
            file_helpers.remove_tree(tally_path)

    def test_all(self):
        desborda_tests_path = os.path.join("test", "desborda_tests")
        test_files = [
            os.path.join(desborda_tests_path, f) 
            for f in os.listdir(desborda_tests_path) 
            if os.path.isfile(os.path.join(desborda_tests_path, f)) 
        ]
        for testfile_path in test_files:
            data = test.desborda_test.read_testfile(testfile_path)
            data["results_config"] = copy.deepcopy(tally_config_desborda1)
            self.do_test(test_data=data)

    def _test_100k_votes_same(self):
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
            "config": copy.deepcopy(tally_config_desborda1),
            "name": "test 100k votes. 95% to A, 5% to B. All ballots for each team are the same"
        }
        # do tally
        self.do_test(test_data=data)
        end_time = time.time()
        print("test_100k_votes_same elapsed time: %f secs" % (end_time - start_time))

    def _test_100k_votes_rand(self):
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
            "config": copy.deepcopy(tally_config_desborda1),
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

class TestBallotOutput(unittest.TestCase):
    def do_test(
        self, 
        testfile_path, 
        num_questions=1, 
        women_in_urls=False, 
        tally_type="borda",
        tally_config=tally_config_borda
    ):
        test_data = test.desborda_test.read_testfile(testfile_path)
        test_data["results_config"] = copy.deepcopy(tally_config)

        print(
            "\nTest file path: %s\nTest name: %s" % (
                testfile_path,
                test_data["name"]
            )
        )

        tally_path = test.desborda_test.create_desborda_test(test_data,
            tally_type = tally_type,
            num_questions = num_questions,
            women_in_urls = women_in_urls
        )

        try:
            tally_targz_path = os.path.join(tally_path, "tally.tar.gz")
            config_results_path = os.path.join(tally_path, "12345.config.results.json")
            results_path = os.path.join(tally_path, "12345.results.json")
            tally_results_dir_path = os.path.join(tally_path, 'results-1')
            os.mkdir(tally_results_dir_path)
            cmd = "tally-pipes -t %s -c %s -x %s -eid 12345 -s -o json" % (
                tally_targz_path,
                config_results_path,
                tally_path
            )

            args = MockArgs({
                "tally": [tally_targz_path],
                "config": config_results_path,
                "tar": tally_path,
                "election_id": 12345,
                "stdout": True,
                "output_format": "json",
            })
            print(cmd)
            with Capturing(results_path, mode='w', encoding="utf-8", errors='strict') as f:
                main(args)

            for question_index in range(0, num_questions):
                results = test.desborda_test.create_simple_results(
                    results_path,
                    question_index=question_index)

                output_name = "output_%i" % question_index
                file_helpers.write_file(os.path.join(tally_path, output_name), results)
                shouldresults = test_data["output"]
                check_results = test.desborda_test.check_results(results, shouldresults)

                if not check_results:
                    print("question index: %i\n" % question_index)
                    print("results:\n" + results)
                    print("shouldresults:\n" + shouldresults)
                self.assertTrue(check_results)

                # check ballots output
                check_ballots(test_data, tally_results_dir_path, question_index)
        finally:
            file_helpers.remove_tree(tally_path)

    def test_output_borda(self):
        testfile_path = os.path.join("test", "output_tests", "test_output_1")
        self.do_test(testfile_path, women_in_urls=True)

    def test_output_plurality(self):
        testfile_path = os.path.join("test", "output_tests", "test_output_2")
        self.do_test(testfile_path, tally_type="plurality-at-large", women_in_urls=True)

    def test_output_plurality2(self):
        testfile_path = os.path.join("test", "output_tests", "test_output_3")
        self.do_test(testfile_path, tally_type="plurality-at-large", women_in_urls=True)


class TestCumulative(unittest.TestCase):
    def do_test(
        self,
        test_data=None,
        num_questions=1,
        women_in_urls=False,
        checks=3
    ):
        if test_data is None:
            return

        print("\nTest name: %s" % test_data["name"])
        tally_pipes_bin_path = "python3 tally-pipes"
        tally_path = test.desborda_test.create_desborda_test(
            test_data,
            extra_options=dict(cumulative_number_of_checkboxes=checks),
            tally_type="cumulative",
            num_questions=num_questions,
            women_in_urls=women_in_urls
        )
        try:
            tally_targz_path = os.path.join(tally_path, "tally.tar.gz")
            config_results_path = os.path.join(tally_path, "12345.config.results.json")
            pipes_whitelist = os.path.join("test", "pipes-whitelist.txt")
            results_path = os.path.join(tally_path, "12345.results.json")
            tally_results_dir_path = os.path.join(tally_path, 'results-1')
            os.mkdir(tally_results_dir_path)
            cmd = "%s -t %s -c %s -x %s -p %s -eid 12345 -s -o json" % (
                tally_pipes_bin_path,
                tally_targz_path,
                config_results_path,
                tally_path,
                pipes_whitelist
            )

            args = MockArgs(
                dict(
                    tally=[tally_targz_path],
                    config=config_results_path,
                    tar=tally_path,
                    election_id=12345,
                    pipes_whitelist=pipes_whitelist,
                    stdout=True,
                    output_format="json",
                )
            )
            print(cmd)
            with Capturing(
                results_path,
                mode='w',
                encoding="utf-8",
                errors='strict'
            ) as f:
                main(args)

            for question_index in range(0, num_questions):
                results = test.desborda_test.create_simple_results(
                    results_path,
                    question_index=question_index
                )

                output_name = "output_%i" % question_index
                file_helpers.write_file(
                    os.path.join(tally_path, output_name),
                    results
                )
                shouldresults = test_data["output"]
                check_results = test.desborda_test.check_results(
                    results,
                    shouldresults
                )

                if not check_results:
                    print("question index: %i\n" % question_index)
                    print("results:\n" + results)
                    print("shouldresults:\n" + shouldresults)
                self.assertTrue(check_results)

                # check ballots output
                check_ballots(test_data, tally_results_dir_path, question_index)
        finally:
            # remove the temp test folder also in a successful test
            file_helpers.remove_tree(tally_path)

    def test_all(self):
        borda_tests_path = os.path.join("test", "cumulative_tests")
        test_files = [
            os.path.join(borda_tests_path, f)
            for f in os.listdir(borda_tests_path)
            if os.path.isfile(os.path.join(borda_tests_path, f)) and
            re.match("^test_(.*)$", f) is not None
        ]
        
        for testfile_path in test_files:
            data = test.desborda_test.read_testfile(testfile_path)
            data["results_config"] = copy.deepcopy(tally_config_cumulative)
            self.do_test(test_data=data)

if __name__ == '__main__':
  unittest.main()
