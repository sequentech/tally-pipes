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

import string
import re
import copy
import json
import os
from os import urandom
from agora_results.utils import file_helpers
import tempfile
import uuid
import tarfile

def remove_spaces(in_str):
    return re.sub(r"[ \t\r\f\v]*", "", in_str)

def has_input_format(in_str):
     # example: "A1f, B2m \nB3f"
     m = re.fullmatch(r"((\s*[A-Z][0-9]+[fm]\s*,)*\s*[A-Z][0-9]+[fm]\s*\n)*(\s*[A-Z][0-9]+[fm]\s*,)*\s*[A-Z][0-9]+[fm]\s*\n?", in_str)
     return m is not None

def has_output_format(out_str):
     # example: "A1f, 1,  3\n B33m, 4"
     m = re.fullmatch(r"(\s*[A-Z][0-9]+[fm]\s*,\s*[0-9]+\s*\n)*\s*[A-Z][0-9]+[fm]\s*,\s*[0-9]+\s*\n?", out_str)
     return m is not None

def encode_ballot(ballot, indexed_candidates):
    max_num = len(indexed_candidates) + 2
    digit_num_per_candidate = len(str(max_num))
    encoded = ""
    for candidate in ballot:
        enc_cand = str(indexed_candidates[candidate] + 1)
        enc_cand = '0' * (digit_num_per_candidate - len(enc_cand)) + enc_cand
        encoded = encoded + enc_cand
    # note, only will work correctly on python 3
    return str(int(encoded) + 1)

# generate password with length number of characters
def gen_pass(length):
  alphabet = string.ascii_letters + string.digits
  return ''.join(alphabet[c % len(alphabet)] for c in urandom(length))

