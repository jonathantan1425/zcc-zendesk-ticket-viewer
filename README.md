# ZCC Zendesk Ticket Viewer
A python-based CLI tool to view tickets via Zendesk's API.

Users can:
1. Request to view all tickets (paged in rows of 25)
2. Request to view details of specifically 1 ticket (given the ticket_id)

## Features
OS-independent ticket viewer designed to view ticket data from Zendesk's Ticket API\
(https://developer.zendesk.com/api-reference/ticketing/tickets/tickets/)

API requests are made on an ad-hoc basis to enable dynamic data-feeding. 
This allows users to view the most updated ticket data at time of interaction with the tool.
> For instance, the user decides to view (1) all tickets, (2) ticket_id 1, (3) ticket_id 2 sequentially.
> Between viewing all tickets and the 2 individual tickets, ticket_id 1 and 2 data were updated.
> As a result of ad-hoc API requests, the user sees the updated data of ticket_id 1 and 2 when viewing individually, as compared to when the user was viewing all tickets

__Notes__
* Output for viewing all tickets are summarized to contain `id`, `subject`, `priority`, `status`, `submitter_id`, `assignee_id`, and `organization_id` data.
* For individual tickets, the data displayed is similar, with the additional of `description`. This allows the user to view more details with regards to a single ticket.

## Prerequisites
* Recommended platform - Linux (Ubuntu 16.04)
* Either
   * Docker installed OR
   * Python 3.8 and Pip installed

### Verify Docker
Run `docker` in terminal to check if Docker is installed. An example of a positive response:
```bash
$ docker
Usage:  docker [OPTIONS] COMMAND

A self-sufficient runtime for containers

Options:
...
```
If `Command 'docker' not found...`, proceed with installing Docker
### Install Docker
Refer to https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-20-04 for instructions.

## Installation and set-up
The CLI tool can be executed through either of two methods.
1. Through a Docker image
2. Through the terminal as a Python executable

For both methods, begin with (1) setting up the local directories, and (2) providing the API user credentials

### Set-up local directories
Clone this repository or download the files to a local directory.\
Open a terminal session and navigate to the path of this repository/codebase.
> e.g. if working path is `/usr/lib/zcc-zendesk-ticket-viewer`
```bash
cd /usr/lib/zcc-zendesk-ticket-viewer
```
### Provide API user credentials
API requests to Zendesk's Ticket API requires authentication (via email and API key) to a targeted subdomain.\
Edit user credentials in `.env.example` to provide API access credentials using any text editor (`vi .env.example`).
1. Replace `<>` fields with the respective information (subdomain, email_address, API_key).
2. Rename `.env.example` to `.env`.

__Note: `.env` is automatically ignored by git__
```yaml
ZCC_SUBDOMAIN=<fill in subdomain>
ZCC_EMAIL_ADDRESS=<fill in email adress>
ZCC_API_KEY=<fill in api key>
```

### Option 1: Setting Up the Docker Image
#### Build Docker image
Create Docker image of directory using `docker build` (for image tag: ticket-viewer)
```bash
docker build -t ticket-viewer .
```
#### Run Docker image
Run the Docker image to initialize the CLI tool\
__Note: `-i` enables interactive mode, `-t` enables optimal terminal viewing experience__
```bash
docker run -i -t ticket-viewer
```

### Option 2: Executing as a Python executable
__Requirements:__
1. Python 3.8
2. Pip
#### Optional: Set up a Virtual Environment
For users who want to isolate their package dependencies, consider using a virtual environment to load the necessary Python packages.
```bash
pip install venv
```
```bash
python3 -m venv /path/to/new/virtual/environment
```
```bash
source /path/to/new/virtual/environment/bin/activate
```
For more information, please refer to: https://docs.python.org/3/library/venv.html

#### Install Python packages
Install the necessary Python packages according to `requirements.txt`.\
__Note: Ensure that the current terminal session is at the file path of this codebase__
> e.g. /usr/lib/zcc-zendesk-ticket-viewer
```bash
pip install -r requirements.txt
```
#### Launch Python executable
While in the main file path, execute the following command (remove the `ticket_viewer/` extension if current session is in the `ticket_viewer` folder).
```bash
python3 ticket_viewer/viewer.py
```

### Successful installation/set-up
On valid API user credentials (from `.env`), you should see:
```
Welcome to Zendesk Ticket Viewer. You are currently connected to {subdomain} as {email}.
Type 'menu' to view ticket options or 'quit' to exit the viewer

->
```

