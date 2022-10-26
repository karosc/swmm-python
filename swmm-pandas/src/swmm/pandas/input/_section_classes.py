import pandas as pd
from typing import List


def _coerce_float(data):
    try:
        return float(data)
    except ValueError:
        return data


def _strip_comment(line: str):
    try:
        return line[: line.index(";")], line[line.index(";") :]

    except ValueError:
        return line, ""


def _is_line_comment(line: str):
    try:
        return line.strip()[0] == ";"
    except IndexError:
        return False


def _is_data(line: str):
    if len(line) == 0 or line.strip()[0:2] == ";;" or line.strip()[0] == "[":
        return False
    return True


class SectionSeries(pd.Series):
    @property
    def _constructor(self):
        return SectionSeries

    @property
    def _constructor_expanddim(self):
        return Section


class Section(pd.DataFrame):
    _metadata = ["_ncol", "_headings", "headings"]
    _ncol = 0
    _headings = []

    @classmethod
    def headings(cls):
        return (
            cls._headings
            + [f"param{i+1}" for i in range(cls._ncol - len(cls._headings))]
            + ["desc"]
        )

    @property
    def _constructor(self):
        return Section

    @property
    def _constructor_sliced(self):
        return SectionSeries

    def __init__(self, text: str, ncols: int, headings: List[str]):

        rows = text.split("\n")
        data = []
        line_comment = ""
        for row in rows:
            if not _is_data(row):
                continue

            elif row.strip()[0] == ";":
                print(row)
                line_comment += row
                continue

            line, comment = _strip_comment(row)
            line_comment += comment

            row_data = [""] * (ncols + 1)
            # print(row_data)
            split_data = [_coerce_float(val) for val in row.split()]
            row_data[:ncols] = self.assigner(split_data)
            row_data[-1] = line_comment
            data.append(row_data)
            line_comment = ""

        super().__init__(data=data, columns=self.headings())

    def assigner(self, line: list):
        out = [""] * self._ncol
        out[: len(line)] = line
        return out


class Option(Section):

    _ncol = 2
    _headings = ["Option", "Value"]

    def __init__(self, text: str):
        super().__init__(text, self._ncol, self._headings)


class Evap(Section):

    _ncol = 13
    _headings = ["Type"]

    def __init__(self, text: str):
        super().__init__(text, self._ncol, self._headings)


class Temperature(Section):

    _ncol = 14
    _headings = ["Option"]

    def __init__(self, text: str):
        super().__init__(text, self._ncol, self._headings)


class Raingage(Section):

    _ncol = 8
    _headings = [
        "Name",
        "Format",
        "Interval",
        "SCF",
        "Source_Type",
        "Source",
        "Station",
        "Units",
    ]

    def __init__(self, text: str):
        super().__init__(text, self._ncol, self._headings)


class Subcatchment(Section):

    _ncol = 9
    _headings = [
        "Name",
        "RainGage",
        "Outlet",
        "Area",
        "PctImp",
        "Width",
        "Slope",
        "CurbLeng",
        "SnowPack",
    ]

    def __init__(self, text: str):
        super().__init__(text, self._ncol, self._headings)


class Subarea(Section):

    _ncol = 8
    _headings = [
        "Subcatchment",
        "Nimp",
        "Nperv",
        "Simp",
        "Sperv",
        "PctZero",
        "RouteTo",
        "PctRouted",
    ]

    def __init__(self, text: str):
        super().__init__(text, self._ncol, self._headings)


class Infil(Section):
    _ncol = 6
    _headings = ["Subcatchment"]

    def __init__(self, text: str):
        super().__init__(text, self._ncol, self._headings)


class Aquifer(Section):

    _ncol = 14
    _headings = [
        "Name",
        "Por",
        "WP",
        "FC",
        "Ksat",
        "Kslope",
        "Tslope",
        "ETu",
        "ETs",
        "Seep",
        "Ebot",
        "Egw",
        "Umc",
        "ETupat",
    ]

    def __init__(self, text: str):
        super().__init__(text, self._ncol, self._headings)


