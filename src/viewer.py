import requests
import json
import time
import pandas as pd

def get_credentials(credentials_source):
    '''
    Assigns users' credentials (subdomain, email, password) to local variables and checks validity

    Args:
        credentials_source(str): filename of user credentials (.json format)
    '''
    # get user credentials via user_credentials.json
    with open(credentials_source, 'r') as credentials:
        credentials_json = json.load(credentials)
        subdomain = credentials_json['subdomain']
        user_email = credentials_json['email']
        password = credentials_json['password']

    # prompt user to modify user_credentials.json if invalid user credentials
    if not validate_credentials(subdomain, user_email, password):
        exit('Exiting Ticket Viewer...')

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
        time.sleep(int(resp.headers['retry-after']))
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
    # TODO

    if tickets == 'all':
        api_url = f'https://{subdomain}.zendesk.com/api/v2/tickets.json'
    else:
        api_url = f'https://{subdomain}.zendesk.com/api/v2/tickets/{tickets}.json'
    headers = {'Accept': 'application/json'}
    results = []
    while api_url:
        resp = requests.get(api_url, auth=(email, password), headers=headers)
        if resp.status_code == 429:
            time.sleep(int(resp.headers['retry-after']))
            continue
        elif resp.status_code != 200:
            exit(f'Authentication failed, status code: {resp.status_code}. Exiting Ticket Viewer...')
        page_data = resp.json()
        results.append(page_data)
        if 'next_page' in page_data:
            api_url = page_data['next_page']
        else:
            break
    return results

def process_api_fields(api_results):

    # TODO select api fields to keep and condense into list format    

def cli_interface():
    '''
    Presents CLI interface for Zendesk Ticket Viewer
    1. Gets user credentials from user_credentials.json
    2. Request user input for viewing type (menu, all, select x, quit)
    3. Returns appropriate user request based on input
    '''

    credentials_source = 'user_credentials.json'
    subdomain, user_email, password = get_credentials(credentials_source)
    print(f'Welcome to Zendesk Ticket Viewer. You are currently connected to {subdomain} as {user_email}.')
    print("Type 'menu' to view ticket options or 'quit' to exit the viewer")
    user_input = input().lower()
    while user_input != 'quit':
        # show view menu if input = menu
        if user_input == 'menu':
            print('Available user commands:')
            print('\tquit:\t\tExit the ticket viewer')
            print('\tall:\t\tView all tickets associated with subdomain and email')
            print('\tselect x:\tView ticket details of ticket with ticket_id = x')

        # request all tickets if input = all
        elif user_input == 'all':
            tickets = get_tickets(subdomain, user_email, password, tickets='all')
            # print(tickets)
            tickets_df = pd.json_normalize(tickets)
            tickets_df.to_csv('tickets.csv', header=True, encoding='utf-8')
            print(tickets_df.head())
            # handle pagination
            # output all tickets in pages of 25 when count > 25

        # request specific ticket detail if input = select x
        elif user_input[0:7] == 'select ':
            select_split = user_input.split(' ')
            ticket_id = select_split[1]
            if len(select_split) != 2 or not ticket_id.isdigit():
                print('select command understood but ticket_id value is invalid, please try again')
            else:
                tickets = get_tickets(subdomain, user_email, password, tickets=ticket_id)
                # print(tickets)

        else:
            print('User command not recognised, please try again.')
        user_input = input().lower()
if __name__ == "__main__":
    cli_interface()