# CodeInfo/main.py

import os, sys, requests, json
from datetime import date, datetime
from zoneinfo import ZoneInfo

# make sibling packages importable
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from DBInfo.db_connection import connection, cursor
from connection import API_KEY   # DB credentials + API key live in connection.py

# Fetch fixtures from API-Sports, save to JSON, and print nicely

def get_data(api_key: str,
             filename="footballdata.json",
             timezone: str = "Europe/Vienna",
             upcoming: bool = True,
             limit: int = 50,
             tonight_only: bool = False,
             start_hour: int = 18,
             end_hour: int = 23):

    url = "https://v3.football.api-sports.io/fixtures"
    headers = {"x-apisports-key": api_key}
    params = {
        "date": date.today().isoformat(),
        "timezone": timezone
    }
    if upcoming:
        params["status"] = "NS"

    response = requests.get(url, headers=headers, params=params, timeout=15)
    data = response.json()
    fixtures = data.get("response", [])

    print("API errors:", data.get("errors"))
    print("API echoed params:", data.get("parameters"))

    if tonight_only:
        fixtures = [
            f for f in fixtures
            if start_hour <= int(f["fixture"]["date"][11:13]) <= end_hour
        ]

    fixtures.sort(key=lambda f: f["fixture"]["date"])
    if limit:
        fixtures = fixtures[:limit]
    data["response"] = fixtures

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(fixtures)} fixtures to {filename}.")

    for f in fixtures:
        timestamp = f["fixture"]["timestamp"]
        tz = f["fixture"]["timezone"]
        dt = datetime.fromtimestamp(timestamp, ZoneInfo(tz))
        if dt.minute == 0:
            tstr = dt.strftime("%I%p").lstrip("0")
        else:
            tstr = dt.strftime("%I:%M%p").lstrip("0")
        date_str = dt.strftime("%d/%m/%Y")

        league = f["league"]["name"]
        logo_league = f["league"]["logo"]
        country = f["league"]["country"]

        home = f["teams"]["home"]["name"]
        logo_home = f["teams"]["home"]["logo"]
        away = f["teams"]["away"]["name"]
        logo_away = f["teams"]["away"]["logo"]

        sh = f["score"]["fulltime"]["home"]
        sa = f["score"]["fulltime"]["away"]
        score_home = sh if sh is not None else "-"
        score_away = sa if sa is not None else "-"

        print(f"{date_str}  {tstr}: {country} {logo_league} {league}  "
              f"{logo_home} {home} {score_home}vs{score_away}  {logo_away} {away}")


