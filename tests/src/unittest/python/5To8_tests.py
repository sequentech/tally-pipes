# -*- coding: utf-8 -*-

import os
import json
import unittest 

import utils

class tests(unittest.TestCase):

	# Prueba en la que no haya votos
	# Asignado a: test_05.tar.gz
	def test_no_votes(self):
		
		utils.executeAgoraResults('test_05')	

		jsonObject = utils.getJsonObjectFromResults()

		jsonObjectTotalVotes = jsonObject["questions"][0]["totals"]

		self.assertEqual(jsonObjectTotalVotes["valid_votes"], 0)
		self.assertEqual(jsonObjectTotalVotes["blank_votes"], 0)
		self.assertEqual(jsonObjectTotalVotes["null_votes"], 0)

	# Prueba en la que no haya ganador si no hay votos
	# Asignado a: test_06.tar.gz
	def test_no_winner_without_votes(self):

		utils.executeAgoraResults('test_06')	

		jsonObject = utils.getJsonObjectFromResults()

		jsonObjectTotalVotes = jsonObject["questions"][0]["totals"]

		jsonObjectAnswers = jsonObject["questions"][0]["answers"]

		self.assertEqual(jsonObjectAnswers[0]["winner_position"], None)
		self.assertEqual(jsonObjectAnswers[1]["winner_position"], None)
		self.assertEqual(jsonObjectAnswers[2]["winner_position"], None)

		self.assertEqual(jsonObjectTotalVotes["valid_votes"], 0)
		self.assertEqual(jsonObjectTotalVotes["blank_votes"], 0)
		self.assertEqual(jsonObjectTotalVotes["null_votes"], 0)

	# Prueba de que no haya ganador si todos los votos son en blanco
	# Asignado a: test_07.tar.gz
	def test_no_winner_with_blank_votes(self):

		utils.executeAgoraResults('test_07')	

		jsonObject = utils.getJsonObjectFromResults()

		jsonObjectTotalVotes = jsonObject["questions"][0]["totals"]

		jsonObjectAnswers = jsonObject["questions"][0]["answers"]

		self.assertEqual(jsonObjectAnswers[0]["winner_position"], None)
		self.assertEqual(jsonObjectAnswers[1]["winner_position"], None)
		self.assertEqual(jsonObjectAnswers[2]["winner_position"], None)

		self.assertEqual(jsonObjectTotalVotes["valid_votes"], 0)
		self.assertEqual(jsonObjectTotalVotes["blank_votes"], 7)
		self.assertEqual(jsonObjectTotalVotes["null_votes"], 0)

	# Prueba de que no hay ganador con todos los votos nulos
	# Asignado a: test_08.tar.gz
	def test_no_winner_with_null_votes(self):

		utils.executeAgoraResults('test_08')	

		jsonObject = utils.getJsonObjectFromResults()

		jsonObjectTotalVotes = jsonObject["questions"][0]["totals"]

		jsonObjectAnswers = jsonObject["questions"][0]["answers"]

		self.assertEqual(jsonObjectAnswers[0]["winner_position"], None)
		self.assertEqual(jsonObjectAnswers[1]["winner_position"], None)
		self.assertEqual(jsonObjectAnswers[2]["winner_position"], None)

		self.assertEqual(jsonObjectTotalVotes["valid_votes"], 0)
		self.assertEqual(jsonObjectTotalVotes["blank_votes"], 0)
		self.assertEqual(jsonObjectTotalVotes["null_votes"], 5)
		
if __name__=='__main__':
   unittest.main()
