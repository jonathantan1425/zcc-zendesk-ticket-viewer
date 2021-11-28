import getpass
import requests
import json
import time

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
        quit

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

def get_tickets(tickets='All'):
    '''
    Returns all tickets as requested
    
    Args:
        tickets(str): All tickets by default, else replaced by ticket_id for specific ticket
    '''

    pass

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
            # 'all' for all tickets
            # 'select x' for ticket with x ticket id
        # request all tickets if input = all
            # handle pagination
            # output all tickets in pages of 25 when count > 25
        # request specific ticket detail if input = select x

if __name__ == "__main__":
    cli_interface()