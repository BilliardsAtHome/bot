from database import Database

class UserDB(Database):
    TABLE_NAME = "users"
    TABLE_SCHEMA = f"""CREATE TABLE {TABLE_NAME}(
                        discord char(18),
                        id      int
                    )"""
    
    BOT_ID = "1209240468605509634"

    def __init__(self, path: str):
        super().__init__(path)

    #
    #
    # Get a user's Discord ID from their unique ID.
    #
    # If the unique ID has not been registered,
    # this function returns the bot's Discord ID.
    #
    # Returns:
    #   Corresponding Discord ID
    #
    #
    def get_discord_id(self, unique_id: int) -> str:
        command = f"""SELECT * FROM {self.TABLE_NAME} WHERE id = ?"""
        self.cursor.execute(command, (unique_id,))
        result = self.cursor.fetchone()
        return self.BOT_ID if not result else result[0]

    #
    #
    # Add a new Discord ID to the database.
    #
    # If the Discord ID is already registered,
    # this function returns the previous unique ID.
    #
    # Returns:
    #   Newly generated unique ID
    #
    #
    def add_discord_id(self, discord_id: str) -> int:
        # Check if the ID has already been registered
        command = f"""SELECT id FROM {self.TABLE_NAME} WHERE discord = ?"""
        self.cursor.execute(command, (discord_id,))
        if result := self.cursor.fetchone():
            return result[0]

        # Get the next sequential ID
        command = f"""SELECT COUNT (*) FROM {self.TABLE_NAME}"""
        self.cursor.execute(command)
        result = self.cursor.fetchone()
        unique_id = 0 if not result else result[0]

        # Create new entry
        command = f"""INSERT INTO {self.TABLE_NAME} VALUES (?, ?)"""
        self.cursor.execute(command, (discord_id, unique_id,))
        self.connection.commit()
        return unique_id
