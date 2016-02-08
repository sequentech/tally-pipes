# -*- coding: utf-8 -*-


import os
import json
import unittest 
import jsonschema

import utils

from agora_results.pipes.modifications import apply_modifications

class modifications_tests(unittest.TestCase):
	
	def test_positive_check_config(self):
		config = json.loads('{"data_list": [0,1,2,3,4], "modifications":[0,1,2] }')
		self.assertTrue(apply_modifications.check_config(config))

	def test_negative_check_config(self):
		config = json.loads('{"data_list": true}')
		self.assertRaises(jsonschema.exceptions.ValidationError, apply_modifications.check_config, config)

if __name__=='__main__':
   unittest.main()
