#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# This file is part of tally-pipes.
# Copyright (C) 2017-2021  Sequent Tech Inc <legal@sequentech.io>

# tally-pipes is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License.

# tally-pipes  is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with tally-pipes.  If not, see <http://www.gnu.org/licenses/>.

import string
import re
import copy
import json
import os
from os import urandom
from tally_pipes.utils import file_helpers
from tally_pipes.main import main, VERSION
from tally_methods.ballot_codec.sequent_codec import NVotesCodec
import tempfile
import uuid
import tarfile

def remove_spaces(in_str):
    return re.sub(r"[ \t\r\f\v]*", "", in_str)

def has_input_format(in_str):
    # example: "A1f, B2m \nB3f"
    m = re.fullmatch(r"((\s*(<blank>|<null>|[A-Z][0-9]+[fm])\s*,)*\s*(<blank>|<null>|[A-Z][0-9]+[fm])\s*\n)*(\s*(<blank>|<null>|[A-Z][0-9]+[fm])\s*,)*\s*(<blank>|<null>|[A-Z][0-9]+[fm])\s*\n?", in_str)
    return m is not None

def has_output_format(out_str):
    # example: "A1f, 1,  3\n B33m, 4"
    m = re.fullmatch(r"(\s*[A-Z][0-9]+[fm]\s*,\s*[0-9]+\s*\n)*\s*[A-Z][0-9]+[fm]\s*,\s*[0-9]+\s*\n?", out_str)
    return m is not None

def encode_ballot(
    text_ballot, 
    question
):
    '''
    ballot encoder
    '''
    ballot_question = copy.deepcopy(question)
    normal_choices_dict = dict()
    write_in_choices_dict = dict()
    is_invalid_vote_flag = False
    for choice_index, text_choice in enumerate(text_ballot):
        if '#' in text_choice:
            answer_id, answer_text = text_choice.split('#')
            answer_id = int(answer_id)
        else:
            answer_id = None
            answer_text = text_choice
        if answer_id is None:
            if answer_text not in ['<blank>', '<null>']:
                if answer_text in normal_choices_dict:
                    normal_choices_dict[answer_text]['count'] += 1
                else:
                    normal_choices_dict[answer_text] = dict(
                        count=1,
                        choice_index=choice_index
                    )
            elif answer_text == '<null>':
                is_invalid_vote_flag = True
        else:
            if answer_id in write_in_choices_dict:
                write_in_choices_dict[answer_id]['count'] += 1
            else:
                write_in_choices_dict[answer_id] = dict(
                    count=1,
                    text=answer_text,
                    choice_index=choice_index
                )

    for answer_index, answer in enumerate(ballot_question['answers']):
        selected = -1
        if answer_index in write_in_choices_dict:
            answer['text'] = write_in_choices_dict[answer_index]['text']
            if question['tally_type'] == 'cumulative':
                selected = write_in_choices_dict[answer_index]['count'] - 1
            else:
                selected = write_in_choices_dict[answer_index]['choice_index']
        elif answer['text'] in normal_choices_dict:
            if question['tally_type'] == 'cumulative':
                selected = normal_choices_dict[answer['text']]['count'] - 1
            else:
                selected = normal_choices_dict[answer['text']]['choice_index']
        answer['selected'] = selected
    
    ballot_encoder = NVotesCodec(ballot_question)
    raw_ballot = ballot_encoder.encode_raw_ballot()
    # if it's an invalid ballot, set the invalid ballot flag
    if is_invalid_vote_flag:
        raw_ballot['choices'][0] = 1
    int_ballot = ballot_encoder.encode_to_int(raw_ballot)
    return str(int_ballot + 1)

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

def check_ballots(text_a, text_b):
    '''
    Check results so that the order of the lines doesn't matter
    '''
    ballots_a = set( line for line in remove_spaces(text_a).splitlines() )
    ballots_b = set( line for line in remove_spaces(text_b).splitlines() )
    ret = (ballots_b == ballots_a)
    return ret

def check_ordered_results(text_a, text_b):
    '''
    Check results so that the order of the winners does matter
    '''
    return text_a == text_b

