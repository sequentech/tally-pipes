# -*- coding:utf-8 -*-

import os
import copy
import json
import subprocess
import agora_tally.tally
from itertools import groupby, chain

def result_to_file(data_list, path):
    data = data_list[0]
    tallies = []

    # use initial order for the counts or the tally log will be messed up
    result_path = os.path.join(data['extract_dir'], "result_json")
    with open(result_path, 'r', encoding="utf-8") as f:
        result_json = json.loads(f.read())

    result = agora_tally.tally.do_tally(data['extract_dir'],
                                        result_json['counts'],
                                        tallies, ignore_invalid_votes=False)
    result["electorate_count"] = result["total_votes"]

    # remove ties
    for count in data['result']['counts']:
        if 'ties' in count:
            del count['ties']

    result['counts'] = data['result']['counts']
    res_data = dict(
        agora_result=result,
        tally_log=[t.get_log() for t in tallies]
    )
    with open(path, 'w', encoding="utf-8") as f:
        f.write(json.dumps(res_data, indent=4))
