# -*- coding: utf-8 -*-


import os
import json
import unittest 
import jsonschema

import utils

from agora_results.pipes.results import do_tallies

class results_tests(unittest.TestCase):
	
	# Test que prueba que los parámetros de configuración estén correctos
	def test_positive_check_config(self):
		config = json.loads('{"ignore_invalid_votes": true , "print_as_csv": true, "requestion_indexes": [0,1,2,3,4] , "reuse_results": true , "tallies_indexes": [0,1,2,3]}')
		self.assertTrue(do_tallies.check_config(config))

	# Test negativo que prueba que el tipo requerido del parámetro se compruebe
	def test_negative_check_config(self):
		config = json.loads('{"ignore_invalid_votes": 0}')
		self.assertRaises(jsonschema.exceptions.ValidationError, do_tallies.check_config, config)

if __name__=='__main__':
   unittest.main()
