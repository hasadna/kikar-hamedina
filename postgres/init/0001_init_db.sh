set -e
psql -U postgres -c "DROP DATABASE IF EXISTS kikar"
psql -U postgres -c "DROP ROLE IF EXISTS kikar"
psql -U postgres -c "DROP ROLE IF EXISTS kikar_readonly"
psql -U postgres -c "CREATE USER kikar WITH PASSWORD 'kikar'"
psql -U postgres -c "CREATE USER kikar_readonly WITH PASSWORD 'kikar_readonly'"
psql -U postgres -c "ALTER USER kikar WITH SUPERUSER"
psql -U postgres -c "CREATE DATABASE kikar TEMPLATE=template0 ENCODING='UTF8' LC_CTYPE='en_US.utf8' LC_COLLATE='en_US.UTF-8'"
