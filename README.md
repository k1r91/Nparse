This is virtual environment for test project.
Project is in nparse/nparse directory
Do not forget to run commands for grant privileges for user 'nasdaq':

# create database
psql -U posgres;
CREATE DATABASE nasdaq; 
# create user
alter user nasdaq with encrypted password '<password>';

# grant privileges
psql nasdaq postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public to nasdaq;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public to nasdaq;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public to nasdaq;