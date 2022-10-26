# swmm-pandas input
# scope:
#   - high level api for loading, inspecting, changing, and
#     altering a SWMM input file using pandas dataframes


from multiprocessing.sharedctypes import Value
from swmm.pandas.input.sections import section_re, _sections
from swmm.pandas.input._section_classes import Section
from typing import List, Dict
import re

section_keys = tuple(_sections.keys())


class Input:

    # title: Section = None
    # option: Section = None
    # file: Section = None
    # raingage: Section = None
    # temperature: Section = None
    # evap: Section = None
    # subcatchment: Section = None
    # subarea: Section = None
    # infil: Section = None
    # aquifer: Section = None
    # groundwater: Section = None
    # snowpack: Section = None
    # junc: Section = None
    # outfall: Section = None
    # storage: Section = None

    def __init__(self, inpfile: str):

        self.path: str = inpfile

        with open(self.path, "r") as inp:
            self.text: str = inp.read()

        self._sections: Dict[str, str] = {}

        # section_data = []
        # section_titles = []

        # # split section data from inp file string
        # for section in section_re.findall(self.text):
        #     section_titles.append(re.findall(R"\[(.*)\]", section)[0])
        #     section_data.append(
        #         "\n".join(re.findall(R"^(?!;|\[).+$", section, re.MULTILINE))
        #     )

        for section in section_re.findall(self.text):
            name = re.findall(R"\[(.*)\]", section)[0]
            data = "\n".join(re.findall(R"^(?!;{2,}|\[).+$", section, re.MULTILINE))
            try:
                section_idx = list(
                    (name.lower().startswith(x.lower()) for x in _sections)
                ).index(True)
                section_key = section_keys[section_idx]
                self._sections[section_key] = data
                self.__setattr__(
                    f"_{section_key.lower()}", _sections[section_key](data)
                )
            except Exception as e:
                print(e)
                self._sections[name] = data
                self.__setattr__(name.lower(), "Not Implemented")

                print(f"Section {name} not yet supported")
