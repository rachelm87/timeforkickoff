-- Normalize times once (e.g., '6PM' -> '6:00PM') if needed
UPDATE matches
SET time = left(time, length(time)-2) || ':00' || right(time, 2)
WHERE position(':' in time) = 0;

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
ORDER BY MIN(ts_vie), league, all_teams;