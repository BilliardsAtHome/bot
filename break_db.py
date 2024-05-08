from break_info import BreakInfo
from dataclasses import fields, astuple
from database import Database

class BreakDB(Database):
    TABLE_NAME = "break"
    TABLE_SCHEMA = f"""CREATE TABLE {TABLE_NAME}(
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
                    )"""

    def __init__(self, path: str):
        super().__init__(path)

    #
    #
    # Check if a user is in the database
    #
    #
    def contains_user(self, user: str) -> bool:
        command = f"SELECT COUNT (*) FROM break WHERE user = ?"

        self.cursor.execute(command, (user,))
        result = self.cursor.fetchone()

        count = 0 if not result else result[0]
        return count > 0

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
        command = f"""SELECT * FROM break WHERE user = ?
        ORDER BY (sunk + off) DESC, sunk DESC, foul ASC, frame ASC"""

        self.cursor.execute(command, (user,))

        return [BreakInfo(*row) for row in self.cursor.fetchall()]

    #
    #
    # Obtain all records in database
    #
    # Returns:
    #   List of all entries in database
    #
    #
    def get_top_10(self) -> list:
        command = f"""SELECT * FROM break
        ORDER BY (sunk + off) DESC, sunk DESC, foul ASC, frame 
        ASC LIMIT 10"""

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
        command = f"""SELECT * FROM break WHERE user = ?
        ORDER BY (sunk + off) DESC, sunk DESC, foul ASC, frame ASC
        LIMIT 1"""

        self.cursor.execute(command, (user,))

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
        if info > old:
            self.replace(old, info)
            return old

    #
    #
    # Obtain best record across all users
    #
    # Returns:
    #   Search result (BreakInfo) copied from the DB
    #   (None if there are no results)
    #
    #
    def get_global_best(self) -> BreakInfo:
        command = """SELECT * FROM break
        ORDER BY (sunk + off) DESC, sunk DESC, foul ASC, frame ASC
        LIMIT 1"""

        self.cursor.execute(command)

        result = self.cursor.fetchone()
        return None if not result else BreakInfo(*result)

    #
    #
    # Obtain best record at/before a specified timestamp
    #
    # Returns:
    #   Search result (BreakInfo) copied from the DB
    #   (None if there are no results)
    #
    #
    def get_global_best_at_before(self, timestamp: int) -> BreakInfo:
        command = f"""SELECT * FROM break WHERE timestamp <= {timestamp}
        ORDER BY (sunk + off) DESC, sunk DESC, foul ASC, frame ASC
        LIMIT 1"""

        self.cursor.execute(command)

        result = self.cursor.fetchone()
        return None if not result else BreakInfo(*result)

    #
    #
    # Obtain best record since a specified timestamp
    #
    # Returns:
    #   Search result (BreakInfo) copied from the DB
    #   (None if there has not been a new record)
    #
    #
    def get_new_global_best(self, last_time: int) -> BreakInfo:
        best_before = self.get_global_best_at_before(last_time)
        best_ever = self.get_global_best()
        return best_ever if best_before != best_ever else None

    #
    #
    # Filter database entries.
    #
    # Returns:
    #   Search results (BreakInfo) copied from the DB
    #
    #
    def filter(self, where: str, args: tuple = ()) -> list:
        return [BreakInfo(*row) for row in
                Database.filter(self, where, args)]


    #
    #
    # Get top database entries fulfulling a certain condition.
    #
    # Returns:
    #   Search results (BreakInfo) copied from the DB
    #
    #
    def top(self, count: int, where: str, args: tuple = ()) -> list:
        return [BreakInfo(*row) for row in
                Database.top(self, count, where, args)]

    #
    #
    # Replace existing database entries.
    #
    # Returns:
    #   Number of entries replaced
    #
    #
    def replace(self, old: BreakInfo, new: BreakInfo) -> int:
        command = f"UPDATE break SET "
        command += ", ".join([f"{x.name} = ?" for x in fields(new)])

        command += " WHERE "
        command += " AND ".join([f"{x.name} = ?" for x in fields(old)])

        params = (*astuple(new), *astuple(old),)

        self.cursor.execute(command, (*params,))
        self.connection.commit()

        return self.cursor.rowcount
