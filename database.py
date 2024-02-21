from sqlite3 import connect, OperationalError
from break_info import BreakInfo
from dataclasses import fields, astuple


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
            self.cursor.execute(
                """CREATE TABLE break(
                    user      char(18),
                    seed      int,
                    kseed     int,
                    sunk      tinyint,
                    off       tinyint,
                    frame     smallint,
                    up        tinyint,
                    left      tinyint,
                    right     tinyint,
                    posx      int,
                    posy      int,
                    power     int,
                    foul      bit,
                    timestamp int
                )""")
        except OperationalError:
            # Table already exists
            pass

    #
    #
    # Add a break to the database
    #
    #
    def add(self, info: BreakInfo):
        values = astuple(info)
        command = f"INSERT INTO break VALUES {values}"

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

        command = f"DELETE FROM break WHERE {where}"

        self.cursor.execute(command)
        self.connection.commit()

        return self.cursor.rowcount

    #
    #
    # Filter database entries.
    #
    # Returns:
    #   Search results (BreakInfo) copied from the DB
    #
    #
    def filter(self, where: str) -> list:
        command = f"SELECT * FROM break WHERE {where}"

        self.cursor.execute(command)

        return [BreakInfo(*row) for row in self.cursor.fetchall()]

    #
    #
    # Update certain fields in existing database entries.
    #
    # Returns:
    #   Number of entries changed
    #
    #
    def update(self, where: str, values: dict) -> int:
        assert len(where) > 0, "This will update the entire table!"

        # Convert dictionary to SQL command syntax
        # {name1 : "value1", name2 : "value2"} -> name1="value1", name2="value2"
        params = ", ".join([f"{key}={value}"
                            for key, value in values.items()])

        command = f"UPDATE break SET {params} WHERE {where}"

        self.cursor.execute(command)
        self.connection.commit()

        return self.cursor.rowcount

    #
    #
    # Replace existing database entries.
    #
    # Returns:
    #   Number of entries replaced
    #
    #
    def replace(self, where: str, info: BreakInfo) -> int:
        assert len(where) > 0, "This will replace the entire table!"

        # Convert BreakInfo to SQL command syntax
        # user="10920192", seed="0x12345678", etc.
        params = ", ".join([f"{field.name}={getattr(info, field.name)}"
                            for field in fields(info)])

        command = f"UPDATE break SET {params} WHERE {where}"

        self.cursor.execute(command)
        self.connection.commit()

        return self.cursor.rowcount