def read_testfile(testfile_path):
    file_raw_text = file_helpers.read_file(testfile_path)
    file_lines = file_raw_text.splitlines(keepends = True)
    ballots = ""
    results = ""
    results_config = ""
    output_ballots_csv = ""
    output_ballots_json = ""
    questions_json = ""
    name = ""
    state = "reading_header"
    for line in file_lines:
        if state == 'reading_header':
            if line == '\n':
                continue
            elif line.startswith("Votes:"):
                name = line
                state = "reading_ballots"
            elif line.startswith("Results:"):
                state = "reading_results"
            elif line.startswith("Config results:"):
                state = "reading_results_config"
            elif line.startswith("Ballots CSV:"):
                state = "reading_ballots_csv"
            elif line.startswith("Ballots JSON:"):
                state = "reading_ballots_json"
            elif line.startswith("Questions JSON:"):
                state = "reading_questions_json"
        else:
            if line == '\n':
                state = 'reading_header'
            elif state == 'reading_ballots':
                ballots += line
            elif state == 'reading_results':
                results += line
            elif state == 'reading_results_config':
                results_config += line
            elif state == 'reading_ballots_csv':
                output_ballots_csv += line
            elif state == 'reading_ballots_json':
                output_ballots_json += line
            elif state == 'reading_questions_json':
                questions_json += line

    try:
        # replace version in tests
        results_config = re.sub(
            r"\"version\": \"[^\"]+\",", 
            f"\"version\": \"{VERSION}\",",
            results_config
        )
        return {
            "input": ballots,
            "output": results,
            "output_ballots_csv": output_ballots_csv,
            "output_ballots_json": output_ballots_json,
            "name": name,
            "results_config": json.loads(results_config) if len(results_config) > 0 else None,
            "questions_json": json.loads(questions_json) if len(questions_json) > 0 else None
        }
    except Exception as e:
        print("failing json loads for file %s" % testfile_path)
        raise e

def create_desborda_test(
    test_data,
    tally_type="desborda",
    num_questions=1,
    women_in_urls=False,
    extra_options=None,
):
    if (
        not has_input_format(test_data["input"]) and
        test_data['questions_json'] is None
    ):
        raise Exception("Error: test data input with format errors")
    if (
        not has_output_format(test_data["output"].split("###\n")[-1]) and
        test_data['questions_json'] is None
    ):
        raise Exception("Error: test data output with format errors")

    # test_struct
    ballots = [
        re.split(r",", line)
        for line in remove_spaces(test_data["input"]).splitlines()
    ]
    results = [
        re.split(r",", line)
        for line in remove_spaces(test_data["output"].split("###\n")[-1]).splitlines()
    ]
    if test_data['questions_json'] is None:
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
                if candidate in ['<blank>', '<null>']:
                    continue
                team = candidate[:1]
                female = "f" == candidate[-1]
                if team not in teams:
                    teams[team] = []
                else:
                    other_sex = candidate[:-1] + ("m" if female else "f")
                    if other_sex in teams[team]:
                        raise Exception(
                            "Error: candidate %s repeated: %s" % (
                                candidate,
                                other_sex
                            )
                        )

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
            raise Exception(
                "Error: there are some answers in the results that are not "\
                "candidates: %s " % str(set_results - set_all)
            )

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
            "title": "Desborda question",
        }

        if extra_options:
            question['extra_options'] = extra_options

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
                    "url": ("https://sequentech.io/api/gender/M" \
                        if candidate_is_woman \
                        else "https://sequentech.io/api/gender/H")
                    }
                    answer["urls"].append(gender_url)
                question["answers"].append(answer)
                cand_index += 1

        config = test_data["results_config"]
        questions_json = [question] * num_questions
        # set women names in the pipes
        for pipe in config['pipes']:
            if "women_names" in pipe['params']:
                if not women_in_urls:
                    pipe['params']["women_names"] = women_names
                else:
                    pipe['params']["women_names"] = None
    else:
        config = test_data["results_config"]
        questions_json = test_data['questions_json']
        question = questions_json[0]
        num_winners = questions_json[0]['num_winners']

    # encode ballots in plaintexts_json format
    plaintexts_json = ""
    counter = 0
    for ballot in ballots:
        counter += 1
        if counter % 1000 == 0:
            print("%i votes encoded" % counter)
        encoded_ballot = encode_ballot(
            text_ballot=ballot,
            question=question
        )
        plaintexts_json = plaintexts_json + '"' + encoded_ballot + '"\n'

    # create folder
    base_path = create_temp_folder()
    desborda_test_path = os.path.join(base_path, "12345")
    os.mkdir(desborda_test_path)

    try:
        targz_folder = os.path.join(desborda_test_path, "tally")
        os.mkdir(targz_folder)
        for question_index in range(0, num_questions):
            plaintexts_folder = os.path.join(targz_folder,
                "%i-%s" % (question_index, str(uuid.uuid4()) ) )
            os.mkdir(plaintexts_folder)
            file_helpers.write_file(
                os.path.join(plaintexts_folder, "plaintexts_json"),
                plaintexts_json
            )
        
        file_helpers.write_file(
            os.path.join(targz_folder, "questions_json"),
            file_helpers.serialize(
                test_data['questions_json']
                if test_data['questions_json'] is not None 
                else questions_json
            )
        )
        make_simple_targz(
            os.path.join(desborda_test_path, "tally.tar.gz"),
            targz_folder
        )
        file_helpers.write_file(
            os.path.join(desborda_test_path, "results_json"),
            test_data["output"]
        )
        file_helpers.write_file(
            os.path.join(desborda_test_path, "12345.config.results.json"),
            file_helpers.serialize(config)
        )
    except:
        file_helpers.remove_tree(base_path)
        raise
    return desborda_test_path