class Groundwater(Section):

    _ncol = 14
    _headings = [
        "Subcatchment",
        "Aquifer",
        "Node",
        "Esurf",
        "A1",
        "B1",
        "A2",
        "B2",
        "A3",
        "Dsw",
        "Egwt",
        "Ebot",
        "Wgr",
        "Umc",
    ]

    def __init__(self, text: str):
        super().__init__(text, self._ncol, self._headings)


class Snowpack(Section):

    _ncol = 9
    _headings = ["Name", "Surface"]

    def __init__(self, text: str):
        super().__init__(text, self._ncol, self._headings)


class Junc(Section):
    _ncol = 6
    _headings = [
        "Name",
        "Elevation",
        "MaxDepth",
        "InitDepth",
        "SurDepth",
        "Aponded",
    ]

    def __init__(self, text: str):
        super().__init__(text, self._ncol, self._headings)


class Outfall(Section):
    _ncol = 6
    _headings = ["Name", "Elevation", "Type", "StageData", "Gated", "RouteTo"]

    def assigner(self, line: list):
        out = [""] * Outfall._ncol
        if len(line) == Outfall._ncol - 1:
            out[:3] = line[:3]
            out[4:] = line[3:]
            return out
        elif len(line) == Outfall._ncol - 2:
            out[:3] = line[:3]
            out[4] = line[3]
            return out
        elif len(line) == Outfall._ncol:
            return line
        else:
            raise ValueError(
                f"Unexpected number of columns in outfall section ({len(line)})"
            )

    def __init__(self, text: str):
        super().__init__(text, self._ncol, self._headings)


class Storage(Section):
    _ncol = 14
    _headings = [
        "Name",
        "Elev",
        "MaxDepth",
        "InitDepth",
        "Shape",
        "CurveName",
        "A1",
        "A2",
        "A0",
        "N/A",
        "Fevap",
        "Psi",
        "Ksat",
        "IMD",
    ]

    def assigner(self, line: list):
        out = [""] * Storage._ncol
        out[: self._headings.index("CurveName")] = line[:5]
        line = line[5:]

        if out[self._headings.index("Shape")].lower() == "functional":
            out[6 : 6 + len(line)] = line
            return out
        elif out[self._headings.index("Shape")].lower() == "tabular":
            out[self._headings.index("CurveName")] = line.pop(0)
            out[
                self._headings.index("N/A") : self._headings.index("N/A") + len(line)
            ] = line
            return out
        else:
            raise ValueError(f"Unexpected line in storage section ({line})")

    def __init__(self, text: str):
        super().__init__(text, self._ncol, self._headings)


class Conduit(Section):

    _ncol = 9
    _headings = [
        "Name",
        "FromNode",
        "ToNode",
        "Length",
        "Roughness",
        "InOffset",
        "OutOffset",
        "InitFlow",
        "MaxFlow",
    ]

    def __init__(self, text: str):
        super().__init__(text, self._ncol, self._headings)


class Pump(Section):

    _ncol = 7
    _headings = [
        "Name",
        "FromNode",
        "ToNode",
        "PumpCurve",
        "Status",
        "Startup",
        "Shutoff",
    ]

    def __init__(self, text: str):
        super().__init__(text, self._ncol, self._headings)


class Orifice(Section):

    _ncol = 8
    _headings = [
        "Name",
        "FromNode",
        "ToNode",
        "Type",
        "Offset",
        "Qcoeff",
        "Gated",
        "CloseTime",
    ]

    def __init__(self, text: str):
        super().__init__(text, self._ncol, self._headings)


class Weir(Section):

    _ncol = 13
    _headings = [
        "Name",
        "FromNode",
        "ToNode",
        "Type",
        "CrestHt",
        "Qcoeff",
        "Gated",
        "EndCon",
        "EndCoeff",
        "Surcharge",
        "RoadWidth",
        "RoadSurf",
        "CoeffCurve",
    ]

    def __init__(self, text: str):
        super().__init__(text, self._ncol, self._headings)


