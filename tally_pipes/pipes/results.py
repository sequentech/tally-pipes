# -*- coding:utf-8 -*-

# This file is part of tally-pipes.
# Copyright (C) 2014-2016  Sequent Tech Inc <legal@sequentech.io>

# tally-pipes is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License.

# tally-pipes  is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with tally-pipes.  If not, see <http://www.gnu.org/licenses/>.

import os
import json
import tally_methods.tally
from tally_methods.voting_systems.base import (
    BlankVoteException,
    ExplicitInvalidVoteException,
    ImplicitInvalidVoteException
)
from collections import defaultdict

def do_tallies(
    data_list, 
    ignore_invalid_votes=True, 
    print_as_csv=False,
    question_indexes=None, 
    reuse_results=False,
    allow_empty_tally=False,
    extra_args=defaultdict(), 
    tallies_indexes=None, 
    help=""
):
    fprint = print
    monkey_patcher=None

    # ballots_fprint is indicated by tally-pipes to write ballots.csv and
    # ballots.json
    if 'ballots_printer' in data_list[0]:
        ballots_printer = data_list[0]['ballots_printer']

    def __patcher(tally):
        parse_vote = tally.parse_vote

        def parse_vote_wrapper(number, question, q_withdrawals):
            exception = None
            vote = None

            try:
                vote = parse_vote(number, question, q_withdrawals)
            except BlankVoteException as error:
                exception = error
                vote = error.ballot
            except ImplicitInvalidVoteException as error:
                exception = error
                vote = error.ballot
            except ExplicitInvalidVoteException as error:
                exception = error
                vote = error.ballot
            except Exception as error:
                exception = error
                vote = None
            ballots_printer(vote, question, tally.question_num, exception)

            if exception is not None:
                raise exception
            return vote

        tally.parse_vote = parse_vote_wrapper

    # ballots_printer is indicated by tally-pipes to write ballots.csv and 
    # ballots.json
    if 'ballots_printer' in data_list[0]:
        monkey_patcher = __patcher


    for dindex, data in enumerate(data_list):
      if tallies_indexes is not None and dindex not in tallies_indexes:
          continue

      tallies = []
      if not reuse_results:
          questions_path = os.path.join(data['extract_dir'], "questions_json")
          with open(questions_path, 'r', encoding="utf-8") as f:
              questions_json = json.loads(f.read())
      else:
          questions_json = data['results']['questions']

      # set the election_index in each question so that it can be used in
      # the ballots_printer
      for question in questions_json:
        question['election_index'] = dindex

      if 'size_corrections' in data:
          for question in questions_json:
              f = data['size_corrections_apply_to_question']
              f(question, data['size_corrections'])

      if print_as_csv and monkey_patcher is None:
          monkey_patcher = __patcher

      withdrawals = []
      for question in questions_json:
          withdrawals = data.get('withdrawals', [])

      results = tally_methods.tally.do_tally(
          data['extract_dir'],
          questions_json,
          tallies,
          question_indexes=question_indexes,
          ignore_invalid_votes=ignore_invalid_votes,
          allow_empty_tally=allow_empty_tally,
          monkey_patcher=monkey_patcher,
          withdrawals=withdrawals)

      def get_log(tally, index):
          if question_indexes is not None and index not in question_indexes:
              if 'log' not in data:
                  return {}
              else:
                  return data['log'][index]
          return tally.get_log()

      data['results'] = results
      data['log'] = [get_log(t, i) for i, t in enumerate(tallies)]

def to_files(data_list, paths, help=""):
    i = 0
    # do not allow strange paths
    paths = [os.path.basename(path) for path in paths]

    for data in data_list:
        with open(paths[i], 'w', encoding="utf-8") as f:
            f.write(json.dumps(data['results'], indent=4, ensure_ascii=False,
                  sort_keys=True, separators=(',', ': ')))
        i += 1

def apply_removals(data_list, help=""):
    data = data_list[0]

    if "removed-candidates" not in data:
        return

    removed_list = data["removed-candidates"]
    for qindex, question in enumerate(data['results']['questions']):
        q_removed = [
            removed['answer_id']
            for removed in removed_list
            if removed['question_index'] == qindex]
        question['answers'] = [answer for answer in question['answers'] if answer['id'] not in q_removed]
