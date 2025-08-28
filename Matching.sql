-- Normalize times once (e.g., '6PM' -> '6:00PM') if needed
UPDATE matches
SET time = left(time, length(time)-2) || ':00' || right(time, 2)
WHERE position(':' in time) = 0

-- Upcoming matches with fans, pretty kickoff string
WITH joined AS (
  SELECT
    (m.date::date + m.time::time) AT TIME ZONE 'Europe/Vienna' AS ts_vie,
    m.league,
    m.home_team,
    m.away_team,
    u.first_name,
    u.last_name
  FROM matches m
  JOIN users u
    ON u.favorite_team = m.home_team
    OR u.favorite_team = m.away_team
  WHERE (m.date::date + m.time::time) AT TIME ZONE 'Europe/Vienna'
        >= (NOW() AT TIME ZONE 'Europe/Vienna')
)
SELECT
  -- "28 August - 8PM" (or "8:30PM" if minutes exist)
  to_char(ts_vie, 'DD FMMonth') || ' - ' ||
  CASE
    WHEN date_part('minute', ts_vie) = 0
      THEN to_char(ts_vie, 'FMHH12AM')
    ELSE to_char(ts_vie, 'FMHH12:MIAM')
  END AS kickoff_local,
  league,
  (home_team || ' vs ' || away_team) AS all_teams,
  STRING_AGG(
    DISTINCT CONCAT_WS(' ', first_name, last_name),
    ', ' ORDER BY CONCAT_WS(' ', first_name, last_name)
  ) AS users
FROM joined
GROUP BY 1, 2, 3
ORDER BY MIN(ts_vie), league, all_teams

--create email to alert the user
SELECT
  u.email                                          AS email_to,
  'Match reminder for ' || u.favorite_team         AS subject,
  'Dear ' || u.first_name || ', Your favorite team ' || u.favorite_team ||
  ' is playing tonight at ' ||
  to_char(m.date::date, 'DD FMMonth') || ' ' || m.time ||
  '. Are you Ready for Kickoff?!'
  AS body
FROM users u
JOIN matches m
  ON u.favorite_team = m.home_team
  OR u.favorite_team = m.away_team
WHERE m.date::date = CURRENT_DATE
ORDER BY u.email, m.date, m.time;

-- most popular team
SELECT
  favorite_team AS team,
  COUNT(*)      AS fans
FROM users
WHERE favorite_team IS NOT NULL AND favorite_team <> ''
GROUP BY favorite_team
ORDER BY fans DESC;


-- (Only if you still have raw '6PM' values; run once)
UPDATE matches
SET time = left(time, length(time)-2) || ':00' || right(time, 2)
WHERE position(':' in time) = 0;