def make_simple_targz(output_filename, source_dir):
    with tarfile.open(output_filename, "x:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename("."))

def create_temp_folder():
    temp_folder = tempfile.mkdtemp()
    print("temp folder created at: %s" % temp_folder)
    return temp_folder

def create_simple_results(results_path, question_index = 0):
    results_json = json.loads(file_helpers.read_file(results_path))
    answers = results_json["questions"][question_index]["answers"]
    indexed_winners = [ index
        for index, answer in enumerate(answers)
        if answer["winner_position"] is not None
     ]
    indexed_winners = sorted(
        indexed_winners,
        key = lambda j: answers[j]["winner_position"])
    text = ""
    for index in indexed_winners:
        winner = answers[index]
        text += "%s, %i\n" %(winner["text"], winner["total_count"])
    return text

def check_results(text_a, text_b):
    '''
    Check results so that the order of the winners doesn't matter
    '''
    results_a = set( tuple(re.split(r",", line)) for line in remove_spaces(text_a).splitlines() )
    results_b = set( tuple(re.split(r",", line)) for line in remove_spaces(text_b).splitlines() )
    ret = (results_b == results_a)
    return ret

def read_testfile(testfile_path):
    file_raw_text = file_helpers.read_file(testfile_path)
    file_lines = file_raw_text.splitlines(keepends = True)
    ballots = ""
    results = ""
    name = ""
    states = ["ballots_first_line", "reading_ballots", "results_first_line", "reading_results"]
    state = "ballots_first_line"
    for line in file_lines:
        if "ballots_first_line" == state:
            if "\n" == line:
                continue
            else:
                name = line
                state = "reading_ballots"
        elif "reading_ballots" == state:
            if "\n" == line:
                state = "results_first_line"
            else:
                ballots += line
        elif "results_first_line" == state:
            if "\n" == line:
                continue
            else:
                state = "reading_results"
        elif "reading_results" == state:
            if "\n" == line:
                break
            else:
                results += line
    return { "input": ballots, "output": results, "name": name }

def create_desborda_test(test_data, tally_type = "desborda", num_questions=1, women_in_urls=False):
    if not has_input_format(test_data["input"]):
        raise Exception("Error: test data input with format errors")
    if not has_output_format(test_data["output"]):
        raise Exception("Error: test data output with format errors")

    # test_struct
    ballots = [re.split(r",", line) for line in remove_spaces(test_data["input"]).splitlines()]
    results = [re.split(r",", line) for line in remove_spaces(test_data["output"]).splitlines()]
    num_winners = len(results)
    teams = {}
    all_candidates = []
    women_names = []
    max_num = 0
    for ballot in ballots:
        len_ballot = len(ballot)
        if len_ballot > max_num:
            max_num = len_ballot
        for candidate in ballot:
            team = candidate[:1]
            female = "f" is candidate[-1]
            if team not in teams:
                teams[team] = []
            else:
                other_sex = candidate[:-1] + ("m" if female else "f")
                if other_sex in teams[team]:
                    raise Exception("Error: candidate %s repeated: %s" % (candidate, other_sex))

            if candidate not in teams[team]:
                if female:
                    women_names.append(candidate)
                teams[team].append(candidate)
                all_candidates.append(candidate)

    if len(all_candidates) != len(set(all_candidates)):
        raise Exception("Error: 'all_candidates' might have duplicate values")

    set_all = set(all_candidates)
    set_results = set([x[0] for x in results])
    if len(set_results) is not len(set_all & set_results):
        raise Exception("Error: there are some answers in the results that are not candidates: %s " % str(set_results - set_all))

    question = {
        "answer_total_votes_percentage": "over-total-valid-votes",
        "answers": [],
        "description": "Desborda question",
        "layout": "simple",
        "max": max_num,
        "min": 0,
        "num_winners": num_winners,
        "randomize_answer_order": True,
        "tally_type": tally_type,
        "title": "Desborda question"
    }
    cand_index = 0
    indexed_candidates = {}
    for team_name in teams:
        team_candidates = teams[team_name]
        for candidate in team_candidates:
            answer = {
                "category": team_name,
                "details": candidate,
                "id": cand_index,
                "text": candidate,
                "urls": []
            }
            indexed_candidates[candidate] = cand_index
            if women_in_urls:
                candidate_is_woman = candidate in women_names
                gender_url = {
                  "title": "Gender",
                  "url": ("https://agoravoting.com/api/gender/M" \
                      if candidate_is_woman \
                      else "https://agoravoting.com/api/gender/H")
                }
                answer["urls"].append(gender_url)
            question["answers"].append(answer)
            cand_index += 1

    questions_json = [question] * num_questions
    config = test_data["config"]
    for config_el in config:
        if "women_names" in config_el[1]:
            if not women_in_urls:
                config_el[1]["women_names"] = women_names
            else:
                config_el[1]["women_names"] = None

    # encode ballots in plaintexts_json format
    plaintexts_json = ""
    counter = 0
    for ballot in ballots:
        counter += 1
        if counter % 1000 == 0:
            print("%i votes encoded" % counter)
        encoded_ballot = encode_ballot(ballot, indexed_candidates)
        plaintexts_json = plaintexts_json + '"' + encoded_ballot + '"\n'

    # create folder
    desborda_test_path = create_temp_folder()
    try:
        targz_folder = os.path.join(desborda_test_path, "tally")
        os.mkdir(targz_folder)
        for question_index in range(0, num_questions):
            plaintexts_folder = os.path.join(targz_folder,
                "%i-%s" % (question_index, str(uuid.uuid4()) ) )
            os.mkdir(plaintexts_folder)
            file_helpers.write_file(os.path.join(plaintexts_folder, "plaintexts_json"), plaintexts_json)
        file_helpers.write_file(os.path.join(targz_folder, "questions_json"), file_helpers.serialize(questions_json))
        make_simple_targz(os.path.join(desborda_test_path, "tally.tar.gz"), targz_folder)
        file_helpers.write_file(os.path.join(desborda_test_path, "results_json"), test_data["output"])
        file_helpers.write_file(os.path.join(desborda_test_path, "12345.config.results.json"), file_helpers.serialize(config))
    except:
        file_helpers.remove_tree(desborda_test_path)
        raise
    return desborda_test_path
