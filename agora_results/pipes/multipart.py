
def reduce_with_corrections(data_list, questions_corrections):
    '''
    Reduce the param tallies, with the given corrections. The tallies should be
    given in historical order <first> <second> <last>. The last tally is the
    most recent and the one used as a base for the corrections.

    In the end, it modifies the data_list reversing the order, so that the next
    pipes that use only the first data_list element are based on the last tally.

    questions_corrections is a list of questions. For each question, it contains
    a dictionary where the key is the answerid, and the value is a list of
    vote sources from other tallies. These vote sources indicates a list of
    elements for sources from the different tallies from which the answer has
    been voted.

    There are some assumptions in this reducing step:
     - all votes are counted, even if some partial selections could be disregarded
     - questions are not changed, only options

    Example:

    questions_corrections = [
        {                             // first question 0
            "1": [                    // answer id 1
                {                     // source of votes for this
                    "tally_id": 0,
                    "question_id": 0,
                    "answer_id": 1
                },
                {
                    "tally_id": 1,
                    "question_id": 0,
                    "answer_id": 1
                }
            ]
        }
    ]
    '''
    last_data = data_list[-1]

    # all votes must be counted, so sum total_votes, so sum total_votes for all
    # tallies
    for tally_num in range(len(data_list[:-1])):
        last_data['result']['total_votes'] += data_list[tally_num]['result']['total_votes']

    for dest_question_id, question in zip(range(len(questions_corrections)), questions_corrections):
        dest_q = last_data['result']['counts'][dest_question_id]

        # sum the invalid votes for this question
        for tally_num in range(len(data_list[:-1])):
            tally_q = data_list[tally_num]['result']['counts'][dest_question_id]
            dest_q['invalid_votes'] += tally_q['invalid_votes']
            dest_q['blank_votes'] += tally_q['blank_votes']

        for answerid, corrections_list in question.items():
            for vote_source in corrections_list:
                tally_id = vote_source['tally_id']
                question_id = vote_source['question_id']
                answer_id = vote_source['answer_id']

                source_answer = data_list[tally_id]['result']['counts'][question_id]['answers'][answer_id - 1]
                dest_q['answers'][int(answerid) - 1]['total_count'] += source_answer['total_count']
                dest_q['valid_votes'] += source_answer['total_count']

    data_list.reverse()