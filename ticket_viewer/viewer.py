from dotenv import load_dotenv
import json
import numpy as np
import os
import requests
import shutil
from tabulate import tabulate
import time
import pandas as pd
import sys

def get_credentials():
    """Get user credentials (subdomain, email_address, oauth_token) from env var

    Returns
    -------
    subdomain : str
        Name of Zendesk subdomain
    user_email : str
        Login email credential
    api_token : str
        Login API token credential
    """    

    load_dotenv()

    subdomain = os.getenv('ZCC_SUBDOMAIN')
    user_email = os.getenv('ZCC_EMAIL_ADDRESS') + "/token"
    api_token = os.getenv('ZCC_API_KEY')

    return subdomain, user_email, api_token

def validate_credentials(subdomain, email, api_token):
    """Validates user's subdomain, email and api_token to ensure API endpoint is calleable

    Parameters
    ----------
    subdomain : str
        Name of Zendesk subdomain
    email : str
        Login email credential
    api_token : str
        Login API token credential

    Returns
    -------
    Bool
        True: If credentials can successfully connect; False: If credentials cannot connect
    """
    
    api_url = f'https://{subdomain}.zendesk.com/api/v2/tickets.json'
    headers = {'Accept': 'application/json'}
    resp = requests.get(api_url, auth=(email, api_token), headers=headers)

    # verify if email and api_token can be authenticated against API
    if resp.status_code == 429: # if rate limit reached, retry again
        time.sleep(int(resp.headers['retry-after']) + 1)
        resp = requests.get(api_url, auth=(email, api_token), headers=headers)

    if resp.status_code == 200:
        return True

    else:
        print(f'Authentication failed, status code: {resp.status_code}')
        return False

def get_tickets(subdomain, email, api_token, tickets):
    """Calls Zendesk Tickets API and returns tickets as requested

    Parameters
    ----------
    subdomain : str
        Name of Zendesk subdomain
    email : str
        Login email credential
    api_token : str
        Login API token credential
    tickets : {'all', int}
        Type of ticket to request
        * all: Request all tickets
        * int: Request ticket with ticket_id = int

    Returns
    -------
    results : list of dicts or dict
        Ticket data from API
        * tickets = all: list of dicts, each dict containing the data of 1 ticket
        * tickets = int: dict of single ticket data
    """

    if tickets == 'all':
        api_url = f'https://{subdomain}.zendesk.com/api/v2/tickets.json'
    else:
        api_url = f'https://{subdomain}.zendesk.com/api/v2/tickets/{tickets}.json'
    headers = {'Accept': 'application/json'}
    results = []
    max_tickets = 0
    pages_downloaded = 0
    while api_url:
        resp = requests.get(api_url, auth=(email, api_token), headers=headers)
        if resp.status_code == 429: # catch rate limit exceeded, although normal usage should not exceed limit of 400/minute
            print('Rate limited, reattempting shortly')
            time.sleep(int(resp.headers['retry-after']) + 1)
            continue
        elif resp.status_code == 404 and tickets != 'all': # API endpoint does not exist (usually for invalid ticket_id)
            print('API endpoint unavailable, possibly due to invalid ticket_id. Please try again.')
            return False
        elif resp.status_code != 200: # API error
            print(f'API request trouble encountered, status code: {resp.status_code}. Please try again.')
            return False
        page_data = resp.json()
        if tickets != 'all': return page_data['ticket']
        
        # show download status
        if max_tickets == 0:
            max_tickets = page_data['count']
        pages_downloaded += len(page_data['tickets'])
        percent_downloaded = round(pages_downloaded/max_tickets*100, 1)
        print(f'{percent_downloaded}% downloaded...', end='\r')
        
        # add results and paginate if possible
        results.extend(page_data['tickets'])
        if 'next_page' in page_data:
            api_url = page_data['next_page']
        else:
            break
    return results

def process_all_tickets(api_results):
    """Condense api_results into a DataFrame, keeping only (id, subject, description, priority, status, submitter_id, assignee_id, organization_id)

    Parameters
    ----------
    api_results : list of dicts
        Ticket data from API, each dict containing the data of 1 ticket

    Returns
    -------
    DataFrame
        Normalized ticket data for ('id', 'subject', 'priority', 'status', 'submitter_id', 'assignee_id', 'organization_id')
    """

    tickets_df = pd.DataFrame(api_results)
    tickets_df = tickets_df[['id', 'subject', 'priority', 'status', 'submitter_id', 'assignee_id', 'organization_id']].set_index('id')
    
    # wraggle datatypes
    tickets_df[['submitter_id', 'assignee_id', 'organization_id']] = tickets_df[['submitter_id', 'assignee_id', 'organization_id']].astype("Int64").astype('string')
    tickets_df[['subject', 'priority', 'status']] = tickets_df[['subject', 'priority', 'status']].astype('string')
    
    return tickets_df.fillna(value='None')

def delete_terminal_lines(n):
    """Moves cursor up and delete previous output lines in the terminal by n times

    Parameters
    ----------
    n : int
        Indicate number of output lines to delete
    """
 
    for i in range(n):
        sys.stdout.write('\x1b[1A')
        sys.stdout.write('\x1b[2K')

