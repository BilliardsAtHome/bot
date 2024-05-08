from sqlite3 import connect, OperationalError
from dataclasses import astuple


class Database:
    def __init__(self, path: str):
        self.connection = None
        self.open(path)

    #
    #
    # Open the database, creating the file if it doesn't exist
    #
    #
    def open(self, path: str):
        # Close existing database
        if self.connection != None:
            self.connection.close()
            self.connection = None

        # Establish connection with database
        self.connection = connect(path)
        self.cursor = self.connection.cursor()

        # Create table for breaks
        try:
            self.cursor.execute(self.TABLE_SCHEMA)
        except OperationalError:
            # Table already exists
            pass

    #
    #
    # Add an entry to the database
    #
    #
    def add(self, info):
        values = astuple(info)
        command = f"INSERT INTO {self.TABLE_NAME} VALUES {values}"

        self.cursor.execute(command)
        self.connection.commit()

    #
    #
    # Remove database entries.
    #
    # Returns:
    #   Number of entries removed
    #
    #
    def remove(self, where: str) -> int:
        assert not where.isspace() and len(where) > 0, "This will delete the entire table!"

        command = f"DELETE FROM {self.TABLE_NAME} WHERE {where}"

        self.cursor.execute(command)
        self.connection.commit()

        return self.cursor.rowcount

    #
    #
    # Filter database entries.
    #
    # Returns:
    #   Search results copied from the DB
    #
    #
    def filter(self, where: str, args: tuple = ()) -> list:
        command = f"SELECT * FROM {self.TABLE_NAME} WHERE {where}"

        self.cursor.execute(command, (*args,))

        return self.cursor.fetchall()

    #
    #
    # Get top database entries fulfulling a certain condition.
    #
    # Returns:
    #   Search results copied from the DB
    #
    #
    def top(self, count: int, where: str, args: tuple = ()) -> list:
        command = f"SELECT * FROM {self.TABLE_NAME} WHERE {where} LIMIT {count}"

        self.cursor.execute(command, (*args,))

        return self.cursor.fetchall()

    #
    #
    # Count database entries fulfilling a certain condition.
    #
    # Returns:
    #   Number of search results
    #
    #
    def count(self, where: str, args: tuple = ()) -> int:
        command = f"SELECT COUNT (*) FROM {self.TABLE_NAME} WHERE {where}"

        self.cursor.execute(command, (*args,))

        result = self.cursor.fetchone()
        return 0 if not result else result[0]
