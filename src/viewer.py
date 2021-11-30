import json
import requests
import shutil
import time
import pandas as pd

def get_credentials(credentials_source):
    '''
    Assigns users' credentials (subdomain, email, password) to local variables

    Args:
        credentials_source(str): filename of user credentials (.json format)
    '''
    # get user credentials via user_credentials.json
    with open(credentials_source, 'r') as credentials:
        credentials_json = json.load(credentials)
        subdomain = credentials_json['subdomain']
        user_email = credentials_json['email']
        password = credentials_json['password']

    return subdomain, user_email, password

def validate_credentials(subdomain, email, password):
    '''
    Validates user's subdomain, email and password to ensure API endpoint is calleable

    Args:
        subdomain(str): Name of Zendesk subdomain
        email(str): Login email credential
        password(str): Login password credential
    '''
    api_url = f'https://{subdomain}.zendesk.com/api/v2/tickets.json'
    resp = requests.get(api_url, auth=(email, password))

    # verify if email and password can be authenticated against API
    if resp.status_code == 429: # if rate limit reached, retry again
        time.sleep(int(resp.headers['retry-after']) + 1)
        resp = requests.get(api_url, auth=(email, password))

    if resp.status_code == 200:
        return True

    else:
        print(f'Authentication failed, status code: {resp.status_code}')
        return False

def get_tickets(subdomain, email, password, tickets):
    '''
    Calls Zendesk Tickets API and returns tickets as requested
    
    Args:
        tickets(str): 'all' for all tickets, 'ticket_id' for specific ticket
    '''

    if tickets == 'all':
        api_url = f'https://{subdomain}.zendesk.com/api/v2/tickets.json'
    else:
        api_url = f'https://{subdomain}.zendesk.com/api/v2/tickets/{tickets}.json'
    headers = {'Accept': 'application/json'}
    results = []
    while api_url:
        resp = requests.get(api_url, auth=(email, password), headers=headers)
        if resp.status_code == 429: # catch rate limit exceeded, although normal usage should not exceed limit of 400/minute
            print('Rate limited, reattempting shortly')
            time.sleep(int(resp.headers['retry-after']) + 1)
            continue
        elif resp.status_code == 404: # API endpoint does not exist (usually for invalid ticket_id)
            return False
        elif resp.status_code != 200:
            print(f'API request trouble encountered, status code: {resp.status_code}. Please try again.')
            return False
        page_data = resp.json()
        print(page_data)
        if tickets != 'all':
            return page_data['ticket']
        results.extend(page_data['tickets'])
        if 'next_page' in page_data:
            api_url = page_data['next_page']
        else:
            break
    return results

def process_all_tickets(api_results):
    # TODO select api fields to keep and condense into list format
    tickets_df = pd.json_normalize(api_results)
    tickets_df = tickets_df[['id', 'subject', 'priority', 'status', 'submitter_id', 'assignee_id', 'organization_id']].set_index('id')
    return tickets_df

def display_pages_25(tickets_df):
    # TODO clean pagination
    max_rows = len(tickets_df)
    print(max_rows)
    print(tickets_df.head(25))
    counter = 25
    navigation = input("Type '<' or '>' to navigate between pages, 'q' to end ticket viewing.").lower()
    while navigation != 'q':
        if navigation == '>' and counter < max_rows:
            print(tickets_df.iloc[counter:counter+25], end='\r')
            counter += 25
        elif navigation == '<' and counter >= 25:
            print(tickets_df.iloc[counter-25:counter], end='\r')
            counter -= 25
        navigation = input()

def process_select_ticket(api_results):
    '''
    Extracts (id, subject, description, priority, status, submitter_id, assignee_id, organization_id) from API results of selected ticket and prints output
    '''
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
    '''
    Prints list of commands
    '''
    print('Available user commands:')
    print('\tquit:\t\tExit the ticket viewer')
    print('\tall:\t\tView all tickets associated with subdomain and email')
    print('\tselect x:\tView ticket details of ticket with ticket_id = x')

def load_select_ticket(user_command):
    '''
    Processes user_command when it starts with 'select ' and differentiates between valid and invalid ticket_id entry
    '''
    user_command = user_command.replace(" ","")
    select_split = user_command.split('select')
    ticket_id = select_split[1]
    if len(select_split) != 2 or not ticket_id.isdigit():
        print('Select command understood but ticket_id value is invalid. Please try again.')
        return False
    return int(ticket_id)

def interface_tool():
    '''
    Presents CLI interface for Zendesk Ticket Viewer
    1. Gets user credentials from user_credentials.json
    2. Request user input for viewing type (menu, all, select x, quit)
    3. Returns appropriate user request based on input
    '''

    credentials_source = 'user_credentials.json'
    subdomain, user_email, password = get_credentials(credentials_source)
    # prompt user to modify user_credentials.json if invalid user credentials
    if not validate_credentials(subdomain, user_email, password):
        exit('Exiting Ticket Viewer...')

    # successful authorization    
    print(f'Welcome to Zendesk Ticket Viewer. You are currently connected to {subdomain} as {user_email}.')
    print("Type 'menu' to view ticket options or 'quit' to exit the viewer\n")

    user_input = input('>').lower()
    while user_input != 'quit':
        # show view menu if input = menu
        if user_input == 'menu':
            menu_action()

        # request all tickets if input = all
        elif user_input == 'all':
            tickets = get_tickets(subdomain, user_email, password, tickets='all')
            tickets_df = process_all_tickets(tickets)
            # handle pagination
            # output all tickets in pages of 25 when count > 25
            display_pages_25(tickets_df)

        # request specific ticket detail if input == 'select x'
        elif user_input[0:7] == 'select ':
            ticket_id = load_select_ticket(user_input)
            if ticket_id:
                tickets = get_tickets(subdomain, user_email, password, tickets=ticket_id)
                if tickets:
                    process_select_ticket(tickets)
                else:
                    print('API endpoint unavailable, possibly due to invalid ticket_id. Please try again.')

        else:
            print("User command not recognised, please try again or type 'menu' to see list of commands.")
        user_input = input('>').lower()

if __name__ == "__main__":
    interface_tool()