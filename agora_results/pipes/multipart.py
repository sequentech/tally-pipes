import copy
import types
import agora_tally.tally

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

def remove_duplicated_votes_and_invalid(data_list, actions):
    '''
    Assumes multiple <n> tallies with the same exact questions, and options
    inside those questions.

    The postprocessing done here is the mixing of the results of two candidates
    that are duplicated. In that case, the duplicates mark as invalid votes to
    the same question twice to a duplicate. Duplicates are only allowed in the
    same question.

    For example if an answer of voter to a given question is "01, 02, 03", and
    01 and 02 candidates are duplicated, that ballot is deemed invalid.

    duplicates follows the format of this example:
    [
      {
        "question_id": 0,
        "action": "duplicated",
        "answer_ids": [1, 2]
      },
      ...
    ]
    '''
    actions = copy.deepcopy(actions)

    def monkey_patcher(tally):
        old_parse_vote = tally.parse_vote

        def parse_vote(self, number, question):
            ret = old_parse_vote(number, question)
            if not isinstance(ret, list):
                print("not a list")
                return ret
            for action in actions:
                if action['question_id'] != tally.question_num:
                    continue
                if action['action'] == 'removed':
                    l = action['answer_ids']
                else:
                    l = action['answer_ids'][1:]
                ret = list(set(ret).difference(set(l)))

            return ret

        tally.parse_vote = types.MethodType(parse_vote, tally)


    # use initial order for the counts or the tally log will be messed up
    for data in data_list:
        data['result'] = agora_tally.tally.do_tally(
            data['extract_dir'],
            data['result']['counts'],
            encrypted_invalid_votes=0,
            monkey_patcher=monkey_patcher)

        for i in range(len(data['result']['counts'])):
            for action in actions:
                if action['question_id'] != i:
                    continue
                if action['action'] == "duplicated":
                    l = action['answer_ids'][1:]
                else:
                    # to remove
                    l = action['answer_ids']
                answers = data['result']['counts'][i]['answers']
                for id_to_remove in l:
                    for j in range(len(answers)):
                        if answers[j]['id'] == id_to_remove:
                            print("removing answer id = %d value = %s" % (id_to_remove, answers[j]['value']))
                            answers.pop(j)
                            break


