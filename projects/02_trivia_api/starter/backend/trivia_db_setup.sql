DROP DATABASE IF EXISTS trivia;
DROP USER IF EXISTS caryn;
CREATE DATABASE trivia;
CREATE USER caryn WITH ENCRYPTED PASSWORD 'caryn';
GRANT ALL PRIVILEGES ON DATABASE trivia TO caryn;
ALTER USER caryn CREATEDB;
ALTER USER caryn WITH SUPERUSER;