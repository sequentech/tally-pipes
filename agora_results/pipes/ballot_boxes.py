# -*- coding:utf-8 -*-

# This file is part of agora-results.
# Copyright (C) 2014-2016  Agora Voting SL <agora@agoravoting.com>

# agora-results is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License.

# agora-results  is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with agora-results.  If not, see <http://www.gnu.org/licenses/>.

import re
import os
import json

def _initialize_question(question):
    '''
    Initialize question results to zero if any
    '''
    if 'winners' not in question:
        question['winners'] = []
    if 'totals' not in question:
        question['totals'] = dict(
            blank_votes=0,
            null_votes=0,
            valid_votes=0
        )
    for answer in question['answers']:
        if "total_count" not in answer:
            answer['total_count'] = 0

def _verify_tally_sheet(tally_sheet, tally_index):
    '''
    Verify that the tally sheets conform with the list of questions and answers
    of this election
    '''

    assert\
        'num_votes' in tally_sheet,\
        'sheet %d: no num_votes' % tally_index
    assert\
        isinstance(tally_sheet['num_votes'], int),\
        'sheet %d: num_votes is not an integer' % tally_index
    assert\
        tally_sheet['num_votes'] >= 0,\
          'sheet %d: num_votes is negative' % tally_index

    assert\
        'ballot_box_name' in tally_sheet,\
        'sheet %d: no ballot_box_name' % tally_index
    assert\
        isinstance(tally_sheet['ballot_box_name'], str),\
        'sheet %d: ballot_box_name is not an string' % tally_index

    assert\
      'questions' in tally_sheet,\
      'sheet %d: tally_sheet has no questions' % tally_index
    assert\
      isinstance(tally_sheet['questions'], list),\
      'sheet %d: tally_sheet questions is not a list' % tally_index

    for qindex, sheet_question in enumerate(tally_sheet['questions']):
        assert\
            'title' in sheet_question,\
            'sheet %d, question %d: no title' % (tally_index, qindex)
        assert\
            isinstance(sheet_question['title'], str),\
            'sheet %d, question %d: title is not a string' % (tally_index, qindex)

        assert\
            'tally_type' in sheet_question,\
            'sheet %d, question %d: no tally_type' % (tally_index, qindex)
        assert\
            isinstance(sheet_question['tally_type'], str),\
            'sheet %d, question %d: tally_type is not a string' % (tally_index, qindex)
        assert\
            sheet_question['tally_type'] in ['plurality-at-large'],\
            'sheet %d, question %d: tally_type is not allowed' % (tally_index, qindex)

        assert\
            'blank_votes' in sheet_question,\
            'sheet %d, question %d: no blank_votes' % (tally_index, qindex)
        assert\
            isinstance(sheet_question['blank_votes'], int),\
            'sheet %d, question %d: blank_votes is not an integer' % (tally_index, qindex)
        assert\
            sheet_question['blank_votes'] >= 0,\
            'sheet %d, question %d: blank_votes is negative' % (tally_index, qindex)

        assert\
            'null_votes' in sheet_question,\
            'sheet %d, question %d: no null_votes' % (tally_index, qindex)
        assert\
            isinstance(sheet_question['null_votes'], int),\
            'sheet %d, question %d: null_votes is not an integer' % (tally_index, qindex)
        assert\
            sheet_question['null_votes'] >= 0,\
            'sheet %d, question %d: null_votes is negative' % (tally_index, qindex)

        assert\
            'answers' in sheet_question,\
            'sheet %d, question %d: no answers' % (tally_index, qindex)
        assert\
            isinstance(sheet_question['answers'], list),\
            'sheet %d, question %d: question answers is not a list' % (tally_index, qindex)

        for aindex, sheet_answer in enumerate(sheet_question['answers']):
            assert\
                'text' in sheet_answer,\
                'sheet %d, question %d, answer %d: no text' % (tally_index, qindex, aindex)
            assert\
                isinstance(sheet_answer['text'], str),\
                'sheet %d, question %d, answer %d: text is not a string' % (tally_index, qindex, aindex)

            assert\
                'num_votes' in sheet_answer,\
                'sheet %d, question %d, answer %d: no num_votes' % (tally_index, qindex, aindex)
            assert\
                isinstance(sheet_answer['num_votes'], int),\
                'sheet %d, question %d, answer %d: num_votes is not an int' % (tally_index, qindex, aindex)
            assert\
                sheet_answer['num_votes'] >= 0,\
                'sheet %d, question %d, answer %d: num_votes is negative' % (tally_index, qindex, aindex)

def _verify_configuration(
    configuration, 
    configuration_index,
    elections_by_id
):
    '''
    Verify the configuration required format
    '''

    assert\
        type(configuration) is dict,\
        'configuration %d: is not a dict' % configuration_index

    assert\
        "ballot_box_name_filter_re" in configuration,\
        'configuration %d: no ballot_box_name_filter_re' % configuration_index
    assert\
        type(configuration["ballot_box_name_filter_re"]) == str,\
        'configuration %d, ballot_box_name_filter_re: is not a string' % configuration_index
    try:
        re.compile(configuration["ballot_box_name_filter_re"])
    except:
        assert\
            False,\
            'configuration %d, ballot_box_name_filter_re: invalid regexp' % configuration_index

    assert\
        "election_index" in configuration,\
        'configuration %d: no election_index' % configuration_index
    assert\
        type(configuration["election_index"]) == int,\
        'configuration %d, election_index: is not a number' % configuration_index
    assert\
        configuration["election_index"] in elections_by_id,\
        'configuration %d, election_index: not found' % configuration_index
    election_data = elections_by_id[configuration["election_index"]]

    assert\
        "question_index" in configuration,\
        'configuration %d: no question_index' % configuration_index
    assert\
        type(configuration["question_index"]) == int,\
        'configuration %d, question_index: is not a number' % configuration_index
    assert\
        (
            configuration["question_index"] >= 0 and 
            len(election_data['results']["questions"]) > configuration["question_index"]
        ),\
        'configuration %d, question_index: not found' % configuration_index

    assert\
        "tally_sheets_question_index" in configuration,\
        'configuration %d: no tally_sheets_question_index' % configuration_index
    assert\
        type(configuration["tally_sheets_question_index"]) == int,\
        'configuration %d, tally_sheets_question_index: is not a number' % configuration_index

