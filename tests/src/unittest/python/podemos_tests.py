# -*- coding: utf-8 -*-


import os
import json
import unittest 
import jsonschema

import utils

from agora_results.pipes.podemos import podemos_proportion_rounded_and_duplicates

class podemos_tests(unittest.TestCase):
	
	def test_positive_check_config(self):
		config = json.loads('{"data_list": [0,1,2,3,4], "women_names":[0,1,2], "proportions":[0,1,2], "withdrawed_candidates":[0,1,2]}')
		self.assertTrue(podemos_proportion_rounded_and_duplicates.check_config(config))

	def test_negative_check_config(self):
		config = json.loads('{"data_list": true}')
		self.assertRaises(jsonschema.exceptions.ValidationError, podemos_proportion_rounded_and_duplicates.check_config, config)

if __name__=='__main__':
   unittest.main()
