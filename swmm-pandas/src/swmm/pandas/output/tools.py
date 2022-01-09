import numpy as np

arrayish = (list, tuple, set, np.ndarray, type(None))


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