class Outlet(Section):

    _ncol = 9
    _headings = [
        "Name",
        "FromNode",
        "ToNode",
        "Offset",
        "Type",
        "CurveName",
        "Qcoeff",
        "Qexpon",
        "Gated",
    ]

    def assigner(self, line: list):
        out = [""] * Outlet._ncol
        out[: self._headings.index("CurveName")] = line[:5]
        line = line[5:]

        if "functional" in out[self._headings.index("Type")].lower():
            out[6 : 6 + len(line)] = line
            return out
        elif "tabular" in out[self._headings.index("Type")].lower():
            out[self._headings.index("CurveName")] = line[0]
            out[self._headings.index("Gated")] = line[1]
            return out
        else:
            raise ValueError(f"Unexpected line in outlet section ({line})")

    def __init__(self, text: str):
        super().__init__(text, self._ncol, self._headings)


class Losses(Section):
    _ncol = 6
    _headings = ["Link", "Kentry", "Kexit", "Kavg", "FlapGate", "Seepage"]

    def __init__(self, text: str):
        super().__init__(text, self._ncol, self._headings)


class Pollutants(Section):
    _ncol = 11
    _headings = [
        "Name",
        "Units",
        "Crain",
        "Cgw",
        "Crdii",
        "Kdecay",
        "SnowOnly",
        "CoPollutant",
        "CoFrac",
        "Cdwf",
        "Cinit",
    ]

    def __init__(self, text: str):
        super().__init__(text, self._ncol, self._headings)


class LandUse(Section):
    _ncol = 4
    _headings = ["Name", "SweepInterval", "Availability", "LastSweep"]

    def __init__(self, text: str):
        super().__init__(text, self._ncol, self._headings)


class Buildup(Section):
    _ncol = 4
    _headings = ["Landuse", "Pollutant", "FuncType", "C1", "C2", "C3", "PerUnit"]

    def __init__(self, text: str):
        super().__init__(text, self._ncol, self._headings)


class Washoff(Section):
    _ncol = 4
    _headings = ["Landuse", "Pollutant", "FuncType", "C1", "C2", "SweepRmvl", "BmpRmvl"]

    def __init__(self, text: str):
        super().__init__(text, self._ncol, self._headings)


# TODO needs double quote handler for timeseries heading
class Inflow(Section):
    _ncol = 8
    _headings = [
        "Node",
        "Constituent",
        "TimeSeries",
        "Type",
        "Mfactor",
        "Sfactor",
        "Baseline",
        "Pattern",
    ]

    def __init__(self, text: str):
        super().__init__(text, self._ncol, self._headings)


class DWF(Section):
    _ncol = 7
    _headings = [
        "Node",
        "Constituent",
        "Baseline",
        "Pat1",
        "Pat2",
        "Pat3",
        "Pat4",
    ]

    def __init__(self, text: str):
        super().__init__(text, self._ncol, self._headings)


# needs tester model
class RDII(Section):
    _ncol = 3
    _headings = ["Node", "UHgroup", "SewerArea"]

    def __init__(self, text: str):
        super().__init__(text, self._ncol, self._headings)


class Xsections(Section):

    _shapes = (
        "CIRCULAR",
        "FORCE_MAIN",
        "FILLED_CIRCULAR",
        "Depth",
        "RECT_CLOSED",
        "RECT_OPEN",
        "TRAPEZOIDAL",
        "TRIANGULAR",
        "HORIZ_ELLIPSE",
        "VERT_ELLIPSE",
        "ARCH",
        "PARABOLIC",
        "POWER",
        "RECT_TRIANGULAR",
        "Height",
        "RECT_ROUND",
        "Radius",
        "MODBASKETHANDLE",
        "EGG",
        "HORSESHOE",
        "GOTHIC",
        "CATENARY",
        "SEMIELLIPTICAL",
        "BASKETHANDLE",
        "SEMICIRCULAR",
    )

    _ncol = 8
    _headings = [
        "Link",
        "Shape",
        "Curve",
        "Geom1",
        "Geom2",
        "Geom3",
        "Geom4",
        "Barrels",
        "Culvert",
    ]

    def assigner(self, line: list):
        out = [""] * Outlet._ncol
        out[:2] = line[:2]
        line = line[2:]

        if out[1].lower() == "custom" and len(line) >= 2:
            out[self._headings.index("Curve")], out[self._headings.index("Geom1")] = (
                line[1],
                line[0],
            )
            out[self.headings.index("Barrels")] = out[2] if len(out) > 2 else 1
            return out
        elif out[1].lower() == "IRREGULAR" and len(line) == 1:
            out[self._headings.index("Curve")] = line[0]
            return out
        elif out[1].upper() in self._shapes:
            out[
                self._headings.index("Geom1") : self._headings.index("Geom1")
                + len(line)
            ] = line
            return out
        else:
            raise ValueError(f"Unexpected line in outlet section ({line})")

    def __init__(self, text: str):
        super().__init__(text, self._ncol, self._headings)


