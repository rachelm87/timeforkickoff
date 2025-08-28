CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(200) UNIQUE,
    favorite_team VARCHAR(100),
    country VARCHAR(100),
    outreach_okay BOOLEAN
);

CREATE TABLE IF NOT EXISTS matches (
    match_id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    time VARCHAR(20) NOT NULL,
    country VARCHAR(100),
    league VARCHAR(100),
    logo_league TEXT,
    home_team VARCHAR(100),
    logo_home TEXT,
    away_team VARCHAR(100),
    logo_away TEXT,
    score_home VARCHAR(10),
    score_away VARCHAR(10)
);