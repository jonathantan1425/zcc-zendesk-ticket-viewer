from unittest import TestCase, mock
from src.viewer import *

class Test(TestCase):
    def test_get_credentials(self):
        '''
        Test if get_credentials returns 3 strings for subdomain, email and password
        '''
        subdomain, email, password = get_credentials('tests/test_user_credentials.json')
        self.assertTrue(type(subdomain) == str)
        self.assertTrue(type(email) == str)
        self.assertTrue(type(password) == str)

    def test_fake_validate_credentials(self):
        '''
        Test if validate_credentials returns False if input params (subdomain, email and password) are invalid
        '''
        fake_credentials = validate_credentials('subdomain','email','password')
        self.assertFalse(fake_credentials)

    def test_true_validate_credentials(self):
        '''
        Test if validate_credentials returns True if input params (subdomain, email and password) are valid
        '''
        with mock.patch('src.viewer.requests.get') as mock_request:
            mock_request.return_value.status_code = 200
            true_credentials = validate_credentials('subdomain','email','password')
            mock_request.assert_called_once()
        self.assertTrue(true_credentials)
    
    