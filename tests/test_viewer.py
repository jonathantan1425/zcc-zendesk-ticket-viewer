from unittest import TestCase, mock
# from requests import status_codes
from src.viewer import *

class TestCredentials(TestCase):
    def setUp(self) -> None:
        TestCredentials.subdomain = 'testerdomain'
        TestCredentials.email = 'tester@abc.com'
        TestCredentials.password = 'tester1234'

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
        fake_credentials = validate_credentials(TestCredentials.subdomain, TestCredentials.email, TestCredentials.password)
        self.assertFalse(fake_credentials)

    def test_true_validate_credentials(self):
        '''
        Test if validate_credentials returns True if input params (subdomain, email and password) are valid
        '''
        with mock.patch('src.viewer.requests.get') as mock_request:
            mock_request.return_value.status_code = 200
            true_credentials = validate_credentials(TestCredentials.subdomain, TestCredentials.email, TestCredentials.password)
            mock_request.assert_called_once()
        self.assertTrue(true_credentials)
    
    def tearDown(self) -> None:
        pass
    
class TestInterfaceActions(TestCase):
    def setUp(self) -> None:
        pass

    def test_menu(self):
        '''
        Test if menu_action() only prints statements without amending anything else
        '''
        self.assertIsNone(menu_action())
    
    def test_load_select_ticket(self):
        '''
        Test if load_select_ticket can accurately differentiate between valid and invalid 'select x' commands
        '''
        test_cases = ['select 1', 'select 222', 'select 33', 'select 5 ', 'select  3', 'select 3 4', 'select ', 'select a', 'select 3A', 'select 5,2']
        test_answers = [1, 222, 33, 5, 3, 34, False, False, False, False]
        test_results = [load_select_ticket(test_case) for test_case in test_cases]
        [self.assertEqual(value, test_answers[index]) for index, value in enumerate(test_results)]

    def tearDown(self) -> None:
        pass

class TestTicketsAPI(TestCase):
    def setUp(self):
        TestTicketsAPI.subdomain = 'testerdomain'
        TestTicketsAPI.email = 'tester@abc.com'
        TestTicketsAPI.password = 'tester1234'

    # TODO: Prevent infinite loop
    # def test_get_tickets_status_429(self):
    #     '''
    #     Test if get_tickets() can respond to status code 429 and wait accordingly
    #     '''
    #     with mock.patch('src.viewer.requests.get') as mock_request:
    #         mock_request.return_value.status_code = 429
    #         mock_request.return_value.header['retry-after'] = 1
    #         with mock.patch('src.viewer.time.sleep') as mock_sleep:
    #             mock_sleep.return_value = None
    #             tickets = get_tickets(TestTicketsAPI.subdomain, TestTicketsAPI.email, TestTicketsAPI.password, 'all')
    #             mock_sleep.assert_called_once()

    def test_get_tickets_status_404(self):
        '''
        Test if get_tickets() can respond to status code 404 and return False
        '''
        with mock.patch('src.viewer.requests.get') as mock_request:
            mock_request.return_value.status_code = 404
            tickets = get_tickets(TestTicketsAPI.subdomain, TestTicketsAPI.email, TestTicketsAPI.password, 'all')
            self.assertFalse(tickets)

    def test_get_tickets_status_not200(self):
        '''
        Test if get_tickets() can respond to status codes other than 429, 404 and 200 and return False
        '''
        with mock.patch('src.viewer.requests.get') as mock_request:
            mock_request.return_value.status_code = 555
            tickets = get_tickets(TestTicketsAPI.subdomain, TestTicketsAPI.email, TestTicketsAPI.password, 'all')
            self.assertFalse(tickets)

    # TODO: Prevent infinite loop
    # def test_get_tickets_pagination(mocked_resp):
    #     '''
    #     Test if get_tickets() can react to next page and output a combined result
    #     '''
    #     with mock.patch('src.viewer.requests.get') as mock_request:
    #         mock_request.return_value.status_code = 200
    #         mock_request.return_value.json.return_value = {"ticket": "mock", "next_page": "mockwebsite.com"}
    #         tickets = get_tickets(TestTicketsAPI.subdomain, TestTicketsAPI.email, TestTicketsAPI.password, 'all')
    #         mock_request.json.assert_called_once()
    
    def tearDown(self) -> None:
        pass