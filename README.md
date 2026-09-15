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