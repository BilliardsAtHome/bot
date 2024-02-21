class BreakInfo:
    # Fields in both the SQL table and the Python object.
    # (Order-sensitive and case-sensitive)
    FIELDS = [
        "user",
        "timestamp",
        "seed",
        "kseed",
        "sunk",
        "off",
        "frame",
        "up",
        "left",
        "right",
        "posx",
        "posy",
        "power",
        "foul"
    ]

    def __init__(self, args):
        # Convert list/tuple to dictionary
        if type(args) != dict:
            # (0123, 1, 0xABCD) -> {user : 0123, timestamp : 1, seed : 0xABCD}
            args = dict((key, value)
                        for key, value in zip(self.FIELDS, args))

        # Read from the dictionary
        self.unpack(args)

    def unpack(self, args: dict):
        self.user = args["user"]
        self.timestamp = 0
        self.seed = args["seed"]
        self.kseed = args["kseed"]
        self.sunk = args["sunk"]
        self.off = args["off"]
        self.frame = args["frame"]
        self.up = args["up"]
        self.left = args["left"]
        self.right = args["right"]
        self.posx = args["posx"]
        self.posy = args["posy"]
        self.power = args["power"]
        self.foul = args["foul"]

    def __repr__(self):
        return f"{self.user} {self.seed} {self.kseed} {self.sunk} {self.off} {self.frame} {self.up} {self.left} {self.right} {self.posX} {self.posY} {self.power} {self.foul} {self.checksum}"