def insert_matches_from_json(filename="footballdata.json"):
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)

    fixtures = data.get("response", [])
    for fxt in fixtures:
        # parse values from JSON (same as before)
        timestamp = fxt["fixture"]["timestamp"]
        tz = fxt["fixture"]["timezone"]
        dt = datetime.fromtimestamp(timestamp, ZoneInfo(tz))
        date_str = dt.strftime("%Y-%m-%d")
        if dt.minute == 0:
            tstr = dt.strftime("%I%p").lstrip("0")
        else:
            tstr = dt.strftime("%I:%M%p").lstrip("0")

        league = fxt["league"]["name"]
        logo_league = fxt["league"]["logo"]
        country = fxt["league"]["country"]

        home = fxt["teams"]["home"]["name"]
        logo_home = fxt["teams"]["home"]["logo"]
        away = fxt["teams"]["away"]["name"]
        logo_away = fxt["teams"]["away"]["logo"]

        sh = fxt["score"]["fulltime"]["home"]
        sa = fxt["score"]["fulltime"]["away"]
        score_home = sh if sh is not None else "-"
        score_away = sa if sa is not None else "-"

        cursor.execute("""
            INSERT INTO matches
            (date, time, country, league, logo_league,
             home_team, logo_home, away_team, logo_away,
             score_home, score_away)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (date_str, tstr, country, league, logo_league,
              home, logo_home, away, logo_away, score_home, score_away))

    connection.commit()
    print(f"Inserted {len(fixtures)} matches into the database.")

def show_matches_from_db(limit=10):
    cursor.execute("""
        SELECT date, time, country, league, logo_league,
               home_team, logo_home, away_team, logo_away,
               score_home, score_away
        FROM matches
        ORDER BY date, time
        LIMIT %s;
    """, (limit,))
    rows = cursor.fetchall()

    for row in rows:
        date_str, tstr, country, league, logo_league, home, logo_home, away, logo_away, score_home, score_away = row
        print(f"{date_str}  {tstr}: {country} {logo_league} {league}  "
              f"{logo_home} {home} {score_home}vs{score_away}  {logo_away} {away}")

#demonstrate database skillz

def test_data():
    test_users = [
        ("Lena", "Klein", "lena.klein@example.com", "Barcelona", "Austria", True),
        ("Jonas", "Müller", "jonas.mueller@example.com", "Real Madrid", "Germany", False),
        ("Sofia", "Novak", "sofia.novak@example.com", "Manchester City", "Hungary", True),
        ("David", "Horváth", "david.horvath@example.com", "Arsenal", "Hungary", True),
        ("Marta", "Kowalska", "marta.k@example.com", "Bayern Munich", "Poland", False),
        ("Elias", "Petrov", "elias.petrov@example.com", "Juventus", "Bulgaria", True),
        ("Chiara", "Rossi", "chiara.rossi@example.com", "AC Milan", "Italy", True),
        ("Mateo", "Santos", "mateo.santos@example.com", "Benfica", "Portugal", False),
        ("Amira", "Haddad", "amira.haddad@example.com", "PSG", "France", True),
        ("Omar", "Ali", "omar.ali@example.com", "Liverpool", "Egypt", True),
        ("Sven", "Larsson", "sven.larsson@example.com", "Ajax", "Sweden", False),
        ("Petra", "Novakova", "petra.novakova@example.com", "Slavia Prague", "Czech Republic", True),
        ("Lucas", "Smith", "lucas.smith@example.com", "Chelsea", "England", True),
        ("Isabella", "Brown", "isabella.brown@example.com", "Tottenham", "England", False),
        ("Yuki", "Tanaka", "yuki.tanaka@example.com", "Kashima Antlers", "Japan", True),
        ("Haruto", "Kobayashi", "haruto.k@example.com", "Urawa Red Diamonds", "Japan", True),
        ("Nina", "Ivanova", "nina.ivanova@example.com", "CSKA Moscow", "Russia", False),
        ("Andrei", "Popescu", "andrei.popescu@example.com", "Steaua Bucharest", "Romania", True),
        ("Fatima", "Karim", "fatima.karim@example.com", "Al Ahly", "Morocco", True),
        ("Aliyah", "Rahman", "aliyah.rahman@example.com", "Galatasaray", "Turkey", True),
        ("Noah", "Dubois", "noah.dubois@example.com", "Lyon", "France", False),
        ("Eva", "Bauer", "eva.bauer@example.com", "Borussia Dortmund", "Germany", True),
        ("Samuel", "Johnson", "samuel.johnson@example.com", "Manchester United", "England", True),
        ("Julia", "Garcia", "julia.garcia@example.com", "Atletico Madrid", "Spain", True),
        ("Diego", "Martinez", "diego.martinez@example.com", "Sevilla", "Spain", False),
        ("Clara", "Andersen", "clara.andersen@example.com", "FC Copenhagen", "Denmark", True),
        ("Henrik", "Olsen", "henrik.olsen@example.com", "Brøndby", "Denmark", True),
        ("Mohammed", "Saleh", "mohammed.saleh@example.com", "Zamalek", "Egypt", True),
        ("Anna", "Nieminen", "anna.nieminen@example.com", "HJK Helsinki", "Finland", False),
        ("Leo", "Virtanen", "leo.virtanen@example.com", "Inter Turku", "Finland", True),
            # ... (rest of the users here)
        ("Ava", "Green", "fan.crystalpalace@example.com", "Crystal Palace", "England", True),
        ("Lars", "Hansen", "fan.fredrikstad@example.com", "Fredrikstad", "Norway", False),
        ("Arman", "Petrosyan", "fan.fcnoah@example.com", "FC Noah", "Armenia", True),
        ("Nika", "Kranjc", "fan.olimpija@example.com", "Olimpija Ljubljana", "Slovenia", True),
        ("Eleni", "Ioannou", "fan.omonia@example.com", "Omonia Nicosia", "Cyprus", False),
        ("Sepp", "Gruber", "fan.wac@example.com", "Wolfsberger AC", "Austria", True),
        ("Majid", "Karimi", "fan.damac@example.com", "Damac", "Saudi Arabia", True),
        ("Fahd", "Al Harbi", "fan.alhazm@example.com", "Al-Hazm", "Saudi Arabia", False),
        ("Nikolai", "Sokolov", "fan.lokomotiv@example.com", "Lokomotiv", "Russia", True),
        ("Igor", "Morozov", "fan.akron@example.com", "Akron", "Russia", True),
        ("Karel", "Novák", "fan.sigmaolomouc@example.com", "Sigma Olomouc", "Czech Republic", True),
        ("Elsa", "Lind", "fan.malmoff@example.com", "Malmo FF", "Sweden", False),
        ("Luca", "Vella", "fan.hibernians@example.com", "Hibernians", "Malta", True),
        ("Maria", "Camilleri", "fan.birkirkara@example.com", "Birkirkara", "Malta", True),
        ("Tobias", "Wieser", "fan.weiz@example.com", "Weiz", "Austria", False),
        ("Felix", "Hofer", "fan.svlafnitz@example.com", "SV Lafnitz", "Austria", True),
        ("Can", "Kaya", "fan.samsunspor@example.com", "Samsunspor", "Turkey", True),
        ("Nikos", "Papadakis", "fan.panathinaikos@example.com", "Panathinaikos", "Greece", False),
        ("Emre", "Yilmaz", "fan.besiktas@example.com", "Besiktas", "Turkey", True),
        ("Léa", "Martin", "fan.lausanne@example.com", "Lausanne", "Switzerland", True),
        ("Arturs", "Ozols", "fan.rigasfs@example.com", "Rīgas FS", "Latvia", False),
        ("Matthew", "Grech", "fan.hamrun@example.com", "Hamrun Spartans", "Malta", True),
        ("Katharina", "Lehner", "fan.rapidvienna@example.com", "Rapid Vienna", "Austria", True),
        ("Bence", "Nagy", "fan.gyori@example.com", "Gyori ETO FC", "Hungary", False),
        ("Youssef", "Bennani", "fan.ittihadtanger@example.com", "Ittihad Tanger", "Morocco", True),
        ("Karim", "El Amrani", "fan.rajacasablanca@example.com", "Raja Casablanca", "Morocco", True),
        ("Hamad", "Al Thani", "fan.alsadd@example.com", "Al Sadd", "Qatar", False),
        ("Nadir", "Saleh", "fan.algharafa@example.com", "Al-Gharafa", "Qatar", True),
        ("Paul", "Durand", "fan.angouleme@example.com", "Angoulême", "France", True),
        ("Jean", "Moreau", "fan.bayonne@example.com", "Bayonne", "France", False),
        ("Ivaylo", "Ivanov", "fan.ludogorets@example.com", "Ludogorets", "Bulgaria", True),
        ("Marko", "Stojanovski", "fan.shkendija@example.com", "Shkendija", "North Macedonia", True),
        ("Giorgos", "Papas", "fan.paok@example.com", "PAOK", "Greece", False),
        ("Dario", "Horvat", "fan.rijeka@example.com", "HNK Rijeka", "Croatia", True),
        ("Jesse", "Bakker", "fan.azalkmaar@example.com", "AZ Alkmaar", "Netherlands", True),
        ("Stoyan", "Dimitrov", "fan.levskisofia@example.com", "Levski Sofia", "Bulgaria", False),
        ("Radu", "Ionescu", "fan.cfrcluj@example.com", "CFR 1907 Cluj", "Romania", True),
        ("Oskar", "Svensson", "fan.bkhacken@example.com", "BK Hacken", "Sweden", True),
        ("Mihai", "Popa", "fan.craiova@example.com", "Universitatea Craiova", "Romania", False),
        ("Kerem", "Demir", "fan.basaksehir@example.com", "Istanbul Basaksehir", "Turkey", True),
        ("Alessia", "Bianchi", "fan.fiorentina@example.com", "Fiorentina", "Italy", True),
        ("Olena", "Kovalenko", "fan.polessya@example.com", "Polessya", "Ukraine", False),
        ("Dimitris", "Nikolaou", "fan.aekathens@example.com", "AEK Athens FC", "Greece", True),
        ("Tom", "Vermeulen", "fan.anderlecht@example.com", "Anderlecht", "Belgium", True),
        ("Raul", "Santos", "fan.rayovallecano@example.com", "Rayo Vallecano", "Spain", False),
        ("Aliaksandr", "Kuznetsov", "fan.neman@example.com", "Neman", "Belarus", True),
        ("Mikkel", "Jensen", "fan.brondby@example.com", "Brondby", "Denmark", True),
        ("Claire", "Roche", "fan.strasbourg@example.com", "Strasbourg", "France", False),
    ]

    for user in test_users:
        cursor.execute("""
            INSERT INTO users (first_name, last_name, email, favorite_team, country, outreach_okay)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (email) DO NOTHING;
        """, user)

    connection.commit()
    print(f"Inserted {len(test_users)} dummy users into the database.")
# Main program flow
def main():
    print("Connection works.")
    ## run test users just this time
    #test_data()
    ans = input("Is this your first time here? (YES / NO): ").strip().upper()
    if ans == "YES":
        first = input("First name: ")
        last = input("Last name: ")
        email = input("Email: ")
        fav_team = input("Favorite team: ")
        country = input("Country: ")
        outreach = input("Receive alerts? (YES / NO): ").strip().upper()
        outreach_bool = (outreach == "YES")

        try:
            cursor.execute("""
                INSERT INTO users (first_name, last_name, email, favorite_team, country, outreach_okay)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (email) DO NOTHING;
            """, (first, last, email, fav_team, country, outreach_bool))
            connection.commit()
            print("Registered successfully.")
        except Exception as e:
            connection.rollback()
            print("Could not register user:", e)

    # after registration or login, fetch and display fixtures
    get_data(API_KEY,
             filename="footballdata.json",
             timezone="Europe/Vienna",
             tonight_only=True)

    # wipe old rows
    cursor.execute("TRUNCATE TABLE matches RESTART IDENTITY;")
    connection.commit()
# NEW STEP: insert those fixtures from JSON into the DB
    insert_matches_from_json("footballdata.json")

    # show matches back from DB in the same format
    print("\nMatches from the database:")
    show_matches_from_db(limit=20)
    
    cursor.close()
    connection.close()


if __name__ == "__main__":
    main()
