import contextlib
import io
from unittest import TestCase, mock
from pandas.api.types import is_string_dtype
import os
from ticket_viewer.viewer import *

class TestCredentials(TestCase):
    def setUp(self) -> None:
        TestCredentials.subdomain = 'testerdomain'
        TestCredentials.email = 'tester@abc.com'
        TestCredentials.api_key = 'testAPIkey'

    def test_get_credentials_returns_str(self):
        subdomain, email, password = get_credentials()
        self.assertTrue(type(subdomain) == str)
        self.assertTrue(type(email) == str)
        self.assertTrue(type(password) == str)

    
    def test_get_credentials_load_env(self):
        with mock.patch('ticket_viewer.viewer.load_dotenv') as mock_load_dotenv:
            with mock.patch('ticket_viewer.viewer.os.getenv') as mock_getenv:
                subdomain, email, password = get_credentials()
                mock_load_dotenv.assert_called_once()
                env_calls = [mock.call('ZCC_SUBDOMAIN'),
                            mock.call('ZCC_EMAIL_ADDRESS'),
                            mock.call().__add__('/token'),
                            mock.call('ZCC_API_KEY')]
                mock_getenv.assert_has_calls(env_calls)
    
    def test_validate_credentials_fail(self):
        with mock.patch('ticket_viewer.viewer.requests.get') as mock_request:
            mock_request.return_value.status_code = 404
            fake_credentials = validate_credentials(TestCredentials.subdomain, TestCredentials.email, TestCredentials.api_key)
        self.assertFalse(fake_credentials)

    def test_validate_credentials_pass(self):
        with mock.patch('ticket_viewer.viewer.requests.get') as mock_request:
            mock_request.return_value.status_code = 200
            true_credentials = validate_credentials(TestCredentials.subdomain, TestCredentials.email, TestCredentials.api_key)
            mock_request.assert_called_once()
        self.assertTrue(true_credentials)
    
    def tearDown(self) -> None:
        pass
    
class TestInterfaceActions(TestCase):
    def setUp(self) -> None:
        pass

    def test_menu_action_print_only(self):
        self.assertIsNone(menu_action())
    
    def test_load_select_ticket_differentiate_commands(self):
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
        TestTicketsAPI.api_key = 'testAPIkey'

    def test_get_tickets_status_429(self):
        with mock.patch('ticket_viewer.viewer.requests.get', side_effect = [mock.Mock(status_code=429, headers = {'retry-after': 1}), mock.Mock(status_code=404)]) as mock_request:
            with mock.patch('ticket_viewer.viewer.time.sleep') as mock_sleep:
                mock_sleep.return_value = None
                tickets = get_tickets(TestTicketsAPI.subdomain, TestTicketsAPI.email, TestTicketsAPI.api_key, 'all')
                mock_sleep.assert_called_once()

    def test_get_tickets_status_404(self):
        with mock.patch('ticket_viewer.viewer.requests.get') as mock_request:
            mock_request.return_value.status_code = 404
            tickets = get_tickets(TestTicketsAPI.subdomain, TestTicketsAPI.email, TestTicketsAPI.api_key, 'all')
            self.assertFalse(tickets)

    def test_get_tickets_status_not_200(self):
        with mock.patch('ticket_viewer.viewer.requests.get') as mock_request:
            mock_request.return_value.status_code = 555
            tickets = get_tickets(TestTicketsAPI.subdomain, TestTicketsAPI.email, TestTicketsAPI.api_key, 'all')
            self.assertFalse(tickets)
            
    def test_get_tickets_return_single_ticket(self):
        with mock.patch('ticket_viewer.viewer.requests.get') as mock_request:
            mock_request.return_value.status_code = 200
            mock_request.return_value.json.return_value = {"ticket": {"mock ticket"}}
            tickets = get_tickets(TestTicketsAPI.subdomain, TestTicketsAPI.email, TestTicketsAPI.api_key, 'select 1')
            self.assertEqual(tickets, {"mock ticket"})

    def test_get_tickets_paginate_correctly(self):
        with mock.patch('ticket_viewer.viewer.requests.get', 
                        side_effect = [mock.Mock(status_code=200, json=lambda : {"tickets": {"mock"}, "next_page": "mockwebsite.com", "count": 2}),
                                       mock.Mock(status_code=200, json=lambda : {"tickets": {"mock2"}, "count": 2})]) as mock_request:
            tickets = get_tickets(TestTicketsAPI.subdomain, TestTicketsAPI.email, TestTicketsAPI.api_key, 'all')
            mock_request.assert_called_with('mockwebsite.com', auth=('tester@abc.com', 'testAPIkey'), headers={'Accept': 'application/json'})
            self.assertEqual(tickets, ["mock", "mock2"])
        
    def test_get_tickets_print_correct_percent_downloaded(self):
        with mock.patch('ticket_viewer.viewer.requests.get', 
                        side_effect = [mock.Mock(status_code=200, json=lambda : {"tickets": {"mock"}, "next_page": "mockwebsite.com", "count": 2}),
                                       mock.Mock(status_code=200, json=lambda : {"tickets": {"mock2"}, "count": 2})]) as mock_request:
            with mock.patch('builtins.print') as mocked_print:
                _ = get_tickets(TestTicketsAPI.subdomain, TestTicketsAPI.email, TestTicketsAPI.api_key, 'all')
                calls = [mock.call('50.0% downloaded...', end='\r'), mock.call('100.0% downloaded...', end='\r')]
                mocked_print.assert_has_calls(calls)
        
    def tearDown(self) -> None:
        pass