def _sum_tally_sheet_numbers(
    tally_sheet,
    results,
    question_index,
    tally_sheets_question_index,
    configuration_index
):
    '''
    Adds the results of the tally sheet
    '''
    questions = results['questions']
    results['total_votes'] += tally_sheet['num_votes']

    question = questions[question_index]
    sheet_question = tally_sheet['questions'][tally_sheets_question_index]
    question['totals']['blank_votes'] += sheet_question['blank_votes']
    question['totals']['null_votes'] += sheet_question['null_votes']
    question['totals']['valid_votes'] += tally_sheet['num_votes'] - sheet_question['blank_votes'] - sheet_question['null_votes']

    sheet_answers = dict([
        (answer['text'], answer)
        for answer in sheet_question['answers']
    ])

    assert\
        len(question['answers']) == len(sheet_question['answers']),\
        'configuration %d, question_index %d (len=%d), tally_sheets_question_index %d (len=%d): not the same number of answers' % (
            configuration_index,
            question_index,
            tally_sheets_question_index,
            len(question['answers']),
            len(sheet_question['answers'])
        )

    for aindex, answer in enumerate(question['answers']):
        text = answer['text']
        sheet_answer = sheet_answers.get(text, None)
        assert\
            sheet_answer is not None,\
            'configuration %d, question_index %d, tally_sheets_question_index %d, answer %d (text=\'%s\'): answer not found in tally sheet' % (
                configuration_index,
                question_index,
                tally_sheets_question_index,
                aindex,
                answer['text']
            )
        answer['total_count'] += sheet_answer['num_votes']

def _init_elections_by_id(data_list):
    '''
    Initializes elections_by_id
    '''
    elections_by_id = dict()
    for dindex, election_data in enumerate(data_list):
        if 'id' not in election_data:
            election_data['id'] = dindex
    
        elections_by_id[election_data['id']] = election_data
    return elections_by_id

def _ensure_results(election_data):
    if 'results' not in election_data:
        questions_path = os.path.join(
            election_data['extract_dir'], 
            "questions_json"
        )
        
        with open(questions_path, 'r', encoding="utf-8") as f:
            questions = json.loads(f.read())
        election_data['results'] = dict(
            questions=questions,
            total_votes=0
        )
    else:
        questions = election_data['results']['questions']

    for question in questions:
        _initialize_question(question)

def count_tally_sheets(
    data_list, 
    tally_sheets,
    configurations,
    help="this parameter is ignored"
):
    '''
    Given a list of tally sheets, add their results to the election in the
    configuration given.

    - "tally_sheets" argument format is like this example:
    tally_sheets = [
        {
            "ballot_box_name": "Postal votes",
            "num_votes": 222,
            "questions": [
                {
                    "title": "Do you want Foo Bar to be president?",
                    "blank_votes": 1,
                    "null_votes": 1,
                    "tally_type": "plurality-at-large",
                    "answers": [
                        {
                            "text": "Yes",
                            "num_votes": 200
                        },
                        {
                            "text": "No",
                            "num_votes": 120
                        }
                    ]
                }
            ]
        }
    ]

    - "configurations" argument format is like this example:
    "configurations": [
        {
            "ballot_box_name_filter_re": "^Postal votes$",
            "election_index": 0,
            "question_index": 0,
            "tally_sheets_question_index": 0,
        }
    ]
    '''

    # initialize elections by id dict
    elections_by_id = _init_elections_by_id(data_list)

    # ensure this election has questions initialized first
    for election_data in data_list:
        _ensure_results(election_data)

    # check ballot_box_list
    for tally_index, tally_sheet in enumerate(tally_sheets):
        _verify_tally_sheet(tally_sheet, tally_index)

    # check configuration
    for configuration_index, configuration in enumerate(configurations):
        _verify_configuration(
            configuration, 
            configuration_index, 
            elections_by_id
        )

    # execute each configuration
    for configuration_index, configuration in enumerate(configurations):
        ballot_box_name_filter_re = configuration["ballot_box_name_filter_re"]
        election_index = configuration["election_index"]
        question_index = configuration["question_index"]
        tally_sheets_question_index = configuration["tally_sheets_question_index"]

        election_data = elections_by_id[election_index]

        # execute each matching tally sheet
        for tally_index, tally_sheet in enumerate(tally_sheets):
            # filter by ballot box name first
            if not re.match(
                ballot_box_name_filter_re, 
                tally_sheet['ballot_box_name']
            ):
                continue

            _sum_tally_sheet_numbers(
                tally_sheet,
                election_data['results'],
                question_index,
                tally_sheets_question_index,
                configuration_index
            )