## Navigating the Ticket Viewer
Use associated commands while the docker image is running to request specific actions
### `menu` - View all available commands
```
-> menu
Available user commands:
        quit:           Exit the ticket viewer
        all:            View all tickets associated with subdomain and email
        select x:       View ticket details of ticket with ticket_id = x
-> 
```
### `quit` - Exit the Ticket Viewer
```
-> quit
Thank you for using the Zendesk Ticket Viewer by Jonathan Tan.
```
### `select x` - View ticket details of ticket with ticket_id = x
```
-> select 1
--------------------------------------------------
Ticket ID: 1    Subject: Sample ticket: Meet the ticket
Priority: normal        Status: open

Hi there,

I’m sending an email because I’m having a problem setting up your new product. Can you help me troubleshoot?

Thanks,
 The Customer

Organization: None      Submitted by: 903456475603      Assigned to: 903456475603
--------------------------------------------------
-> 
```
### `all` - View all tickets associated with subdomain and email
Navigate between pages by entering `<` for left, and `>` for right, `q` to quit viewing all tickets
```
Type '<' or '>' to navigate between pages, 'q' to end ticket viewing.

+----+-----------------------------------------------+----------+--------+--------------+--------------+-----------------+
| id |                    subject                    | priority | status | submitter_id | assignee_id  | organization_id |
+----+-----------------------------------------------+----------+--------+--------------+--------------+-----------------+
| 1  |        Sample ticket: Meet the ticket         |  normal  |  open  | 903456475603 | 903456475603 |      None       |
| 2  |        Sample ticket: Meet the ticket         |  normal  |  open  | 903456475603 | 903456475603 |      None       |
| 3  |        Sample ticket: Meet the ticket         |  normal  |  open  | 903456475603 | 903456475603 |      None       |
| 4  |        Sample ticket: Meet the ticket         |  normal  |  open  | 903456475603 | 903456475603 |      None       |
| 5  |        Sample ticket: Meet the ticket         |  normal  |  open  | 903456475603 | 903456475603 |      None       |
| 6  |        Sample ticket: Meet the ticket         |  normal  |  open  | 903456475603 | 903456475603 |      None       |
| 7  |        Sample ticket: Meet the ticket         |  normal  |  open  | 903456475603 | 903456475603 |      None       |
| 8  |        Sample ticket: Meet the ticket         |  normal  |  open  | 903456475603 | 903456475603 |      None       |
| 9  |        Sample ticket: Meet the ticket         |  normal  |  open  | 903456475603 | 903456475603 |      None       |
| 10 |        Sample ticket: Meet the ticket         |  normal  |  open  | 903456475603 | 903456475603 |      None       |
| 11 |        Sample ticket: Meet the ticket         |  normal  |  open  | 903456475603 | 903456475603 |      None       |
| 12 |        Sample ticket: Meet the ticket         |  normal  |  open  | 903456475603 | 903456475603 |      None       |
| 13 |        Sample ticket: Meet the ticket         |  normal  |  open  | 903456475603 | 903456475603 |      None       |
| 14 |        Sample ticket: Meet the ticket         |  normal  |  open  | 903456475603 | 903456475603 |      None       |
| 15 |        Sample ticket: Meet the ticket         |  normal  |  open  | 903456475603 | 903456475603 |      None       |
| 16 |        Sample ticket: Meet the ticket         |  normal  |  open  | 903456475603 | 903456475603 |      None       |
| 17 |        Sample ticket: Meet the ticket         |  normal  |  open  | 903456475603 | 903456475603 |      None       |
| 18 |        Sample ticket: Meet the ticket         |  normal  |  open  | 903456475603 | 903456475603 |      None       |
| 19 |        Sample ticket: Meet the ticket         |  normal  |  open  | 903456475603 | 903456475603 |      None       |
| 20 |        Sample ticket: Meet the ticket         |  normal  |  open  | 903456475603 | 903456475603 |      None       |
| 21 |        Sample ticket: Meet the ticket         |  normal  |  open  | 903456475603 | 903456475603 |      None       |
| 22 |        Sample ticket: Meet the ticket         |  normal  |  open  | 903456475603 | 903456475603 |      None       |
| 23 |        Sample ticket: Meet the ticket         |  normal  |  open  | 903456475603 | 903456475603 |      None       |
| 24 |        Sample ticket: Meet the ticket         |  normal  |  open  | 903456475603 | 903456475603 |      None       |
| 25 |        Sample ticket: Meet the ticket         |  normal  |  open  | 903456475603 | 903456475603 |      None       |
+----+-----------------------------------------------+----------+--------+--------------+--------------+-----------------+

```
## Teardown (Removing Docker image and containers)
As the `docker build` is an image, there will likely be containers using the images as dependencies. Thus to teardown (or uninstall the tool), the associated containers must be removed before the image. Alternatively, you might consider force removing the image, although that may cause other Docker images and containers on the same machine to be affected.

Consider removing the Docker image to identify the dependent containers. For instance, running `docker image rm ticket-viewer` will return the container `9a62b15b8x1h` that is using the image.
```bash
$ docker image rm ticket-viewer  
Error response from daemon: conflict: unable to remove repository reference "ticket-viewer" (must force) - container  is using its referenced image {image_id}
```
With this information, drop the container `{container_id}` and attempt to drop the image again.
```bash
$ docker rm {container_id}
{container_id}
$ docker image rm ticket-viewer
```
## Testing (For Developers)
Python Unittests are provided to ensure functionality and usability.
This can be run either in the Docker image, or from the working path of this codebase if the local machine has necessary Python packages in `requirements.txt`.

__From the Docker image__
```bash
docker run ticket-viewer sh -c "python -m unittest tests/test_viewer.py -b"
```
```bash
$ docker run ticket-viewer sh -c "python -m unittest tests/test_viewer.py -b"
....................
----------------------------------------------------------------------
Ran 20 tests in 0.051s

OK
$ 
```
__From working path__
```bash
python -m unittest tests/test_viewer.py -b
```
```bash
zcc-zendesk-ticket-viewer $ python -m unittest tests/test_viewer.py -b
....................
----------------------------------------------------------------------
Ran 20 tests in 0.053s

OK
zcc-zendesk-ticket-viewer $
```
