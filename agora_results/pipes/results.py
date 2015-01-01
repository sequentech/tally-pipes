# -*- coding:utf-8 -*-

import os
import json
import agora_tally.tally


def do_tallies(data_list, ignore_invalid_votes=True):
    for data in data_list:
      tallies = []
      questions_path = os.path.join(data['extract_dir'], "questions_json")
      with open(questions_path, 'r', encoding="utf-8") as f:
          questions_json = json.loads(f.read())

      if 'size_corrections' in data:
          for question in questions_json:
              f = data['size_corrections_apply_to_question']
              f(question, data['size_corrections'])

      results = agora_tally.tally.do_tally(
          data['extract_dir'],
          questions_json,
          tallies, ignore_invalid_votes=ignore_invalid_votes)

      data['results'] = results
      data['log'] = [t.get_log() for t in tallies]

def to_files(data_list, paths):
    i = 0
    # do not allow strange paths
    paths = [os.path.basename(path) for path in paths]

    for data in data_list:
        with open(paths[i], 'w', encoding="utf-8") as f:
            f.write(json.dumps(data['results'], indent=4, ensure_ascii=False,
                  sort_keys=True, separators=(',', ': ')))
        i += 1
