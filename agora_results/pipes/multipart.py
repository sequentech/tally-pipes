# This file is part of agora-results.
# Copyright (C) 2014-2016  Agora Voting SL <agora@agoravoting.com>

# agora-results is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License.

# agora-results  is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with agora-results.  If not, see <http://www.gnu.org/licenses/>.

import os
import json
import re
import codecs
import unicodedata
import string
import traceback
import copy
import types
from glob import glob
import agora_tally.tally

def curate_text(text):
    text = text.replace("&#34;", '"')
    text = text.replace("&#43;", '+')
    text = text.replace("&#64;", '@')
    text = text.replace("&#39;", "'")
    text = text.replace("\xa0", ' ')
    text = re.sub("[ \n\t]+", " ", text)
    text = remove_accents(text)
    return text

def remove_accents(text):
    return ''.join(x for x in unicodedata.normalize('NFKD', text) if x in string.ascii_letters).lower()


def make_multipart(data_list, election_ids, help=""):
    '''
    check that the agora-results is being correctly invoked
    '''
    for election_id, data in zip(election_ids, data_list):
        data['id'] = election_id

def election_max_size_corrections(data_list, corrections, help=""):
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

def question_totals_with_corrections(data_list, mappings, help=""):
    '''
    Given a list of question corrections, fix totals in the questions and in
    the election. Example mappings:
   [
    {
      'source_election_id': 0,
      'source_question_num': 0,
      'source_question_title': "what?",
      'dest_question_num': 0
      'dest_question_title': "what?",
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
        src_qtitle = mapping['source_question_title']
        dst_qnum = mapping['dest_question_num']
        dst_qtitle = mapping['dest_question_title']

        src_election =[data for data in data_list if data['id'] == src_eid][0]
        src_q = src_election['results']['questions'][src_qnum]
        assert src_q['title'] == src_qtitle
        dst_q = last_data['results']['questions'][dst_qnum]
        assert dst_q['title'] == dst_qtitle

        dst_q['totals']['blank_votes'] += src_q['totals']['blank_votes']
        dst_q['totals']['null_votes'] += src_q['totals']['null_votes']
        dst_q['totals']['valid_votes'] += src_q['totals']['valid_votes']

def reduce_answers_with_corrections(data_list, mappings, reverse=True, help=""):
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
        try:
          assert curate_text(src_answer['text']) == curate_text(src_anstxt)
        except Exception as e:
          print("source_text != expected_source_text, '%s' != '%s'" %
                (curate_text(src_answer['text']),
                 curate_text(src_anstxt)))
          raise e

        dst_answer = [a for a in dst_q['answers'] if a['id'] == dst_ansid][0]
        try:
          assert curate_text(dst_answer['text']) == curate_text(dst_anstxt)
        except Exception as e:
          print("source_text != expected_source_text, '%s' != '%s'" %
                (curate_text(dst_answer['text']),
                 curate_text(dst_anstxt)))
          raise e

        dst_answer['total_count'] += src_answer['total_count']

    if reverse:
        data_list.reverse()


def multipart_tally_plaintexts_append_joiner(data_list, dst_election_id,
    question_num=0, src_election_ids=[], silent=False, reverse=True, help=""):
    '''
    Does a multipart tally where the ballots from different question
    '''
    # preload questions
    for dindex, data in enumerate(data_list):
        data['id'] = dindex
        questions_path = os.path.join(data['extract_dir'], "questions_json")
        with open(questions_path, 'r', encoding="utf-8") as f:
            data['questions'] = json.loads(f.read())

    dst_plaintexts_path = glob(os.path.join(
          data_list[dst_election_id]['extract_dir'],
          "%d-*" % question_num, "plaintexts_json"))[0]

    with codecs.open(dst_plaintexts_path, encoding='utf-8', mode='a') as final_plaintexts:
        # open the plaintexts file from other tallies, and convert each ballot
        # and append it to the last_tally plaintexts file
        for dindex, data in enumerate(data_list):
            if dindex == dst_election_id or dindex not in src_election_ids:
                continue

            src_question = data['questions'][question_num]
            plaintexts_path = glob(os.path.join(
                  data['extract_dir'], "%d-*" % question_num, "plaintexts_json"))[0]
            with codecs.open(plaintexts_path, encoding='utf-8', mode='r') as plaintexts:
                for line in plaintexts.readlines():
                    final_plaintexts.write(line)

    if reverse:
        data_list.reverse()

def data_list_reverse(data_list, help=""):

    '''
    reverses the data_list
    '''
    data_list.reverse()

def multipart_tally_plaintexts_joiner(data_list, mappings, silent=False,
    reverse=True, help=""):
    '''
    Converts ballots (plaintexts) from different election tallies that share some
    candidates, into a common "final" ballots format, then saves it to be tallied
    later by agora-tally.

    Similar to reduce answers with corrections, but the technique used here is
    to append the list of ballots from different elections into the plaintexts
    of the final tally plaintexts.

    The tallies should be given in historical order <first> <second> <last>.
    The last tally is the most recent and the one used as a base for the
    corrections.

    In the end, it modifies the data_list reversing the order, so that the next
    pipes that use only the first data_list element are based on the last tally.

    There are some assumptions in this reducing step:
     - all ballots are counted, even if some partial selections could be disregarded
     - questions are NOT changed, only options. Order and number of the
       questions is the same.
     - all tallies are used

    Example:

    mappings is a list of corrections with the following format:
    [
      {
        "source_election_id": 0,
        "source_question_num": 0,
        "source_answer_id": 1,
        "source_answer_text": "whatever",
        "dest_question_num": 0,
        "dest_answer_id": 1,
        "dest_answer_text": "whatever"
      },
      ...
    ]
    '''
    last_data = data_list[-1]
    # contains the same information as the mappings list, but in a more
    # convenient way, as a dictionary
    #
    # Use it this way:
    #
    # mappings_dict["%(src_eid)d-%(src_qnum)d-%(src_ansid)d"] -> mapping
    mappings_dict = dict()

    # preload questions
    for dindex, data in enumerate(data_list):
        data['id'] = dindex
        questions_path = os.path.join(data['extract_dir'], "questions_json")
        with open(questions_path, 'r', encoding="utf-8") as f:
            data['questions'] = json.loads(f.read())

    # 1. check mappings, and fill mappings_dict
    for imapping, mapping in enumerate(mappings):
        src_eid = mapping['source_election_id']
        src_qnum = mapping['source_question_num']
        src_ansid = mapping['source_answer_id']
        src_anstxt = mapping['source_answer_text']
        dst_qnum = mapping['dest_question_num']
        dst_ansid = mapping['dest_answer_id']
        dst_anstxt = mapping['dest_answer_text']

        try:
            assert dst_qnum == src_qnum
        except Exception as e:
            print("assert dst_qnum(%d) == src_qnum(%d), mapping #%d: %s" % (
                dst_qnum, src_qnum, imapping, json.dumps(mapping)))
            raise e

        dst_q = last_data['questions'][dst_qnum]
        src_election =[data for data in data_list if data['id'] == src_eid][0]
        src_q = src_election['questions'][src_qnum]
        src_answer = [a for a in src_q['answers'] if a['id'] == src_ansid][0]

        try:
            assert src_answer['text'] == src_anstxt
        except Exception as e:
            print("assert src_answer['text'](%s) == src_anstxt(%s), mapping #%d: %s" % (
                src_answer['text'], src_anstxt, imapping, json.dumps(mapping)))
            raise e


        dst_answer = [a for a in dst_q['answers'] if a['id'] == dst_ansid][0]
        try:
            assert dst_answer['text'] == dst_anstxt
        except Exception as e:
            print("assert dst_answer['text'](%s) == dst_anstxt(%s), mapping #%d: %s" % (
                dst_answer['text'], dst_anstxt, imapping, json.dumps(mapping)))
            raise e

        map_key = "%(src_eid)d-%(src_qnum)d-%(src_ansid)d" % dict(
            src_eid=src_eid, src_qnum=src_qnum, src_ansid=src_ansid)
        mappings_dict[map_key] = mapping

    # 2. add plaintexts from the other tallies into the final one. to do so, open
    # the first plaintexts files first, then open the others one by one, parsing
    # each ballot and translating it with the given mappings into a valid
    # final-tally ballot. This is done for each question separatedly.

    questions_path = os.path.join(last_data['extract_dir'], "questions_json")
    with open(questions_path, 'r', encoding="utf-8") as f:
         dst_questions_json = json.loads(f.read())

    not_found_mappings = []

    def translate_ballot(line, dindex, qindex, src_question, dst_question):
        '''
        Reads a ballot string, decodes it, translate it from source tally
        numbering to dest tally numbering, then encodes it again and returns it.

        Works with all the voting systems in agora-tally, including
        pairwise-beta.
        '''
        # 1. DECODE
        #
        # copied from agora_tally/tally.py and
        # agora_tally/voting_systems/plurality_at_large.py:

        # Note line starts with " (1 character) and ends with
        # "\n (2 characters). It contains the index of the
        # option selected by the user but starting with 1
        # because number 0 cannot be encrypted with elgammal
        # so we trim beginning and end, parse the int and
        # substract one
        number = int(line[1:-2]) - 1
        vote_str = str(number)
        tab_size = len(str(len(src_question['answers']) + 2))

        # fix add zeros
        if len(vote_str) % tab_size != 0:
            num_zeros = (tab_size - (len(vote_str) % tab_size)) % tab_size
            vote_str = "0" * num_zeros + vote_str

        # 2. TRANSLATE
        translated_ballot = []
        for i in range(int(len(vote_str) / tab_size)):
            base_option = int(vote_str[i*tab_size: (i+1)*tab_size])

            map_key = "%(src_eid)d-%(src_qnum)d-%(src_ansid)d" % dict(
            src_eid=dindex, src_qnum=qindex, src_ansid=base_option-1)

            # if not found the mapping, we add the invalid option -1 to the
            # resulting ballot. This option is afterwards processed differently
            # depending on the tally method: in the case of a pairwise
            # comparison questuion, we would have to remove the comparison pair.
            # In other cases we just remove all the -1.
            if map_key not in mappings_dict:
                if map_key not in not_found_mappings:
                    not_found_mappings.append(map_key)

                translated_ballot.append(-1)
                continue

            mapping = mappings_dict[map_key]
            translated_option = mapping['dest_answer_id']+1
            translated_ballot.append(translated_option)

        # print the non-translated options
        if not silent and len(not_found_mappings) > 0:
            print("some ballot answers were not mapped and thus ignored: %s" %
                json.dumps(not_found_mappings))

        # process the untranslated options (-1) and invalid ballots
        final_ballot = []
        if dst_question['tally_type'] is 'pairwise-beta':
            if len(translated_ballot) % 2 != 0:
                raise Exception("Invalid number of options in pairwise ballot")

            for a, b in zip(translated_ballot[::2], translated_ballot[1::2]):
                if a == -1 or b == -1:
                    continue
                final_ballot += [a, b]
        else:
            final_ballot = [a for a in translated_ballot if a != -1]

        # 3. ENCODE
        # start the encoding of the final_ballot, which is a list of ints, into
        # a single already tabulated number.
        #
        # so something like:
        #
        # [1, 5, 7, 8, 11]
        #
        # is translated into:
        #
        # 1050711
        dst_tab_size = len(str(len(dst_question['answers']) + 2))
        final_ballot_int = int(''.join([
            ("%0" + str(dst_tab_size) + "d") % a for a in final_ballot]))

        # return it as a codified line that can be directly appended to the list
        # of plaintexts.
        #
        # so something like:
        #
        # 1050711
        #
        # is translated into:
        #
        # '"1050712"\n'
        return '"%s"\n' % str(final_ballot_int + 1)

    # for each dest question, append translated ballots from the other tallies
    for qindex, dst_question in enumerate(dst_questions_json):

        # open last_tally plaintexts file, only used for "append-only", adding
        # more ballots at the end of the file from the other tallies
        last_plaintexts_path = glob(os.path.join(
              last_data['extract_dir'], "%d-*" % qindex, "plaintexts_json"))[0]
        with codecs.open(last_plaintexts_path, encoding='utf-8', mode='a') as final_plaintexts:
            # open the plaintexts file from other tallies, and convert each ballot
            # and append it to the last_tally plaintexts file
            for dindex, data in enumerate(data_list[:-1]):
                src_question = data['questions'][qindex]
                plaintexts_path = glob(os.path.join(
                      data['extract_dir'], "%d-*" % qindex, "plaintexts_json"))[0]
                with codecs.open(plaintexts_path, encoding='utf-8', mode='r') as plaintexts:
                    for line in plaintexts.readlines():
                        try:
                            translated_ballot = translate_ballot(
                                line,
                                dindex,
                                qindex,
                                src_question,
                                dst_question)
                            final_plaintexts.write(translated_ballot)
                        except Exception as e:
                            final_plaintexts.write("invalid\n")
                            # TODO: count invalid these votes here
                            if not silent:
                                traceback.print_exc()
                            pass


    # 3. reverse data list so that the last election is the first one, as it is
    # starting from now the only one that should really be used for any
    # tallying, as we have consolidated all the ballots in that one.
    if reverse:
        data_list.reverse()


def append_ballots(data_list, ballots, dst_election_id=0,
    question_num=0, allow_null_votes=False, help=""):
    '''
    appends ballots to an election question. This is an example of the votes:
    [
      {
        "Candidate 1": "3",
        "Candidate 2": "",
        "Candidate 3": "1",
        "Candidate 4": "2",
      }
    ]

    The previous example adds one vote where the first selected candidate is
    "Candidate 3", then "Candidate 4", then "Candidate 1".
    '''

    # preload questions
    data = data_list[dst_election_id]
    data['id'] = dst_election_id
    questions_path = os.path.join(data['extract_dir'], "questions_json")
    with open(questions_path, 'r', encoding="utf-8") as f:
        data['questions'] = json.loads(f.read())

    # sanity-check input ballots
    assert(isinstance(ballots, list))

    answer_text_to_id = dict([(a['text'], a['id']) for a in data['questions'][question_num]['answers']])
    fill_size = len(str(len(answer_text_to_id) + 2))

    def encode_ballot(ballot, answer_text_to_id, fill_size):
        # blank vote
        if len(ballot) == 0:
            return str(len(answer_text_to_id) + 2).zfill(fill_size)

        inverse_ballot = {str(v): answer_text_to_id[k] for k, v in ballot.items()}

        return str(int("".join([
            str(
              inverse_ballot.get(
                  str(i),
                  len(answer_text_to_id) + 2) + 1 # null if not found
              ).zfill(fill_size)
            for i in range(0,len(inverse_ballot))
        ])) + 1)

    parsed_ballots = []
    for ballot in ballots:
        assert(isinstance(ballot, dict))
        assert(set(ballot.keys()) == set([a['text'] for a in data['questions'][question_num]['answers']]))
        for value in ballot.values():
            assert(isinstance(value, str))
            # convert to int. all should be int-strings, even null votes, but not empty ones
            if len(value) > 0:
                int(value, 10)

        selection = dict([(k, int(v, 10)-1) for k, v in ballot.items() if len(v) > 0])

        if not allow_null_votes:
            assert(len(set(selection.values())) == len(selection.values()))
            # selection should be ints, sequential and starting from 1
            assert(set(range(0, len(selection))) == set(selection.values()))

        parsed_ballots.append("\"%s\"\n" % encode_ballot(selection, answer_text_to_id, fill_size))

    dst_plaintexts_path = glob(os.path.join(
          data_list[dst_election_id]['extract_dir'],
          "%d-*" % question_num, "plaintexts_json"))[0]

    with codecs.open(dst_plaintexts_path, encoding='utf-8', mode='a') as final_plaintexts:
          for ballot in parsed_ballots:
              final_plaintexts.write(ballot)
