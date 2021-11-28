# ZCC Zendesk Ticket Viewer
A python-based CLI script to view tickets via Zendesk's API.
## Prerequisites
* python3
* pip3
### Platform (Assumed)
* To be updated
### Configurations (Assumed)
* To be updated
## Installation and set-up
Minimal installation is required as long as Python is available on the machine
### Setting up user configuration
API calls require authentication (via email and password) to the targeted subdomain
1. Open user_credentials.json
2. Edit subdomain, email and password \
__Caution: Do not commit changes made to user_credentials.json to GitHub to protect credential confidentiality__
## Using the Ticket Viewer
1. Open session in CLI (Terminal, Powershell, etc.)
2. Navigate to zcc-zendesk-ticket-viewer root folder (Git clone folder or downloaded folder)
3. Run `python viewer.py`

### Navigating the Ticket Viewer
Use associated commands in `viewer.py` to request specific actions
* `menu` - View all available commands
* `quit` - Exit the Ticket Viewer
* `all` - View all tickets associated with subdomain and email
* `select x` - View ticket details of ticket with ticket_id = x
