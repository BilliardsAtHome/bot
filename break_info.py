from dataclasses import dataclass, fields
from functools import total_ordering


"""
From values -> BreakInfo(user, seed, kseed, ...)
From tuple  -> BreakInfo(*the_tuple)
From dict   -> BreakInfo(**the_dict)
"""


@dataclass(eq=False, order=False)
@total_ordering
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

    checksum: int

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
                # Expect integer values for booleans
                elif field.type == bool:
                    if type(member) == str:
                        member = int(member, base=0)

                    setattr(self, field.name, bool(member))
                # Some other type, cast normally
                else:
                    setattr(self, field.name, field.type(member))

    #
    # Equal operator
    #
    def __eq__(self, other: "BreakInfo") -> bool:
        if other == None:
            return False
        return (self.sunk == other.sunk
                and self.off == other.off
                and self.foul == other.foul
                and self.frame == other.frame)

    #
    # Greater-than operator
    #
    def __gt__(self, other: "BreakInfo") -> bool:
        if other == None:
            return True
        self_total = self.sunk + self.off
        other_total = other.sunk + other.off

        # Compare total balls out of play
        if self_total != other_total:
            return self_total > other_total

        # Compare balls pocketed
        if self.sunk != other.sunk:
            return self.sunk > other.sunk

        # Compare foul
        if self.foul != other.foul:
            return self.foul == False

        # Compare frame count
        if self.frame != other.frame:
            return self.frame < other.frame

        return False

    def __repr__(self):
        return str(self.__dict__)

    # Compute checksum of this break
    def calcChecksum(self) -> int:
        sum = invsum = 0

        for field in fields(self):
            # dont touch user id
            if field.name == "user":
                continue
            # everything at/below checksum is ignored
            if field.name == "checksum":
                break

            value = int(getattr(self, field.name))

            # lower 16
            sum += (value & 0xFFFF)
            invsum += ~(value & 0xFFFF)

            # higher 16 (when applicable)
            if field.type == int:
                sum += (value >> 16 & 0xFFFF)
                invsum += ~(value >> 16 & 0xFFFF)

        return (sum << 16 | invsum) & 0xFFFFFFFF

    # X component of aim for Gecko code
    def getAimX(self):
        if self.right > 0:
            return self.right
        else:
            return self.left * -1
