#!/usr/bin/env python3

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
                    answ_id=result['answers_by_name'][i][answ['value']],
                    answ_value=answ['value']
                  ))
            q[str(answ['id'])] = answ_corrections
        corrections.append(q)

    print(json.dumps(corrections, indent=4))