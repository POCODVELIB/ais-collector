import os
from snowflake.connector import connect

def get_connection():
    return connect(
        user      = os.environ["SF_USER"],
        password  = os.environ["SF_PASSWORD"],
        account   = os.environ["SF_ACCOUNT"],
        warehouse = os.environ["SF_WAREHOUSE"],
        database  = os.environ["SF_DATABASE"],
        schema    = os.environ["SF_SCHEMA"],
    )