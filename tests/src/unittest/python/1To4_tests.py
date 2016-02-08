# -*- coding: utf-8 -*-

import os
import json
import unittest 

import utils


class tests(unittest.TestCase):

	# Prueba de un caso en el que todos los votos sean válidos
	# Asociado a: test_01.tar.gz
	def test_valid_votes(self):

		utils.executeAgoraResults('test_01')	

		jsonObject = utils.getJsonObjectFromResults()

		jsonObjectTotalVotes = jsonObject["questions"][0]["totals"]

		self.assertEqual(jsonObjectTotalVotes["valid_votes"], 4)
		self.assertEqual(jsonObjectTotalVotes["blank_votes"], 0)
		self.assertEqual(jsonObjectTotalVotes["null_votes"], 0)

	# Prueba en el que todos los vatos sean en blanco
	# Asociado a: test_02.tar.gz
	def test_blank_votes(self):

		utils.executeAgoraResults('test_02')	

		jsonObject = utils.getJsonObjectFromResults()

		jsonObjectTotalVotes = jsonObject["questions"][0]["totals"]

		self.assertEqual(jsonObjectTotalVotes["valid_votes"], 0)
		self.assertEqual(jsonObjectTotalVotes["blank_votes"], 4)
		self.assertEqual(jsonObjectTotalVotes["null_votes"], 0)
	
	# Prueba en el que todos los votos son en nulo
	# Asociado a: test_03.tar.gz
	def test_null_votes(self):

		utils.executeAgoraResults('test_03')	

		jsonObject = utils.getJsonObjectFromResults()

		jsonObjectTotalVotes = jsonObject["questions"][0]["totals"]

		self.assertEqual(jsonObjectTotalVotes["valid_votes"], 0)
		self.assertEqual(jsonObjectTotalVotes["blank_votes"], 0)
		self.assertEqual(jsonObjectTotalVotes["null_votes"], 4)

	# Prueba en el que haya una variedad de votos (nulos, blancos y válidos)
	# Asociado a: test_04.tar.gz
	def test_all_types_of_votes(self):
		
		utils.executeAgoraResults('test_04')	

		jsonObject = utils.getJsonObjectFromResults()

		jsonObjectTotalVotes = jsonObject["questions"][0]["totals"]

		self.assertEqual(jsonObjectTotalVotes["valid_votes"], 2)
		self.assertEqual(jsonObjectTotalVotes["blank_votes"], 2)
		self.assertEqual(jsonObjectTotalVotes["null_votes"], 2)
		
if __name__=='__main__':
   unittest.main()

