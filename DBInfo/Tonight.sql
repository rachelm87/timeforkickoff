SELECT * FROM public.matches
ORDER BY match_id ASC;

-- (Only if you still have raw '6PM' values; run once)
UPDATE public.matches
SET time = left(time, length(time)-2) || ':00' || right(time, 2)
WHERE position(':' in time) = 0;

-- Tonight = today after 18:00
SELECT
  to_char(m.date::date, 'DD FMMonth') || ' - ' ||
  CASE
    WHEN date_part('minute', m.time::time) = 0
      THEN to_char(m.time::time, 'FMHH12AM')     -- 8PM
    ELSE to_char(m.time::time, 'FMHH12:MIAM')    -- 8:30PM
  END || ' — ' || m.league || ': ' || m.home_team || ' vs ' || m.away_team
  AS pretty_line
FROM matches m
WHERE m.date::date = CURRENT_DATE
  AND m.time::time >= TIME '18:00'
ORDER BY m.time::time, m.league, m.home_team;