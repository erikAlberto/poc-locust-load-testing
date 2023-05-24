import psycopg2
import configparser
from psycopg2 import Error

config = configparser.ConfigParser()
config.read('database.ini')

class PostgreSqlDatabase:
    def __init__(self):
        self.user = config['TESTING']['DB_USER']
        self.password = config['TESTING']['DB_PASSWORD']
        self.host = config['TESTING']['DB_HOST']
        self.port = config['TESTING']['DB_PORT']
        self.database = config['TESTING']['DB_NAME']
        self.connection = None

    def connection_database(self):
        try:
            # Connect to an existing database

            self.connection = psycopg2.connect(
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
                database=self.database)

        except (Exception, Error) as error:
            print("Error while connecting to PostgreSQL", error)

    def close_connection(self):
        if (self.connection):
                #cursor.close()
                self.connection.close()
                print("PostgreSQL connection is closed")

    def select_from_database(self, query):
        # Create a cursor to perform database operations
        cursor = self.connection.cursor()
        # Executing a SQL query
        cursor.execute(query)
        # Fetch result
        record = cursor.fetchone()
        print("You are connected to - ", record)
        return record
