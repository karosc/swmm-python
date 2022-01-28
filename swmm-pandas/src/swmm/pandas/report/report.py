import re
from io import StringIO
from typing import Dict, List, Sequence, Tuple

from pandas.core.api import DataFrame, Timestamp, to_datetime, to_timedelta
from pandas.io.parsers import read_csv, read_fwf


class Report(object):
    _rptfile: str
    """path to swmm rpt file"""

    _rpt_text: str
    """text string of rpt file contents"""

    _sections: Dict[str, str]
    """dictionary of SWMM report sections as {section name : section text}"""

    def __init__(self, rptfile: str):
        """Base class for a SWMM simulation report file.

        The report object provides an api for the tables in the the SWMM
        simulation report file. Tables are access as properties of the object
        and returned as pandas DataFrames.

        Parameters
        ----------
        rptfile : str
            model report file path
        """

        self._rptfile = rptfile

        with open(rptfile, "r") as file:
            self._rpt_text = file.read()

        self._sections = {
            self._find_title(section): section
            for section in self._find_sections(self._rpt_text)
        }

    @staticmethod
    def _find_sections(rpt_text: str) -> List[str]:
        # pattern to match blank lines preceding a line of asterisks
        section_pattern = R"^\s+$\s+(?=\*|A)"
        section_comp = re.compile(section_pattern, re.MULTILINE)
        return list(
            map(lambda x: x.replace("\n  ", "\n"), section_comp.split(rpt_text)[2:-1])
        )

    @staticmethod
    def _find_title(section: str) -> str:
        # pattern to match line between two lines of asterisks
        title_pattern = R"^\*+[\s\S]*?\n([\s\S]*?)\s*\*+"
        title_comp = re.compile(title_pattern, re.MULTILINE)
        s = title_comp.match(section)
        if s:
            return s.group(1).split("  ")[0]
        else:
            raise Exception(f"Error finding title for section\n{section}")

    @staticmethod
    def _split_section(section: str) -> Tuple[str, str]:
        title = Report._find_title(section)
        subsections = re.split(R"\s*-+\n", section)

        if len(subsections) == 1:
            header = "Result"
            # split section on line of asterisks
            data = re.split(R"\*+", section)[-1]

        elif len(subsections) == 2:
            header, data = subsections

        elif len(subsections) == 3:
            notes, header, data = subsections

        elif len(subsections) == 4:
            notes, header, data, sytem = subsections

        else:
            raise Exception(f"Error parsing table {title}")

        return header, data

    @staticmethod
    def _parse_header(header: str) -> List[str]:
        header = [
            re.sub(R"(?<=\w)[^\S\r\n](?=\w)", "_", field[1].dropna().str.cat(sep="_"))
            for field in read_fwf(
                StringIO(re.sub(R"\*|-", " ", header)), header=None
            ).iteritems()
        ]

        if "Time_of_Max_Occurrence_days_hr:min" in header:
            max_idx = header.index("Time_of_Max_Occurrence_days_hr:min")
            header[max_idx] = "days"
            header.insert(max_idx + 1, "Time_of_Max")

        return header

    @staticmethod
    def _parse_table(
        header: Sequence, data: str, sep=R"\s{2,}|\s:\s", index_col=0
    ) -> DataFrame:

        # remove leading spaces on each line and replace long runs of periods with spaces
        data = re.sub(R"^\s+", "", re.sub(R"\.{2,}", "  ", data), flags=re.MULTILINE)

        # by default read in data with minimum 2-spaces or semicolon flanked by spaces as delimiter
        df = read_csv(
            StringIO(data),
            header=None,
            engine="python",
            sep=sep,
            index_col=index_col,
            names=header,
        )

        if "Time_of_Max" in df.columns:

            # convert time of max to timedelta
            df["Time_of_Max"] = to_timedelta(df.pop("days"), unit="D") + to_timedelta(
                df["Time_of_Max"] + ":00"
            )
        return df

    @property
    def analysis_options(self) -> DataFrame:
        if not hasattr(self, "_analysis_options"):
            header, data = self._split_section(self._sections["Analysis Options"])
            df = self._parse_table(["Option", "Setting"], data)
            self._analysis_options = df.dropna()

        return self._analysis_options

    @property
    def runoff_quantity_continuity(self) -> DataFrame:
        if not hasattr(self, "_runoff_quantity_continuity"):
            header, data = self._split_section(
                self._sections["Runoff Quantity Continuity"]
            )
            # substitute spaces between words with underscore so read_fwf works
            # had to use some  regex to not also match new lines
            header = self._parse_header(re.sub(R"(?<=\w)[^\S\r\n](?=\w)", "_", header))
            self._runoff_quantity_continuity = self._parse_table(header, data)
        return self._runoff_quantity_continuity

    @property
    def runoff_quality_continuity(self) -> DataFrame:
        if not hasattr(self, "_runoff_quality_continuity"):
            header, data = self._split_section(
                self._sections["Runoff Quality Continuity"]
            )
            # substitute spaces between words with underscore so read_fwf works
            # had to use some  regex to not also match new lines
            header = self._parse_header(re.sub(R"(?<=\w)[^\S\r\n](?=\w)", "_", header))
            self._runoff_quantity_continuity = self._parse_table(header, data)
        return self._runoff_quantity_continuity

    @property
    def groundwater_continuity(self) -> DataFrame:
        if not hasattr(self, "_groundwater_continuity"):
            header, data = self._split_section(self._sections["Groundwater Continuity"])
            # substitute spaces between words with underscore so read_fwf works
            # had to use some  regex to not also match new lines
            header = self._parse_header(re.sub(R"(?<=\w)[^\S\r\n](?=\w)", "_", header))
            self._groundwater_continuity = self._parse_table(header, data)
        return self._groundwater_continuity

    @property
    def flow_routing_continuity(self) -> DataFrame:
        if not hasattr(self, "_flow_routing_continuity"):
            header, data = self._split_section(
                self._sections["Flow Routing Continuity"]
            )
            # substitute spaces between words with underscore so read_fwf works
            # had to use some  regex to not also match new lines
            header = self._parse_header(re.sub(R"(?<=\w)[^\S\r\n](?=\w)", "_", header))
            self._flow_routing_continuity = self._parse_table(header, data)
        return self._flow_routing_continuity

    @property
    def quality_routing_continuity(self) -> DataFrame:
        if not hasattr(self, "_quality_routing_continuity"):
            header, data = self._split_section(
                self._sections["Quality Routing Continuity"]
            )
            # substitute spaces between words with underscore so read_fwf works
            # had to use some  regex to not also match new lines
            header = self._parse_header(re.sub(R"(?<=\w)[^\S\r\n](?=\w)", "_", header))
            self._quality_routing_continuity = self._parse_table(header, data)
        return self._quality_routing_continuity

    @property
    def highest_continuity_errors(self) -> DataFrame:
        if not hasattr(self, "_highest_errors"):
            header, data = self._split_section(
                self._sections["Highest Continuity Errors"]
            )
            df = self._parse_table(
                ["object_type", "name", "percent_error"], data, sep=R"\s+", index_col=1
            )
            df["percent_error"] = df["percent_error"].str.strip("()%").astype(float)
            self._highest_errors = df
        return self._highest_errors

    @property
    def time_step_critical_elements(self) -> DataFrame:
        if not hasattr(self, "_ts_critical"):
            header, data = self._split_section(
                self._sections["Time-Step Critical Elements"]
            )
            df = self._parse_table(
                ["object_type", "name", "percent"], data, sep=R"\s+", index_col=1
            )
            df["percent"] = df["percent"].str.strip("()%").astype(float)
            self._ts_critical = df
        return self._ts_critical

    @property
    def highest_flow_instability_indexes(self) -> DataFrame:
        if not hasattr(self, "_highest_flow_instability_indexes"):
            header, data = self._split_section(
                self._sections["Highest Flow Instability Indexes"]
            )
            df = self._parse_table(
                ["object_type", "name", "index"], data, sep=R"\s+", index_col=1
            )
            df["index"] = df["index"].str.strip("()").astype(int)
            self._highest_flow_instability_indexes = df
        return self._highest_flow_instability_indexes

    @property
    def routing_time_step_summary(self) -> DataFrame:
        if not hasattr(self, "_routing_time_step_summary"):
            header, data = self._split_section(
                self._sections["Routing Time Step Summary"]
            )
            self._routing_time_step_summary = self._parse_table(
                self._parse_header(header), data, sep=R"\s+:\s+"
            )
        return self._routing_time_step_summary

    @property
    def runoff_summary(self) -> DataFrame:
        if not hasattr(self, "_runoff_summary"):
            header, data = self._split_section(
                self._sections["Subcatchment Runoff Summary"]
            )
            self._runoff_summary = self._parse_table(self._parse_header(header), data)
        return self._runoff_summary

    @property
    def groundwater_summary(self) -> DataFrame:
        if not hasattr(self, "_groundwater_summary"):
            header, data = self._split_section(self._sections["Groundwater Summary"])
            self._groundwater_summary = self._parse_table(
                self._parse_header(header), data
            )
        return self._groundwater_summary

    @property
    def washoff_summary(self) -> DataFrame:
        if not hasattr(self, "_washoff_summary"):
            header, data = self._split_section(
                self._sections["Subcatchment Washoff Summary"]
            )
            self._washoff_summary = self._parse_table(self._parse_header(header), data)
        return self._washoff_summary

    @property
    def node_depth_summary(self) -> DataFrame:
        if not hasattr(self, "_node_depth_summary"):
            header, data = self._split_section(self._sections["Node Depth Summary"])
            self._node_depth_summary = self._parse_table(
                self._parse_header(header), data
            )
        return self._node_depth_summary

    @property
    def node_inflow_summary(self) -> DataFrame:
        if not hasattr(self, "_node_inflow_summary"):
            header, data = self._split_section(self._sections["Node Inflow Summary"])

            self._node_inflow_summary = self._parse_table(
                self._parse_header(header), data
            )
        return self._node_inflow_summary

    @property
    def node_surchage_summary(self) -> DataFrame:
        if not hasattr(self, "_node_surcharge_summary"):
            header, data = self._split_section(self._sections["Node Surcharge Summary"])

            self._node_surcharge_summary = self._parse_table(
                self._parse_header(header), data
            )
        return self._node_surcharge_summary

    @property
    def node_flooding_summary(self) -> DataFrame:
        if not hasattr(self, "_node_flooding_summary"):
            header, data = self._split_section(self._sections["Node Flooding Summary"])

            self._node_flooding_summary = self._parse_table(
                self._parse_header(header), data
            )
        return self._node_flooding_summary

    @property
    def storage_volume_summary(self) -> DataFrame:
        if not hasattr(self, "_storage_volume_summary"):
            header, data = self._split_section(self._sections["Storage Volume Summary"])
            header = header.replace("Storage Unit", "Storage     ")
            self._storage_volume_summary = self._parse_table(
                self._parse_header(header), data
            )
        return self._storage_volume_summary

    @property
    def outfall_loading_summary(self) -> DataFrame:
        if not hasattr(self, "_outfall_loading_summary"):
            header, data = self._split_section(
                self._sections["Outfall Loading Summary"]
            )
            header = header.replace("Outfall Node", "Outfall     ")
            self._outfall_loading_summary = self._parse_table(
                self._parse_header(header), data
            )
        return self._outfall_loading_summary

    @property
    def link_flow_summary(self) -> DataFrame:
        if not hasattr(self, "_link_flow_summary"):
            header, data = self._split_section(self._sections["Link Flow Summary"])
            header = header.replace("|", " ")
            self._link_flow_summary = self._parse_table(
                self._parse_header(header), data
            )
        return self._link_flow_summary

    @property
    def flow_classification_summary(self) -> DataFrame:
        if not hasattr(self, "_flow_classification_summary"):
            header, data = self._split_section(
                self._sections["Flow Classification Summary"]
            )
            to_remove = "---------- Fraction of Time in Flow Class ----------"
            to_replace = "                                                    "
            header = header.replace(to_remove, to_replace)
            self._flow_classification_summary = self._parse_table(
                self._parse_header(header), data
            )
        return self._flow_classification_summary

    @property
    def conduit_surcharge_summary(self) -> DataFrame:
        if not hasattr(self, "_conduit_surcharge_summary"):
            header, data = self._split_section(
                self._sections["Conduit Surcharge Summary"]
            )
            to_remove = "--------- Hours Full --------"
            to_replace = "HrsFull   HoursFull  HrsFull "
            header = header.replace(to_remove, to_replace)
            self._conduit_surcharge_summary = self._parse_table(
                self._parse_header(header), data
            )
        return self._conduit_surcharge_summary

    @property
    def pumping_summary(self) -> DataFrame:
        if not hasattr(self, "_pumping_summary"):
            header, data = self._split_section(self._sections["Pumping Summary"])
            header = self._parse_header(header)
            header[-1] = "Percent_Time_Off_Pump_Curve_Low"
            header.append("Percent_Time_Off_Pump_Curve_High")
            self._pumping_summary = self._parse_table(header, data)
        return self._pumping_summary

    @property
    def link_pollutant_load_summary(self) -> DataFrame:
        if not hasattr(self, "_link_pollutant_load_summary"):
            header, data = self._split_section(
                self._sections["Link Pollutant Load Summary"]
            )

            self._link_pollutant_load_summary = self._parse_table(
                self._parse_header(header), data
            )
        return self._link_pollutant_load_summary

    @property
    def analysis_begun(self) -> Timestamp:
        if not hasattr(self, "_analysis_begun"):
            pattern = R"\s+Analysis begun on:\s+([^\n]+)$"
            s = re.search(pattern, self._rpt_text, flags=re.MULTILINE)
            if s:
                self._analysis_begun = to_datetime(s.group(1))
            else:
                raise Exception("Error finding analysis begun")
        return self._analysis_begun

    @property
    def analysis_end(self) -> Timestamp:
        if not hasattr(self, "_analysis_end"):
            pattern = R"\s+Analysis ended on:\s+([^\n]+)$"
            s = re.search(pattern, self._rpt_text, flags=re.MULTILINE)
            if s:
                self._analysis_end = to_datetime(s.group(1))
            else:
                raise Exception("Error finding analysis end")
        return self._analysis_end
