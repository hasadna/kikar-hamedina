set -e
sudo -u postgres psql -c "DROP DATABASE IF EXISTS kikar"
sudo -u postgres psql -c "DROP ROLE IF EXISTS kikar"
sudo -u postgres psql -c "DROP ROLE IF EXISTS kikar_readonly"
sudo -u postgres psql -c "CREATE USER kikar WITH PASSWORD 'kikar'"
sudo -u postgres psql -c "CREATE USER kikar_readonly WITH PASSWORD 'kikar_readonly'"
sudo -u postgres psql -c "ALTER USER kikar WITH SUPERUSER"
sudo -u postgres psql -c "CREATE DATABASE kikar TEMPLATE=template0 ENCODING='UTF8' LC_CTYPE='en_US.utf8' LC_COLLATE='en_US.UTF-8'"
