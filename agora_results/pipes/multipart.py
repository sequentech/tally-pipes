import copy
import types
import agora_tally.tally

def make_multipart(data_list, election_ids):
    '''
    check that the agora-results is being correctly invoked
    '''
    for election_id, data in zip(election_ids, data_list):
        data['id'] = election_id

def election_max_size_corrections(data_list, corrections):
    '''
    correct max and min number of options allowed in an election.
    corrections are in the form [[src_max, dest_max], [src_max, dest_max], ..]
    It also affects to num_winners
    '''
    def apply_to_question(question, corrections):
        if question['tally_type'] == 'plurality-at-large' and\
            question['num_winners'] in list(corrections.keys()):
            question['num_winners'] = corrections[question['num_winners']]
            question['max'] = max(question['max'], question['num_winners'])

    for data in data_list:
        # used by do_talies
        data['size_corrections'] = dict(corrections)
        data['size_corrections_apply_to_question'] = apply_to_question

def question_totals_with_corrections(data_list, mappings):
    '''
    Given a list of question corrections, fix totals in the questions and in
    the election. Example mappings:
   [
    {
      'source_election_id': 0,
      'source_question_num': 0,
      'dest_question_num': 0
    },
    ...
   ]
    '''
    # sum the invalid votes for this question
    last_data = data_list[-1]
    for tally_num in range(len(data_list[:-1])):
        tally_q = data_list[tally_num]['results']
        last_data['results']['total_votes'] += tally_q['total_votes']

    for mapping in mappings:
        src_eid = mapping['source_election_id']
        src_qnum = mapping['source_question_num']
        dst_qnum = mapping['dest_question_num']

        src_election =[data for data in data_list if data['id'] == src_eid][0]
        src_q = src_election['results']['questions'][src_qnum]
        dst_q = last_data['results']['questions'][dst_qnum]
        dst_q['totals']['blank_votes'] += src_q['totals']['blank_votes']
        dst_q['totals']['null_votes'] += src_q['totals']['null_votes']
        dst_q['totals']['valid_votes'] += src_q['totals']['valid_votes']

def reduce_answers_with_corrections(data_list, mappings):
    '''
    Reduce the param tallies, with the given corrections. The tallies should be
    given in historical order <first> <second> <last>. The last tally is the
    most recent and the one used as a base for the corrections.

    In the end, it modifies the data_list reversing the order, so that the next
    pipes that use only the first data_list element are based on the last tally.

    There are some assumptions in this reducing step:
     - all votes are counted, even if some partial selections could be disregarded
     - questions are not changed, only options

    Example:

    mappings is a list of correcitons with the following format:
    [
      {
        "source_election_id": 0,
        "source_question_num": 0,
        "source_answer_id": 1
        "source_answer_text": "whatever",
        "dest_question_num": 0,
        "dest_answer_id": 1
        "dest_answer_text": "whatever"
      },
      ...
    ]
    '''
    last_data = data_list[-1]

    for mapping in mappings:
        src_eid = mapping['source_election_id']
        src_qnum = mapping['source_question_num']
        src_ansid = mapping['source_answer_id']
        src_anstxt = mapping['source_answer_text']
        dst_qnum = mapping['dest_question_num']
        dst_ansid = mapping['dest_answer_id']
        dst_anstxt = mapping['dest_answer_text']

        dst_q = last_data['results']['questions'][dst_qnum]
        src_election =[data for data in data_list if data['id'] == src_eid][0]
        src_q = src_election['results']['questions'][src_qnum]
        src_answer = [a for a in src_q['answers'] if a['id'] == src_ansid][0]
        assert src_answer['text'] == src_anstxt

        dst_answer = [a for a in dst_q['answers'] if a['id'] == dst_ansid][0]
        assert dst_answer['text'] == dst_anstxt

        dst_answer['total_count'] += src_answer['total_count']

    data_list.reverse()
