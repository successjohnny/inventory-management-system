# step 1
python3 -m venv .venv

# step 2
source .venv/bin/activate

# step 3
pip install -r requirement.txt

# step 4 
pip install sqlalchemy

# step 5
pip install alembic
alembic --version
alembic init alembic

## our first migration
bash: alembic revision --autogenerate -m "initial database"
check migration py file for upgrade or downgrade
bash: alembic upgrade head

# step 6
pip install pytest

# step 7
pip install httpx2

pip freeze > requirements.txt
cat requirements.txt

# step 8
python -m pip install itsdangerous
python -m pip freeze | grep -i '^itsdangerous=='

# step 9 Install the PostgreSQL driver
python -m pip install "psycopg[binary]"

# step 10 Install PostgreSQL backup tools
sudo apt update
sudo apt install postgresql-client
Do you want to continue? [Y/n]

# step 11 backup command
bash "$HOME/inventory-backups/scripts/backup.sh"