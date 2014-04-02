# -*- coding:utf-8 -*-

import os
import copy
import json
import subprocess
import agora_tally.tally
from itertools import groupby, chain

def result_to_file(data, path):
    tallies = []
    result = agora_tally.tally.do_tally(data['extract_dir'],
                                        data['result']['counts'],
                                        tallies)
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