def check_terminal_window():
    """Checks the terminal window size and prompts user to increase it for the best paging viewing experience
    """

    terminal_rows = shutil.get_terminal_size().lines
    while terminal_rows < 31:
        print("Current terminal window size is too short. It is recommended to increase the height for the best viewing experience. Type 'Y' to continue.")
        user_input = input().upper()
        if user_input == 'Y':
            break

def display_pages_25(tickets_df):
    """Prints all tickets in pages of 25 rows

    Parameters
    ----------
    tickets_df : DataFrame
        Normalized ticket data for ('id', 'subject', 'priority', 'status', 'submitter_id', 'assignee_id', 'organization_id')
    """
    
    max_rows = len(tickets_df)
    pages = [(x,x+25) for x in range(0,max_rows,25)]
    page_num = 0
    max_page = len(pages) - 1
    print("Type '<' or '>' to navigate between pages, 'q' to end ticket viewing.\n")
    paged_df = tickets_df.iloc[pages[page_num][0]:pages[page_num][1]]
    print(tabulate(paged_df, headers='keys', tablefmt='pretty'))
    navigation = input().lower()
    delete_terminal_lines(1)
    print_count = len(paged_df) + 4
    
    while navigation != 'q':
        if navigation == '>' and page_num < max_page:
            page_num += 1
            delete_terminal_lines(print_count)
            paged_df = tickets_df.iloc[pages[page_num][0]:pages[page_num][1]]
            print(tabulate(paged_df, headers='keys', tablefmt='pretty'))
            print_count = len(paged_df) + 4
            
        elif navigation == '<' and page_num > 0:
            page_num -= 1
            delete_terminal_lines(print_count)
            paged_df = tickets_df.iloc[pages[page_num][0]:pages[page_num][1]]
            print(tabulate(paged_df, headers='keys', tablefmt='pretty'))
            print_count = len(paged_df) + 4
            
        navigation = input()
        delete_terminal_lines(1)


def process_select_ticket(api_results):
    """Extracts (id, subject, description, priority, status, submitter_id, assignee_id, organization_id) from API results of selected ticket and prints output

    Parameters
    ----------
    api_results : dict
        Dict of single ticket data
    """

    divider = '-' * min(shutil.get_terminal_size().columns, 50)

    id = api_results['id']
    subject = api_results['subject']
    description = api_results['description']
    priority = api_results['priority']
    status = api_results['status']
    submitter_id = api_results['submitter_id']
    assignee_id = api_results['assignee_id']
    organization_id = api_results['organization_id']

    print(divider)
    print(f'Ticket ID: {id}\tSubject: {subject}')
    print(f'Priority: {priority}\tStatus: {status}')
    print(f'\n{description}\n')
    print(f'Organization: {organization_id}\tSubmitted by: {submitter_id}\tAssigned to: {assignee_id}')
    print(divider)

def menu_action():
    """Prints list of commands
    """

    print('Available user commands:')
    print('\tquit:\t\tExit the ticket viewer')
    print('\tall:\t\tView all tickets associated with subdomain and email')
    print('\tselect x:\tView ticket details of ticket with ticket_id = x')

def load_select_ticket(user_command):
    """Processes user_command when it starts with 'select ' and differentiates between valid and invalid ticket_id entry

    Parameters
    ----------
    user_command : str
        String starting with 'select '

    Returns
    -------
    int
        Represent ticket_id
    """

    user_command = user_command.replace(" ","")
    select_split = user_command.split('select')
    ticket_id = select_split[1]
    if len(select_split) != 2 or not ticket_id.isdigit():
        print('Select command understood but ticket_id value is invalid. Please try again.')
        return False
    return int(ticket_id)

def interface_tool():
    """Presents interface for Zendesk Ticket Viewer
    
    1. Gets user credentials from config.env
    2. Request user input for viewing type (menu, all, select x, quit)
    3. Returns appropriate user request based on input
    """

    subdomain, user_email, api_token = get_credentials()
    # prompt user to modify config.env if invalid user credentials
    if not validate_credentials(subdomain, user_email, api_token):
        exit('Exiting Ticket Viewer...')

    # successful authorization
    print(f'Welcome to Zendesk Ticket Viewer. You are currently connected to {subdomain} as {user_email.rstrip("/token")}.')
    print("Type 'menu' to view ticket options or 'quit' to exit the viewer.\n")

    user_input = input('-> ').lower()
    while user_input != 'quit':
        # show view menu if input = menu
        if user_input == 'menu':
            menu_action()

        # request all tickets if input = all
        elif user_input == 'all':
            tickets = get_tickets(subdomain, user_email, api_token, tickets='all')
            if tickets:
                tickets_df = process_all_tickets(tickets)
                check_terminal_window()
                display_pages_25(tickets_df)

        # request specific ticket detail if input == 'select x'
        elif user_input[0:7] == 'select ':
            ticket_id = load_select_ticket(user_input)
            if ticket_id:
                tickets = get_tickets(subdomain, user_email, api_token, tickets=ticket_id)
                if tickets:
                    process_select_ticket(tickets)
                    
        else:
            print("User command not recognised, please try again or type 'menu' to see list of commands.")
        user_input = input('-> ').lower()

if __name__ == "__main__":
    pd.options.display.float_format = '{:.0f}'.format
    interface_tool()