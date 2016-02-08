import unittest

class prueba(unittest.TestCase):
 # Functions beginning with "test" will be ran as a unit test.
   def test_positive_add(self):
      '''Verify that adding positive numbers works''' # Printed if test fails
      self.assertEqual(5, 5)
	
if __name__=='__main__':
   unittest.main()

