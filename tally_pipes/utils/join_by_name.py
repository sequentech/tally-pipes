#!/usr/bin/env python3

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

import argparse
import json
import codecs

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Match multiple tally options by name to generate a configuration.')
    parser.add_argument('files', nargs='+', help='result_json files')
    args = parser.parse_args()
    results = []

    # load results
    for fname in args.files:
        with codecs.open(fname, encoding='utf-8', mode='r') as f:
            results.append(dict(
                data=json.loads(f.read()),
                answers_by_name=[]
            ))

    # creating answers_by_name dict
    for result in results:
        for i, question in zip(range(len(result['data']['counts'])), result['data']['counts']):
            q = dict([(answ['value'], answ['id']) for answ in question['answers']])
            result['answers_by_name'].append(q)

    # create the join
    corrections = []
    for i, question in zip(range(len(results[-1]['data']['counts'])), results[-1]['data']['counts']):
        q = dict()
        for answ in question['answers']:
            answ_corrections = []
            for j, result in zip(range(len(results[-1])), results[:-1]):
                if answ['value'] in result['answers_by_name'][i]:
                  answ_corrections.append(dict(
                    tally_id = j,
                    question_id= i,
                    answer_id=result['answers_by_name'][i][answ['value']],
                    answer_value=answ['value']
                  ))
            q[str(answ['id'])] = answ_corrections
        corrections.append(q)

    print(json.dumps(corrections, indent=4))