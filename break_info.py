from dataclasses import dataclass, fields


"""
From values -> BreakInfo(user, seed, kseed, ...)
From tuple  -> BreakInfo(*the_tuple)
From dict   -> BreakInfo(**the_dict)
"""


@dataclass
class BreakInfo:
    user: str  # Discord user ID

    seed: int   # RP random seed (for balls)
    kseed: int  # libkiwi random seed (for simulation)

    sunk: int  # Balls pocketed
    off: int   # Balls shot off the table

    frame: int  # Shot frame count
    up: int     # Frames aimed up
    left: int   # Frames aimed left
    right: int  # Frames aimed right

    posx: int   # Cue X position
    posy: int   # Cue Y position
    power: int  # Cue power

    foul: bool  # One or more fouls occurred

    timestamp: int = 0  # Submission timestamp

    #
    # Enforces type checking (automatically called by __init__)
    #
    def __post_init__(self):
        for field in fields(self):
            # Real class member
            member = getattr(self, field.name)

            # Try to convert to the expected type.
            # If this fails it will raise an exception.
            if not isinstance(member, field.type):

                # Don't default to base 10 for integers
                if field.type == int:
                    setattr(self, field.name, int(member, base=0))
                # Some other type, cast normally
                else:
                    setattr(self, field.name, field.type(member))

    def __repr__(self):
        return str(self.__dict__)
