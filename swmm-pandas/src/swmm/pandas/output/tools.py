import numpy as np
from aenum import Enum
from typing import Tuple

arrayishNone = (list, tuple, set, np.ndarray, type(None))
arrayish = (list, tuple, set, np.ndarray)


def elements(path: str) -> dict:
    with open(path, "r") as fil:
        out = {}
        for lin in fil:
            line = lin.replace("\n", "")
            if "[" in line:
                section = line.replace("[", "").replace("]", "").lower().strip()
                out[section] = []
                continue
            if len(line) > 0:
                out[section].append(line)
    return out


def _enum_get(enum: Enum, name: str) -> int:
    try:
        return enum.__getitem__(name.upper())
    except KeyError:
        return None


def _enum_keys(enum: Enum) -> Tuple[str]:
    return tuple(map(lambda x: x.lower(), enum.__members__.keys()))
