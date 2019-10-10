from dataclasses import dataclass, asdict
import serialtest


@dataclass
class LocationData:
    x: float
    y: float
    z: float

    def get_as_dict(self):
        return asdict(self)


@dataclass
class Tag(LocationData):
    confidence: float


class Anchor(LocationData):
    anchor_ID: str