class TestTicketProcessing(TestCase):      
    def test_process_all_tickets_return_all_rows_expected_cols(self):
        test_case=[{'id': 1, 'subject': 'sub1', 'priority': 'high', 'status': 'open', 'submitter_id': 33, 'assignee_id': 44, 'organization_id': 55},
                   {'id': 2, 'subject': 'sub2', 'priority': 'low', 'status': 'closed', 'submitter_id': 35, 'assignee_id': 44, 'organization_id': 55},
                   {'id': 3, 'subject': 'sub3', 'priority': 'med', 'status': 'open', 'submitter_id': 33, 'assignee_id': 46, 'organization_id': 55},
                   {'id': 4, 'subject': 'sub4', 'priority': None, 'status': 'open', 'submitter_id': 35, 'assignee_id': 46, 'organization_id': 55},
                   {'id': 5, 'subject': 'sub5', 'priority': 'high', 'status': 'closed', 'submitter_id': 33, 'assignee_id': 44, 'organization_id': 56},
                   {'id': 6, 'subject': 'sub6', 'priority': 'med', 'status': 'open', 'submitter_id': 33, 'assignee_id': 44, 'organization_id': 56},
                   {'id': 7, 'subject': 'sub7', 'priority': 'low', 'status': 'open', 'submitter_id': 33, 'assignee_id': 48, 'organization_id': 57},
                   {'id': 8, 'subject': 'sub8', 'priority': None, 'status': 'open', 'submitter_id': 37, 'assignee_id': 44, 'organization_id': 57},
                   {'id': 9, 'subject': 'sub9', 'priority': 'high', 'status': 'closed', 'submitter_id': 33, 'assignee_id': 48, 'organization_id': 55},
                   {'id': 10, 'subject': 'sub10', 'priority': 'low', 'status': 'open', 'submitter_id': 39, 'assignee_id': 42, 'organization_id': 55}]
        output_df = process_all_tickets(test_case)
        self.assertEqual(len(output_df), 10)
        self.assertEqual(len(output_df.reset_index().columns), 7)
        self.assertEqual(output_df.reset_index().columns.tolist(), ['id', 'subject', 'priority', 'status', 'submitter_id', 'assignee_id', 'organization_id'])
    
    def test_process_all_tickets_dtype(self):
        test_case=[{'id': 1, 'subject': 'sub1', 'priority': 'high', 'status': 'open', 'submitter_id': 33, 'assignee_id': 44, 'organization_id': 55},
                   {'id': 2, 'subject': 'sub2', 'priority': 'low', 'status': 'closed', 'submitter_id': 35, 'assignee_id': 44, 'organization_id': 55},
                   {'id': 3, 'subject': 'sub3', 'priority': 'med', 'status': 'open', 'submitter_id': 33, 'assignee_id': 46, 'organization_id': 55},
                   {'id': 4, 'subject': 'sub4', 'priority': None, 'status': 'open', 'submitter_id': 35, 'assignee_id': 46, 'organization_id': 55},
                   {'id': 5, 'subject': 'sub5', 'priority': 'high', 'status': 'closed', 'submitter_id': 33, 'assignee_id': 44, 'organization_id': 56},
                   {'id': 6, 'subject': 'sub6', 'priority': 'med', 'status': 'open', 'submitter_id': 33, 'assignee_id': 44, 'organization_id': 56},
                   {'id': 7, 'subject': 'sub7', 'priority': 'low', 'status': 'open', 'submitter_id': 33, 'assignee_id': 48, 'organization_id': 57},
                   {'id': 8, 'subject': 'sub8', 'priority': None, 'status': 'open', 'submitter_id': 37, 'assignee_id': 44, 'organization_id': 57},
                   {'id': 9, 'subject': 'sub9', 'priority': 'high', 'status': 'closed', 'submitter_id': 33, 'assignee_id': 48, 'organization_id': 55},
                   {'id': 10, 'subject': 'sub10', 'priority': 'low', 'status': 'open', 'submitter_id': 39, 'assignee_id': 42, 'organization_id': 55}]
        output_df = process_all_tickets(test_case)
        self.assertTrue(is_string_dtype(output_df['subject']))
        self.assertTrue(is_string_dtype(output_df['priority']))
        self.assertTrue(is_string_dtype(output_df['status']))
        self.assertTrue(is_string_dtype(output_df['submitter_id']))
        self.assertTrue(is_string_dtype(output_df['assignee_id']))
        self.assertTrue(is_string_dtype(output_df['organization_id']))
    
    def test_process_all_tickets_no_nan(self):
        test_case=[{'id': 1, 'subject': 'sub1', 'priority': None, 'status': 'open', 'submitter_id': 33, 'assignee_id': 44, 'organization_id': 55},
                   {'id': 2, 'subject': 'sub2', 'priority': 'low', 'status': 'closed', 'submitter_id': 35, 'assignee_id': 44, 'organization_id': 55},
                   {'id': 3, 'subject': 'sub3', 'priority': 'med', 'status': 'open', 'submitter_id': 33, 'assignee_id': 46, 'organization_id': 55},
                   {'id': 4, 'subject': None, 'priority': None, 'status': 'open', 'submitter_id': None, 'assignee_id': None, 'organization_id': None},
                   {'id': 5, 'subject': 'sub5', 'priority': 'high', 'status': None, 'submitter_id': 33, 'assignee_id': 44, 'organization_id': 56},
                   {'id': 6, 'subject': 'sub6', 'priority': 'med', 'status': 'open', 'submitter_id': 33, 'assignee_id': 44, 'organization_id': 56},
                   {'id': 7, 'subject': 'sub7', 'priority': 'low', 'status': 'open', 'submitter_id': 33, 'assignee_id': 48, 'organization_id': None},
                   {'id': 8, 'subject': 'sub8', 'priority': None, 'status': 'open', 'submitter_id': 37, 'assignee_id': 44, 'organization_id': 57},
                   {'id': 9, 'subject': 'sub9', 'priority': 'high', 'status': 'closed', 'submitter_id': 33, 'assignee_id': 48, 'organization_id': 55},
                   {'id': 10, 'subject': 'sub10', 'priority': 'low', 'status': 'open', 'submitter_id': 39, 'assignee_id': 42, 'organization_id': 55}]
        output_df = process_all_tickets(test_case)
        self.assertFalse(output_df.isnull().values.any())
    
    def test_delete_terminal_lines(self):
        console1 = io.StringIO()
        with contextlib.redirect_stdout(console1):
            print('Hello World')
        output_before = console1.getvalue()
        console2 = io.StringIO()
        with contextlib.redirect_stdout(console2):
            delete_terminal_lines(1)
        output_after = console2.getvalue()
        self.assertEqual(output_before, 'Hello World\n')
        self.assertEqual(output_after, '\x1b[1A\x1b[2K')
    
    def test_check_terminal_window_too_short(self):
        with mock.patch('ticket_viewer.viewer.shutil.get_terminal_size') as mock_terminal:
            mock_terminal.return_value.lines = 1
            with mock.patch('builtins.input') as mock_input:
                mock_input.return_value = 'Y'
                check_terminal_window()
                mock_input.assert_called_once()
                
    def test_display_pages_25(self):
        test_df = pd.DataFrame({'id':[i for i in range(1,46)], 'subject': ['sub'+str(i) for i in range(1,46)]}).set_index('id')
        with mock.patch('builtins.input', side_effect = ['>', '>', '>', '<', '<', '<' , '<', '>', 'q']) as mock_input:
            with mock.patch('ticket_viewer.viewer.delete_terminal_lines') as mock_delete_terminal_lines:            
                display_pages_25(test_df)
                calls = [mock.call(1),
                         mock.call(25+4),
                         mock.call(1),
                         mock.call(1),
                         mock.call(1),
                         mock.call(20+4),
                         mock.call(1),
                         mock.call(1),
                         mock.call(1),
                         mock.call(1),
                         mock.call(25+4),
                         mock.call(1)]
                mock_delete_terminal_lines.assert_has_calls(calls)
            
    def test_process_select_ticket_print_correctly(self):
        test_cases = [{'url': 'https://subdomain.zendesk.com/api/v2/tickets/55.json', 'id': 1, 'external_id': None, 'via': {'channel': 'sample_ticket','source': {'from': {}, 'to': {}, 'rel': None}}, 'created_at': '2021-11-26T14:08:15Z',
                      'updated_at': '2021-11-26T14:08:16Z', 'type': 'incident', 'subject': 'Sample', 'raw_subject': 'Sample ticket: Meet the ticket', 'description': 'Sample desc', 'priority': 'normal', 'status': 'open',
                      'recipient': None, 'requester_id': 22, 'submitter_id': 33, 'assignee_id': 44, 'organization_id': 55, 'group_id': 4410465873049, 'collaborator_ids': [], 'follower_ids': [], 'email_cc_ids': [],
                      'forum_topic_id': None, 'problem_id': None, 'has_incidents': False, 'is_public': True, 'due_at': None, 'tags': ['sample', 'support', 'zendesk'], 'custom_fields': [], 'satisfaction_rating': None,
                      'sharing_agreement_ids': [], 'fields': [], 'followup_ids': [], 'ticket_form_id': 900002917083, 'brand_id': 900003782903, 'allow_channelback': False, 'allow_attachments': True},
                      {'url': None, 'id': None, 'external_id': None, 'via': {'channel': None,'source': {'from': {}, 'to': {}, 'rel': None}}, 'created_at': None,
                      'updated_at': None, 'type': None, 'subject': None, 'raw_subject': None, 'description': None, 'priority': None, 'status': None,
                      'recipient': None, 'requester_id': None, 'submitter_id': None, 'assignee_id': None, 'organization_id': None, 'group_id': None, 'collaborator_ids': [], 'follower_ids': [], 'email_cc_ids': [],
                      'forum_topic_id': None, 'problem_id': None, 'has_incidents': None, 'is_public': None, 'due_at': None, 'tags': [], 'custom_fields': [], 'satisfaction_rating': None,
                      'sharing_agreement_ids': [], 'fields': [], 'followup_ids': [], 'ticket_form_id': None, 'brand_id': None, 'allow_channelback': False, 'allow_attachments': True}]
                      
        
        with mock.patch('ticket_viewer.viewer.shutil.get_terminal_size') as mock_terminal_columns:
            mock_terminal_columns.return_value.columns = 1
            with mock.patch('builtins.print') as mocked_print:
                for test_case in test_cases:
                    process_select_ticket(test_case)
                    calls = [mock.call('-'*1), 
                             mock.call(f'Ticket ID: {test_case["id"]}\tSubject: {test_case["subject"]}'), 
                             mock.call(f'Priority: {test_case["priority"]}\tStatus: {test_case["status"]}'),
                             mock.call(f'\n{test_case["description"]}\n'),
                             mock.call(f'Organization: {test_case["organization_id"]}\tSubmitted by: {test_case["submitter_id"]}\tAssigned to: {test_case["assignee_id"]}')]
                    mocked_print.assert_has_calls(calls)
                    
