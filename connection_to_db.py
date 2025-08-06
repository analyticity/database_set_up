import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()

conn_params_brno = {
    "host": 'localhost',
    "port": 5433,
    "dbname": os.getenv("POSTGRES_DB_BRNO"),
    "user": os.getenv("POSTGRES_USER_BRNO"),
    "password": os.getenv("POSTGRES_PASSWORD_BRNO")
}

CONN_BRNO = psycopg2.connect(**conn_params_brno)


conn_params_jmk = {
    "host": 'localhost',
    "port": 5434,
    "dbname": os.getenv("POSTGRES_DB_JMK"),
    "user": os.getenv("POSTGRES_USER_JMK"),
    "password": os.getenv("POSTGRES_PASSWORD_JMK")
}

CONN_JMK = psycopg2.connect(**conn_params_jmk)


conn_params_most = {
    "host": 'localhost',
    "port": 5435,
    "dbname": os.getenv("POSTGRES_DB_ORP_MOST"),
    "user": os.getenv("POSTGRES_USER_ORP_MOST"),
    "password": os.getenv("POSTGRES_PASSWORD_ORP_MOST")
}

CONN_ORP_MOST = psycopg2.connect(**conn_params_most)


conn_params_central = {
    "host": 'localhost',
    "port": 5431,
    "dbname": os.getenv("POSTGRES_DB_CENTRAL"),
    "user": os.getenv("POSTGRES_USER_CENTRAL"),
    "password": os.getenv("POSTGRES_PASSWORD_CENTRAL")
}

CONN_CENTRAL = psycopg2.connect(**conn_params_central)