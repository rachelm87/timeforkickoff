Time For Kickoff!
Team: Hat Trick Hackers
What is it?
Time For Kickoff! is a small, beginner-friendly tool that shows upcoming football (soccer) matches across the world in your local timezone, and links them to users who have marked a favorite team. It solves a simple problem: busy fans miss games because schedules are spread across leagues and timezones.
Features
Pulls today’s fixtures from API-Sports (API-Football)
Converts kickoff times to a chosen timezone (default: Europe/Vienna)
Stores new users (name, email, favorite team, outreach okay) to table of users
Saves fixtures to JSON and inserts them into PostgreSQL
Simple demo queries: “tonight only”, “users who like this match”, “most popular teams”
Console output in a readable format (for example: 28/08/2025 8PM: Fiorentina vs Polessya (UEFA Europa Conference League))


How to run it (on someone else’s computer)
Prerequisites
Python 3.10 or newer
PostgreSQL 13 or newer
API-Sports (API-Football) key
1) Clone and enter the project
git clone <your-repo-url>.git
cd <your-project-folder>
2) Create and activate a virtual environment
macOS/Linux:
python3 -m venv .venv
source .venv/bin/activate
Windows (PowerShell):
py -m venv .venv
.venv\Scripts\Activate.ps1
3) Install dependencies
pip install -r requirements.txt

5) Configure credentials
Create two files:
connection.py (project root)
# API key from https://dashboard.api-football.com/
API_KEY = "YOUR_APISPORTS_KEY"
DBInfo/db_connection.py
import psycopg2
connection = psycopg2.connect(
    host="localhost",
    port=5432,
    dbname="hackathon",
    user="YOUR_DB_USER",
    password="YOUR_DB_PASSWORD",
)
cursor = connection.cursor()
The app imports them like this:
from DBInfo.db_connection import connection, cursor
from connection import API_KEY
6) Run the app
python CodeInfo/main.py
On first run it will:
Print API status (remaining daily calls)
create fake users hardcoded (skips duplicates by email)
Fetch today’s fixtures (optionally “today only”)
Save to footballdata.json
Insert into matches
Read back and print a sample
Project structure
.
├─ CodeInfo/
│  └─ main.py
├─ DBInfo/
│  └─ db_connection.py
├─ connection.py
├─ requirements.txt
└─ README.md
