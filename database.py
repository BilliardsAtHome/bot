from sqlite3 import connect, OperationalError
from break_info import BreakInfo
from dataclasses import fields, astuple, asdict
from random import randint


#
# Convert dictionary to SET command values
#
def dict_to_sql_set(d):
    # {name1 : "value1", name2 : "value2"} -> name1="value1", name2="value2"
    return ", ".join([f"{key}={value}"
                      for key, value in d.items()])


#
# Convert dictionary to SET command values
#
def dict_to_sql_where(d):
    # {name1 : "value1", name2 : "value2"} -> name1="value1" AND name2="value2"
    return " AND ".join([f"{key}={value}"
                         for key, value in d.items()])


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
                    checksum  int,
                    timestamp int
                )""")
        except OperationalError:
            # Table already exists
            pass

    """
    ===========================================================================

                                Functions by user

    ===========================================================================
    """

    #
    #
    # Check if a user is in the database
    #
    #
    def contains_user(self, user: str) -> bool:
        return self.count(f"user = {user}") > 0

    #
    #
    # Obtain all records by user ID
    #
    # Returns:
    #   Search results (BreakInfo) copied from the DB.
    #   Results are sorted in descending order.
    #
    #
    def get_user_all(self, user: str) -> list:
        command = f"""SELECT * FROM break WHERE user = {user}
        ORDER BY (sunk + off) DESC, sunk DESC, foul ASC, frame ASC"""

        self.cursor.execute(command)

        return [BreakInfo(*row) for row in self.cursor.fetchall()]

    #
    #
    # Obtain best record by user ID
    #
    # Returns:
    #   Search result (BreakInfo) copied from the DB
    #
    #
    def get_user_best(self, user: str) -> BreakInfo:
        command = f"""SELECT * FROM break WHERE user = {user}
        ORDER BY (sunk + off) DESC, sunk DESC, foul ASC, frame ASC
        LIMIT 1"""

        self.cursor.execute(command)

        result = self.cursor.fetchone()
        return None if not result else BreakInfo(*result)

    #
    #
    # Update best record by user ID
    #
    # Returns:
    #   Old best record
    #
    #
    def set_user_best(self, info: BreakInfo):
        old = self.get_user_best(info.user)

        # Nothing in the DB from this user
        if not old:
            self.add(info)
            return None

        # Replace old entry
        where = dict_to_sql_where(asdict(old))
        self.replace(where, info)
        return old

    """
    ===========================================================================

                                   SQL commands

    ===========================================================================
    """

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
    # Get top database entries fulfulling a certain condition.
    #
    # Returns:
    #   Search results (BreakInfo) copied from the DB
    #
    #
    def top(self, count: int, where: str) -> list:
        command = f"SELECT * FROM break WHERE {where} LIMIT {count}"

        self.cursor.execute(command)

        return [BreakInfo(*row) for row in self.cursor.fetchall()]

    #
    #
    # Count database entries fulfilling a certain condition.
    #
    # Returns:
    #   Search results (BreakInfo) copied from the DB
    #
    #
    def count(self, where: str) -> int:
        command = f"SELECT COUNT (*) FROM break WHERE {where}"

        self.cursor.execute(command)

        result = self.cursor.fetchone()
        return 0 if not result else result[0]

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

        params = dict_to_sql_set(values)
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