class Coordinates(Section):
    _ncol = 3
    _headings = ["Node", "X", "Y"]

    def __init__(self, text: str):
        super().__init__(text, self._ncol, self._headings)


class Verticies(Section):
    _ncol = 3
    _headings = ["Link", "X", "Y"]

    def __init__(self, text: str):
        super().__init__(text, self._ncol, self._headings)


class Polygons(Section):
    _ncol = 3
    _headings = ["Subcatch", "X", "Y"]

    def __init__(self, text: str):
        super().__init__(text, self._ncol, self._headings)


class Symbols(Section):
    _ncol = 3
    _headings = ["Gage", "X", "Y"]

    def __init__(self, text: str):
        super().__init__(text, self._ncol, self._headings)


class Labels(Section):
    _ncol = 8
    _headings = [
        "Xcoord",
        "Ycoord",
        "Label",
        "Anchor",
        "Font",
        "Size",
        "Bold",
        "Italic",
    ]

    def __init__(self, text: str):
        super().__init__(text, self._ncol, self._headings)


class Tags(Section):
    _ncol = 3
    _headings = ["Element", "Name", "Tag"]

    def __init__(self, text: str):
        super().__init__(text, self._ncol, self._headings)


class LID_Control(Section):
    _ncol = 9
    _headings = ["Name", "Type"]

    def __init__(self, text: str):
        super().__init__(text, self._ncol, self._headings)


class LID_Usage(Section):
    _ncol = (11,)
    _headings = (
        [
            "Subcatchment",
            "LIDProcess",
            "Number",
            "Area",
            "Width",
            "InitSat",
            "FromImp",
            "ToPerv",
            "RptFiqle",
            "DrainTo",
            "FromPerv",
        ],
    )

    def __init__(self, text: str):
        super().__init__(text, self._ncol, self._headings)


class Adjustments(Section):
    _ncol = ("13",)
    _headings = [
        "Parameter",
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]

    def __init__(self, text: str):
        super().__init__(text, self._ncol, self._headings)


# TODO: write custom to_string class
class Backdrop:
    def __init__(self, text: str):
        rows = text.split("\n")
        data = []
        line_comment = ""
        for row in rows:
            if not _is_data(row):
                continue

            elif row.strip()[0] == ";":
                print(row)
                line_comment += row
                continue

            line, comment = _strip_comment(row)
            line_comment += comment

            split_data = [_coerce_float(val) for val in row.split()]

            if split_data[0].upper() == "DIMENSIONS":
                self.dimensions = split_data[1:]

            elif split_data[0].upper() == "FILE":
                self.file = split_data[1]

    def __repr__(self) -> str:
        return f"Backdrop(dimensions = {self.dimensions}, file = {self.file})"


# TODO: write custom to_string class
class Map:
    def __init__(self, text: str):
        rows = text.split("\n")
        data = []
        line_comment = ""
        for row in rows:
            if not _is_data(row):
                continue

            elif row.strip()[0] == ";":
                print(row)
                line_comment += row
                continue

            line, comment = _strip_comment(row)
            line_comment += comment

            split_data = [_coerce_float(val) for val in row.split()]

            if split_data[0].upper() == "DIMENSIONS":
                self.dimensions = split_data[1:]

            elif split_data[0].upper() == "UNITS":
                self.units = split_data[1]

    def __repr__(self) -> str:
        return f"Map(dimensions = {self.dimensions}, units = {self.units})"
