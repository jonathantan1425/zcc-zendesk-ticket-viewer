import unittest
from src.viewer import *

class Test(unittest.TestCase):
    def test_validate_credentials(self):
        '''
        Test if validate_credentials returns False if input params (subdomain, email and password) are invalid
        '''
        actual = validate_credentials('subdomain','email','password')
        expected = False
        self.assertEqual(actual, expected)