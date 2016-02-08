# -*- coding: utf-8 -*-

import os
import json
import unittest 

import utils

class tests(unittest.TestCase):

	# Prueba en la que existe un ganador bajo una situación normal
	# Asignado a: test_09.tar.gz
	def test_normal_winner(self):
		
		utils.executeAgoraResults('test_09')	

		jsonObject = utils.getJsonObjectFromResults()

		jsonObjectTotalVotes = jsonObject["questions"][0]["totals"]

		jsonObjectAnswers = jsonObject["questions"][0]["answers"]

		self.assertEqual(jsonObjectAnswers[0]["winner_position"], 0)
		self.assertEqual(jsonObjectAnswers[1]["winner_position"], None)
		self.assertEqual(jsonObjectAnswers[2]["winner_position"], None)

		self.assertEqual(jsonObjectAnswers[0]["text"], "Opcion 2")

		self.assertEqual(jsonObjectTotalVotes["valid_votes"], 8)
		self.assertEqual(jsonObjectTotalVotes["blank_votes"], 1)
		self.assertEqual(jsonObjectTotalVotes["null_votes"], 1)
	
	# Prueba en la que existe un empate bajo una situación normal
	# Asignado a: test_10.tar.gz
	def test_tie_of_winners(self):
		
		utils.executeAgoraResults('test_10')	

		jsonObject = utils.getJsonObjectFromResults()

		jsonObjectTotalVotes = jsonObject["questions"][0]["totals"]

		jsonObjectAnswers = jsonObject["questions"][0]["answers"]

		self.assertEqual(jsonObjectAnswers[0]["winner_position"], None)
		self.assertEqual(jsonObjectAnswers[1]["winner_position"], None)
		self.assertEqual(jsonObjectAnswers[2]["winner_position"], None)

		self.assertEqual(jsonObjectTotalVotes["valid_votes"], 4)
		self.assertEqual(jsonObjectTotalVotes["blank_votes"], 0)
		self.assertEqual(jsonObjectTotalVotes["null_votes"], 0)

	# Prueba en la que existe un ganador en una situación con 2 ganadores como máximo
	# Asignado a: test_11.tar.gz
	def test_winner_with_two_max_winners(self):
		
		utils.executeAgoraResults('test_11')	

		jsonObject = utils.getJsonObjectFromResults()

		jsonObjectTotalVotes = jsonObject["questions"][0]["totals"]

		jsonObjectAnswers = jsonObject["questions"][0]["answers"]

		self.assertEqual(jsonObjectAnswers[0]["winner_position"], 0)
		self.assertEqual(jsonObjectAnswers[1]["winner_position"], None)
		self.assertEqual(jsonObjectAnswers[2]["winner_position"], None)
		
		self.assertEqual(jsonObjectAnswers[0]["text"], "Opcion 2")

		self.assertEqual(jsonObjectTotalVotes["valid_votes"], 8)
		self.assertEqual(jsonObjectTotalVotes["blank_votes"], 1)
		self.assertEqual(jsonObjectTotalVotes["null_votes"], 1)

	# Prueba en la que existe un empate en una situación con 2 ganadores como máximo
	# Asignado a: test_12.tar.gz
	def test_tie_with_two_max_winners(self):
		
		utils.executeAgoraResults('test_12')	

		jsonObject = utils.getJsonObjectFromResults()

		jsonObjectTotalVotes = jsonObject["questions"][0]["totals"]

		jsonObjectAnswers = jsonObject["questions"][0]["answers"]

		self.assertEqual(jsonObjectAnswers[0]["winner_position"], 0)
		self.assertEqual(jsonObjectAnswers[1]["winner_position"], 1)
		self.assertEqual(jsonObjectAnswers[2]["winner_position"], None)

		self.assertEqual(jsonObjectAnswers[0]["text"], "Opcion 1")
		self.assertEqual(jsonObjectAnswers[1]["text"], "Opcion 2")

		self.assertEqual(jsonObjectTotalVotes["valid_votes"], 4)
		self.assertEqual(jsonObjectTotalVotes["blank_votes"], 0)
		self.assertEqual(jsonObjectTotalVotes["null_votes"], 0)

if __name__=='__main__':
   unittest.main()
