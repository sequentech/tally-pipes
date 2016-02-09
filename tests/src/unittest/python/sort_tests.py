# -*- coding: utf-8 -*-


import os
import json
import unittest 
import jsonschema

import utils

from agora_results.pipes.sort import sort_non_iterative

class sort_tests(unittest.TestCase):
	
	def test_positive_check_config(self):
		config = json.loads('{"question_indexes": [0,1,2,3,4], "withdrawals":[0,1,2], "ties_sorting":[0,1,2]}')
		self.assertTrue(sort_non_iterative.check_config(config))

	def test_negative_check_config(self):
		config = json.loads('{"question_indexes": true}')
		self.assertRaises(jsonschema.exceptions.ValidationError, sort_non_iterative.check_config, config)

if __name__=='__main__':
   unittest.main()
