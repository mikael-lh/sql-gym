CREATE ROLE sql_gym_readonly LOGIN PASSWORD 'readonly';
GRANT CONNECT ON DATABASE sqlgym TO sql_gym_readonly;
GRANT USAGE ON SCHEMA public TO sql_gym_readonly;
GRANT SELECT ON times_archive TO sql_gym_readonly;

CREATE ROLE sql_gym_app LOGIN PASSWORD 'app';
GRANT CONNECT ON DATABASE sqlgym TO sql_gym_app;
GRANT USAGE ON SCHEMA public TO sql_gym_app;
GRANT SELECT ON times_archive TO sql_gym_app;