class TestIntegrationInterface(TestCase):
    def test_interface_tool_integration(self):
        """Integration test for interface tool
        1. Call all possible commands ('menu', 'all', 'select 5', 'hello world', 'quit') with fail criteria on ticket commands ('all' and 'select 5')
        2. Call ticket commands ('all' and 'select 5') with pass criteria
        """
        with mock.patch('ticket_viewer.viewer.get_credentials') as mock_get_credentials:
            mock_get_credentials.return_value = 'testerdomain', 'tester@abc.com', 'tester1234'
            with mock.patch('ticket_viewer.viewer.validate_credentials') as mock_validate_credentials:
                mock_validate_credentials.return_value = True
                with mock.patch('builtins.input',
                                side_effect = ['menu', 'all', 'select 5', 'hello world', 'quit']) as mock_input:
                    with mock.patch('ticket_viewer.viewer.menu_action') as mock_menu_action:
                        with mock.patch('ticket_viewer.viewer.get_tickets') as mock_get_tickets:
                            mock_get_tickets.return_value = False
                            with mock.patch('ticket_viewer.viewer.process_all_tickets') as mock_process_all_tickets:
                                with mock.patch('ticket_viewer.viewer.load_select_ticket') as mock_load_select_ticket:
                                    with mock.patch('ticket_viewer.viewer.get_tickets') as mock_get_tickets:
                                        mock_get_tickets.return_value = False
                                        with mock.patch('ticket_viewer.viewer.process_select_ticket') as mock_process_select_ticket:
                                            with mock.patch('builtins.print') as mock_print:
                                                interface_tool()
                                                mock_get_credentials.assert_called_once()
                                                mock_validate_credentials.assert_called_once()
                                                mock_menu_action.assert_called_once()
                                                mock_process_all_tickets.assert_not_called()
                                                mock_load_select_ticket.assert_called_once()
                                                self.assertEqual(mock_get_tickets.call_count, 2)
                                                mock_process_select_ticket.assert_not_called()
                                                print_calls = [mock.call('Welcome to Zendesk Ticket Viewer. You are currently connected to testerdomain as tester@abc.com.'),
                                                               mock.call("Type 'menu' to view ticket options or 'quit' to exit the viewer\n"),
                                                               mock.call("User command not recognised, please try again or type 'menu' to see list of commands.")]
                                                mock_print.assert_has_calls(print_calls)
        with mock.patch('ticket_viewer.viewer.get_credentials') as mock_get_credentials:
            mock_get_credentials.return_value = 'testerdomain', 'tester@abc.com', 'tester1234'
            with mock.patch('ticket_viewer.viewer.validate_credentials') as mock_validate_credentials:
                mock_validate_credentials.return_value = True
                with mock.patch('builtins.input',
                                side_effect = ['all', '>', '<', 'q', 'select 5', 'quit']) as mock_input:
                    with mock.patch('ticket_viewer.viewer.get_tickets') as mock_get_tickets:
                            all_test_case=[{'id': 1, 'subject': 'sub1', 'priority': None, 'status': 'open', 'submitter_id': 33, 'assignee_id': 44, 'organization_id': 55},
                                           {'id': 2, 'subject': 'sub2', 'priority': 'low', 'status': 'closed', 'submitter_id': 35, 'assignee_id': 44, 'organization_id': 55},
                                           {'id': 3, 'subject': 'sub3', 'priority': 'med', 'status': 'open', 'submitter_id': 33, 'assignee_id': 46, 'organization_id': 55},
                                           {'id': 4, 'subject': None, 'priority': None, 'status': 'open', 'submitter_id': None, 'assignee_id': None, 'organization_id': None},
                                           {'id': 5, 'subject': 'sub5', 'priority': 'high', 'status': None, 'submitter_id': 33, 'assignee_id': 44, 'organization_id': 56},
                                           {'id': 6, 'subject': 'sub6', 'priority': 'med', 'status': 'open', 'submitter_id': 33, 'assignee_id': 44, 'organization_id': 56},
                                           {'id': 7, 'subject': 'sub7', 'priority': 'low', 'status': 'open', 'submitter_id': 33, 'assignee_id': 48, 'organization_id': None},
                                           {'id': 8, 'subject': 'sub8', 'priority': None, 'status': 'open', 'submitter_id': 37, 'assignee_id': 44, 'organization_id': 57},
                                           {'id': 9, 'subject': 'sub9', 'priority': 'high', 'status': 'closed', 'submitter_id': 33, 'assignee_id': 48, 'organization_id': 55},
                                           {'id': 10, 'subject': 'sub10', 'priority': 'low', 'status': 'open', 'submitter_id': 39, 'assignee_id': 42, 'organization_id': 55}]
                            mock_get_tickets.return_value = all_test_case
                            with mock.patch('ticket_viewer.viewer.process_all_tickets') as mock_process_all_tickets:
                                with mock.patch('ticket_viewer.viewer.check_terminal_window') as mock_check_terminal_window:
                                    with mock.patch('ticket_viewer.viewer.display_pages_25') as mock_display_pages_25:
                                        with mock.patch('ticket_viewer.viewer.load_select_ticket') as mock_load_select_ticket:
                                            mock_load_select_ticket.return_value = all_test_case[0]
                                            with mock.patch('ticket_viewer.viewer.get_tickets') as mock_get_tickets:
                                                with mock.patch('ticket_viewer.viewer.process_select_ticket') as mock_process_select_ticket:
                                                    interface_tool()
                                                    mock_get_credentials.assert_called_once()
                                                    mock_validate_credentials.assert_called_once()
                                                    mock_process_all_tickets.assert_called_once()
                                                    mock_check_terminal_window.assert_called_once()
                                                    mock_display_pages_25.assert_called_once()
                                                    mock_load_select_ticket.assert_called_once()
                                                    self.assertEqual(mock_get_tickets.call_count, 2)
                                                    mock_process_select_ticket.assert_called_once()