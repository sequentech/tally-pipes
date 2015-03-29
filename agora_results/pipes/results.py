# -*- coding:utf-8 -*-

import os
import json
import agora_tally.tally

def __patcher(tally):
    parse_vote = tally.parse_vote

    def parse_vote_f(number, question):
        vote = parse_vote(number, question)
        l = [tally.question_num] + vote
        to_str = [str(i) for i in l]
        print(",".join(to_str))
        return vote

    tally.parse_vote = parse_vote_f

def do_tallies(data_list, ignore_invalid_votes=True, print_as_csv=False,
               question_indexes=None, reuse_results=False, truncate_votes=None):
    for data in data_list:
      tallies = []
      if not reuse_results:
          questions_path = os.path.join(data['extract_dir'], "questions_json")
          with open(questions_path, 'r', encoding="utf-8") as f:
              questions_json = json.loads(f.read())
      else:
          questions_json = data['results']['questions']

      if 'size_corrections' in data:
          for question in questions_json:
              f = data['size_corrections_apply_to_question']
              f(question, data['size_corrections'])

      monkey_patcher=None
      if print_as_csv:
          monkey_patcher = __patcher

      if "truncate_votes" in data and truncate_votes is None:
          truncate_votes = data["truncate_votes"]
      results = agora_tally.tally.do_tally(
          data['extract_dir'],
          questions_json,
          tallies,
          question_indexes=question_indexes,
          ignore_invalid_votes=ignore_invalid_votes,
          monkey_patcher=monkey_patcher,
          truncate_votes=truncate_votes,
          withdrawals=data.get('withdrawals', []))

      def get_log(tally, index):
          if question_indexes is not None and index not in question_indexes:
              if 'log' not in data:
                  return {}
              else:
                  return data['log'][index]
          return tally.get_log()

      data['results'] = results
      data['log'] = [get_log(t, i) for i, t in enumerate(tallies)]

def to_files(data_list, paths):
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