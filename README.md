# ScheduleBot

This bot scrapes the [TW-5 schedules site](https://www.cnatra.navy.mil/scheds/), and notifies registered users when their specific squadron's schedule is available. An attempt is made to scrape the respective data for a user when their name is found on the schedule. Notifications are sent through email, and optionally, text.

# Configuration

Configuration of the project is rather simple with three main steps:

1. [Configure Venv](#configure-venv)
2. [Setup AddressBook](#setup-addressbook)
3. [Configure Windows Task Scheduler](#configure-windows-taskscheduler)

## Configure Venv

As always with python, it is best to setup a virtual environment. I used venv for this.
```powershell
python -m venv C:\path\to\new\virtual\environment
```
Then activate the environment and run the following. This will install all dependencies to the environment:
```powershell
pip install -r requirements.txt
```

To setup the email password, we will configure a .env file. Create this in the root directory. There will be two entries:
```env
EMAIL_PASSWORD=
SENDER_EMAIL=
```

## Setup AddressBook
The AddressBook is a simple `addresses.json` file that contains all contact information for each user. It should be formatted as follows: 
```json
[
  {
    "name": "name",
    "squadron": "squadron",
    "email": ["email@gmail.com"],
    "notified": false,
    "number": [[ 1234567890, "carrier" ] ]
  },
  {
    "name": "name",
    "squadron": "squadron",
    "email": ["email1@gmail.com","email2@gmail.com","email3@comcast.net"],
    "notified": false,
    "number": [[ 1234567890, "carrier1" ], [ 1234567890, "carrier2" ] ]
  }
]
```
- The `Name` field is a string, exactly as written on the schedule PDF
- The `Squadron` field is a string using either `VT-2, VT-3, or VT-6`
- The `Email` field is a list of strings for any number of email addresses
- The `Notified` field is a boolean flag, and should be set to `false`.
- The `Number` field is optional. It is a list of lists. The internal list is the phonenumber, and carrier. The number needs to be without spaces, or special characters. The carrier is a string from the following:
```
verizon, tmobile, sprint, at&t, boost, cricket, uscellular, googlefi
```

## Configure Windows Taskscheduler

Finally, to automate this, we will utilize `Windows Task Scheduler`. Setup a task with the following parameters:
- Run at `11:00 AM` every day
- Repeat every `15` minutes for a duration of `12 hours`
- Select `Run whether user is logged on or not`
- Select `Run with highest privileges`
- Select `Wake the computer to run this task`
  
The `Action` script is as follows:
```
Program/script: C:\PathToBot\ScheduleBot\.venv\Scripts\python.exe
Add arguments (optional): C:\PathToBot\ScheduleBot\ScheduleBot.py
Start in (optional): C:\PathToBot\ScheduleBot\
```
