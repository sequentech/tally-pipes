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

def _initialize_question(question, override):
    '''
    Initialize question results to zero if any
    '''
    if 'winners' not in question or override:
        question['winners'] = []
    if 'totals' not in question or override:
        question['totals'] = dict(
            blank_votes=0,
            null_votes=0,
            valid_votes=0
        )
    for answer in question['answers']:
        if "total_count" not in answer:
            answer['total_count'] = 0

def _verify_tally_sheet(tally_sheet, questions, tally_index):
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
        'ballot_box_title' in tally_sheet,\
        'sheet %d: no ballot_box_title' % tally_index
    assert\
        isinstance(tally_sheet['ballot_box_title'], str),\
        'sheet %d: ballot_box_title is not an string' % tally_index

    assert\
      'questions' in tally_sheet,\
      'sheet %d: tally_sheet has no questions' % tally_index
    assert\
      isinstance(tally_sheet['questions'], list),\
      'sheet %d: tally_sheet questions is not a list' % tally_index
    assert\
      len(tally_sheet['questions']) <= len(questions),\
      'sheet %d: tally_sheet has invalid number of questions' % tally_index

    for qindex, question in enumerate(questions):
        if len(tally_sheet['questions']) <= qindex:
            continue

        sheet_question = tally_sheet['questions'][qindex]

        assert\
            'title' in sheet_question,\
            'sheet %d, question %d: no title' % (tally_index, qindex)
        assert\
            isinstance(sheet_question['title'], str),\
            'sheet %d, question %d: title is not a string' % (tally_index, qindex)
        assert\
            question['title'] == sheet_question['title'],\
            'sheet %d, question %d: invalid title' % (tally_index, qindex)

        assert\
            'tally_type' in sheet_question,\
            'sheet %d, question %d: no tally_type' % (tally_index, qindex)
        assert\
            isinstance(sheet_question['tally_type'], str),\
            'sheet %d, question %d: tally_type is not a string' % (tally_index, qindex)
        assert\
            sheet_question['tally_type'] == question['tally_type'],\
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
        assert\
            len(sheet_question['answers']) == len(question['answers']),\
            'sheet %d, question %d: invalid number of answers' % (tally_index, qindex)

        sheet_answers = dict([
          (answer['text'], answer)
          for answer in sheet_question['answers']
        ])

        answers = dict([
          (answer['text'], answer)
          for answer in question['answers']
        ])

        assert\
            set(sheet_answers.keys()) == set(answers.keys()),\
            'not the same set of answers'

        for aindex, answer in enumerate(question['answers']):
            text = answer['text']
            sheet_answer = sheet_answers[text]

            assert\
                'text' in sheet_answer,\
                'sheet %d, question %d, answer %d: no text' % (tally_index, qindex, aindex)
            assert\
                isinstance(sheet_answer['text'], str),\
                'sheet %d, question %d, answer %d: text is not a string' % (tally_index, qindex, aindex)
            assert\
                sheet_answer['text'] == answer['text'],\
                'sheet %d, question %d, answer %d: text is not valid "%s" != "%s"' % (
                    tally_index,
                    qindex,
                    aindex,
                    sheet_answer['text'],
                    answer['text']
                )

            assert\
                'num_votes' in sheet_answer,\
                'sheet %d, question %d, answer %d: no num_votes' % (tally_index, qindex, aindex)
            assert\
                isinstance(sheet_answer['num_votes'], int),\
                'sheet %d, question %d, answer %d: num_votes is not an int' % (tally_index, qindex, aindex)
            assert\
                sheet_answer['num_votes'] >= 0,\
                'sheet %d, question %d, answer %d: num_votes is negative' % (tally_index, qindex, aindex)

        assert\
            sum([
                sum([
                    answer['num_votes']
                    for answer in sheet_question['answers']
                ]),
                sheet_question['blank_votes'],
                sheet_question['null_votes']
            ]) == tally_sheet['num_votes'],\
            'sheet %d, question %d: number of votes does not match' % (tally_index, qindex)

def _sum_tally_sheet_numbers(tally_sheet, results, tally_index):
    '''
    Adds the results of the tally sheet
    '''
    questions = results['questions']
    results['total_votes'] += tally_sheet['num_votes']

    for qindex, question in enumerate(questions):
        if len(tally_sheet['questions']) <= qindex:
            continue

        sheet_question = tally_sheet['questions'][qindex]
        question['totals']['blank_votes'] += sheet_question['blank_votes']
        question['totals']['null_votes'] += sheet_question['null_votes']

        sheet_answers = dict([
          (answer['text'], answer)
          for answer in sheet_question['answers']
        ])

        for aindex, answer in enumerate(question['answers']):
            text = answer['text']
            sheet_answer = sheet_answers[text]
            answer['total_count'] += sheet_answer['num_votes']
            question['totals']['valid_votes'] += sheet_answer['num_votes']

# given a list of tally_sheets, add them to the electoral results
def count_tally_sheets(
    data_list, 
    tally_sheets,
    override=False,
    filter_ballot_box_re=None,
    help="this parameter is ignored"
):
    data = data_list[0]

    if override or 'results' not in data:
        questions_path = os.path.join(data['extract_dir'], "questions_json")
        with open(questions_path, 'r', encoding="utf-8") as f:
            questions = json.loads(f.read())
        data['results'] = dict(
            questions=questions,
            total_votes=0
        )
    else:
        questions = data['results']['questions']

    # initialize
    for question in questions:
        _initialize_question(question, override=override)

    # check ballot_box_list
    for tally_index, tally_sheet in enumerate(tally_sheets):
        _verify_tally_sheet(tally_sheet, questions, tally_index)

    # add the numbers of each tally sheet to the electoral results
    for tally_index, tally_sheet in enumerate(tally_sheets):
        if (
            filter_ballot_box_re is not None and
            not re.match(filter_ballot_box_re, tally_sheet['ballot_box_title']
        ):
            continue

        _sum_tally_sheet_numbers(tally_sheet, data['results'], tally_index)
