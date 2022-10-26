import re
from typing import Callable, NamedTuple, List
from pandas import read_csv
from io import StringIO
from pandas.core.api import DataFrame
from swmm.pandas.input import section_parsers
from swmm.pandas.input._section_classes import *

# def default_parser(text:str):
#     return read_csv(StringIO(text),sep='\s+',header=None,comment=';')


class _section_props(NamedTuple):
    """a docstring"""

    ncols: int
    col_names: List[str]
    parser: Callable = section_parsers._default_parser


# class _swmm_section(DataFrame):
#     @property
#     def _constructor(self):
#         return _swmm_section

#     _metadata = ['new_property']


_sections = {
    # TODO build parser for this table
    "TITLE": lambda x: x,
    "OPTION": Option,
    # TODO build parser for this table
    # _section_props(ncols=3, col_names=["Action", "File Type", "File Path"]),
    "FILE": lambda x: x,
    "RAINGAGE": Raingage,
    "TEMPERATURE": Temperature,
    "EVAP": Evap,
    "SUBCATCHMENT": Subcatchment,
    "SUBAREA": Subarea,
    "INFIL": Infil,
    "AQUIFER": Aquifer,
    "GROUNDWATER": Groundwater,
    "SNOWPACK": Snowpack,
    "JUNC": Junc,
    "OUTFALL": Outfall,
    "STORAGE": Storage,
    # TODO build parser for this table
    "DIVIDER": lambda x: x,
    "CONDUIT": Conduit,
    "PUMP": Pump,
    "ORIFICE": Orifice,
    "WEIR": Weir,
    "OUTLET": Outlet,
    "XSECT": Xsections,
    # TODO build parser for this table
    "TRANSECT": lambda x: x,
    "LOSS": Losses,
    # TODO build parser for this table
    "CONTROL": lambda x: x,
    "POLLUT": Pollutants,
    "LANDUSE": LandUse,
    "BUILDUP": Buildup,
    "WASHOFF": Washoff,
    "COVERAGE": lambda x: x,
    "INFLOW": Inflow,
    "DWF": DWF,
    # TODO build parser for this table
    "PATTERN": lambda x: x,
    "RDII": RDII,
    # TODO build parser for this table
    "HYDROGRAPH": lambda x: x,
    # TODO build parser for this table
    "LOADING": lambda x: x,
    # TODO build parser for this table
    "TREATMENT": lambda x: x,
    # TODO build parser for this table
    "CURVE": lambda x: x,
    # TODO build parser for this table
    "TIMESERIES": lambda x: x,
    # TODO build parser for this table
    "REPORT": lambda x: x,  # _section_props(ncols=2, col_names=["Option", "Value"]),
    "MAP": Map,
    "COORDINATE": Coordinates,
    "VERTICES": Verticies,
    "POLYGON": Polygons,
    "SYMBOL": Symbols,
    "LABEL": Labels,
    "BACKDROP": Backdrop,
    "TAG": Tags,
    "PROFILE": lambda x: x,
    "LID_CONTROL": LID_Control,
    "LID_USAGE": LID_Usage,
    "GWF": lambda x: x,  # _section_props(ncols=3, col_names=["Subcatchment", "Type", "Expr"]),
    "ADJUSTMENT": Adjustments,
    "EVENT": lambda x: x,
}

section_re = re.compile(R"\[[\s\S]*?(?=\[)", re.MULTILINE)
