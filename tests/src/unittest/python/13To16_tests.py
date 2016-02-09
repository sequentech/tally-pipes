# -*- coding: utf-8 -*-

import os
import json
import unittest 

import utils

class Test13To16(unittest.TestCase):

	# Prueba de votos válidos en una situación en la que min=2 y max=4
	# Asignado a: test_13.tar.gz
	def test_valid_votes_with_min2max4(self):
		utils.executeAgoraResults('test_13')	

		jsonObject = utils.getJsonObjectFromResults()

		jsonObjectTotalVotes = jsonObject["questions"][0]["totals"]

		jsonObjectAnswers = jsonObject["questions"][0]["answers"]

		self.assertEqual(jsonObjectAnswers[0]["winner_position"], 0)
		self.assertEqual(jsonObjectAnswers[1]["winner_position"], None)

		self.assertEqual(jsonObjectAnswers[0]["text"], "Opcion 2")

		self.assertEqual(jsonObjectTotalVotes["valid_votes"], 4)
		self.assertEqual(jsonObjectTotalVotes["blank_votes"], 0)
		self.assertEqual(jsonObjectTotalVotes["null_votes"], 0)

	# Prueba de votos inválidos saliendo del rango en una situación en la que min=2 y max=4
	# Asignado a: test_14.tar.gz
	def test__invalid_votes_with_min2max4(self):
		utils.executeAgoraResults('test_14')	

		jsonObject = utils.getJsonObjectFromResults()

		jsonObjectTotalVotes = jsonObject["questions"][0]["totals"]

		jsonObjectAnswers = jsonObject["questions"][0]["answers"]

		self.assertEqual(jsonObjectTotalVotes["valid_votes"], 0)
		self.assertEqual(jsonObjectTotalVotes["blank_votes"], 0)
		self.assertEqual(jsonObjectTotalVotes["null_votes"], 3)

	# Prueba de votos de todo tipo en una situación en la que min=2 y max=4
	# Asignado a: test_15.tar.gz
	def test_all_types_votes_with_min2max4(self):
		utils.executeAgoraResults('test_15')	

		jsonObject = utils.getJsonObjectFromResults()

		jsonObjectTotalVotes = jsonObject["questions"][0]["totals"]

		jsonObjectAnswers = jsonObject["questions"][0]["answers"]

		self.assertEqual(jsonObjectAnswers[0]["winner_position"], 0)
		self.assertEqual(jsonObjectAnswers[1]["winner_position"], None)

		self.assertEqual(jsonObjectAnswers[0]["text"], "Opcion 2")

		self.assertEqual(jsonObjectTotalVotes["valid_votes"], 4)
		self.assertEqual(jsonObjectTotalVotes["blank_votes"], 0)
		self.assertEqual(jsonObjectTotalVotes["null_votes"], 4)

	# Prueba de dos ganadores en una situación en la que min=2 y max=4
	# Asignado a: test_16.tar.gz
	def test_two_winners_with_min2max4(self):
		utils.executeAgoraResults('test_16')	

		jsonObject = utils.getJsonObjectFromResults()

		jsonObjectTotalVotes = jsonObject["questions"][0]["totals"]

		jsonObjectAnswers = jsonObject["questions"][0]["answers"]

		self.assertEqual(jsonObjectAnswers[0]["winner_position"], 0)
		self.assertEqual(jsonObjectAnswers[1]["winner_position"], 1)
		self.assertEqual(jsonObjectAnswers[2]["winner_position"], None)

		self.assertEqual(jsonObjectAnswers[0]["text"], "Opcion 2")
		self.assertEqual(jsonObjectAnswers[1]["text"], "Opcion 4")

		self.assertEqual(jsonObjectTotalVotes["valid_votes"], 5)
		self.assertEqual(jsonObjectTotalVotes["blank_votes"], 0)
		self.assertEqual(jsonObjectTotalVotes["null_votes"], 2)
	
if __name__=='__main__':
   unittest.main()
