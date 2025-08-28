--all users
SELECT * FROM users;

--cap at first 30 based on id
SELECT * FROM users LIMIT 30;

--users by country
SELECT * FROM users 
ORDER by country asc;