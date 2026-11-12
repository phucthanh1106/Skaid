from app import config
import mysql.connector

# Open a database connection per request and always close it.
def get_database():
    connection = mysql.connector.connect(
        host=config.MYSQL_HOST,
        port=config.MYSQL_PORT,
        user=config.MYSQL_USER,
        password=config.MYSQL_PASSWORD,
        database=config.MYSQL_DATABASE
    )
    
    try:
        yield connection
    finally:
        connection.close()