from sqlite3 import connect, OperationalError
from break_info import BreakInfo


class Database:
    def __init__(self, path: str):
        self.connection = None
        self.open(path)

    def open(self, path: str):
        """Open the database, creating the file if it doesn't exist.
        """

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
                    timestamp DATETIME,
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
                    foul      bit
                )""")
        except OperationalError:
            # Table already exists
            pass

    def add(self, info: BreakInfo):
        """Add a break to the database.
        """

        values = tuple(info.__dict__.values())
        command = f"INSERT INTO break VALUES {values}"

        self.cursor.execute(command)
        self.connection.commit()

    def remove(self, where: str) -> int:
        """Remove database entries.
        Returns:
            Number of entries removed
        """
        assert len(where) > 0 and not where.isspace(
        ), "This will delete the entire table!"

        command = f"DELETE FROM break WHERE {where}"

        self.cursor.execute(command)
        self.connection.commit()

        return self.cursor.rowcount

    def filter(self, where: str) -> list:
        """Filter database entries.
        Returns:
            Search results (converted to BreakInfo)
        """

        command = f"SELECT * FROM break WHERE {where}"

        self.cursor.execute(command)

        return [BreakInfo(row)
                for row in self.cursor.fetchall()]

    def update(self, where: str, values: dict) -> int:
        """Update certain fields in existing database entries.
        Returns:
            Number of entries changed
        """

        assert len(where) > 0, "This will update the entire table!"

        params = ", ".join([f"{key}={value}"
                            for key, value in values.items()])
        command = f"UPDATE break SET {params} WHERE {where}"

        self.cursor.execute(command)
        self.connection.commit()

        return self.cursor.rowcount

    def replace(self, where: str, info: BreakInfo) -> int:
        """Replace existing database entries.
        Returns:
            Number of entries replaced
        """

        assert len(where) > 0, "This will replace the entire table!"

        params = ", ".join([f"{key}={value}"
                           for key, value in info.__dict__.items()])
        command = f"UPDATE break SET {params} WHERE {where}"

        self.cursor.execute(command)
        self.connection.commit()

        return self.cursor.rowcount


"""
Example code:


dummy_data = {'user': '109888805842968576', 'seed': 2863311530, 'kseed': 3149642683, 'sunk': 7, 'off': 3, 'frame': 11,
              'up': 1, 'left': 2, 'right': 3, 'posx': 1065353216, 'posy': 0, 'power': 1099104256, 'foul': True, 'timestamp': None}

d = Database("dummy.db")
info = BreakInfo(dummy_data)

# Add new entries
d.add(info)
d.add(info)
d.add(info)

# Replace existing entries
info.frame = 999
num_replaced = d.replace(
    where="user = 109888805842968576", info=info)

# Update fields in existing entries
num_updated = d.update(
    where="user = 109888805842968576",
    values={"user": "123456789012345678"})

# Filter existing entries
results = d.filter("frame = 999")

# Remove existing entries
num_removed = d.remove("sunk < 8")

"""
