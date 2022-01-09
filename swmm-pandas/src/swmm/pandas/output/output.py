import os.path
import warnings
from datetime import datetime, timedelta
from functools import wraps
from typing import Callable, List, NoReturn, Optional, Sequence, Tuple, Union

import numpy as np
import pandas as pd
from aenum import Enum, extend_enum
from julian import from_jd

# Third party imports
from swmm.toolkit import output, shared_enum
from swmm.pandas.output.tools import arrayish
from swmm.pandas.output.structure import Structure
from swmm.pandas.output.enums import (
    link_attribute,
    node_attribute,
    subcatch_attribute,
    system_attribute,
)


def output_open_handler(func):
    """Checks if output file is open before running function.

    Parameters
    ----------
    func : function
        method of Output class
    """

    @wraps(func)
    def inner_function(self, *args, **kwargs):
        if not self._loaded:
            self._open()

        return func(self, *args, **kwargs)

    return inner_function


class Output(object):
    def __init__(self, binfile: str):
        """Base class for a SWMM binary output file.

        The output object provides several options to process timeseries within binary output file.

        Output files should be closed after use prevent memory leaks. Close them explicitly with
        the `_close()` method or deleting the object using `del`, or use it with a context manager.

        .. code-block:: python

            # Using a the _close method
            >>> from swmm.pandas import Output
            >>> out = Output('tests/Model.out')
            >>> print(out.project_size)
            [3, 9, 8, 1, 3]
            >>> out._close() # can also use `del out`
            >>>
            # Using a context manager
            >>> with Output('tests/Model.out') as out:
            ...     print(out.pollutants)
            ('groundwater', 'pol_rainfall', 'sewage')



        Parameters
        ----------
        binfile : str
            model binary file path

        Returns
        -------

        """
        self._binfile = binfile
        self._period = None
        self._report = None
        self._start = None
        self._end = None
        self._delete_handle = False
        self._handle = None
        self._loaded = False
        self._timeIndex = None
        self._project_size = None
        self._subcatchments = None
        self._nodes = None
        self._links = None
        self._pollutants = None

        # have to copy attribute dicts since they are edited
        # to include pollutants when outfile is opened
        # editing global attributes would break things
        # if more than one output object was created
        # from different output files
        self.subcatch_attributes = subcatch_attribute.copy()
        self.node_attributes = node_attribute.copy()
        self.link_attributes = link_attribute.copy()
        self.system_attributes = system_attribute.copy()

        # need copies of enumes to extend them for pollutants
        # looked into using swmm.toolkit.output_metadata but it
        # extends global enums, which can break having multiple
        # output objects opened in the same python session.
        self._subcatchAttrEnum = Enum(
            "SubcatchAttribute",
            list(shared_enum.SubcatchAttribute.__members__.keys()),
            start=0,
        )
        self._nodeAttrEnum = Enum(
            "NodeAttribute",
            list(shared_enum.NodeAttribute.__members__.keys()),
            start=0,
        )
        self._linkAttrEnum = Enum(
            "LinkAttribute",
            list(shared_enum.LinkAttribute.__members__.keys()),
            start=0,
        )

    @staticmethod
    def _elementIndex(
        elementID: Union[str, int, None], indexSquence: Sequence[str], elementType: str
    ) -> int:
        """Validate the index of a model element passed to Output methods. Used to
        convert model element names to their index in the out file.

        Parameters
        ----------
        elementID : str, int
            The name or index of the model element listed in the index_dict dict.
        indexSquence : one of more string
            The ordered sequence against which to validate the index
            (one of self.nodes, self.links, self.subcatchments).
        elementType : str
            The type of model element (e.g. node, link, etc.)
            Only used to print the exception if an attribute cannot be found.

        Returns
        -------
        int
            The integer index of the requested element.

        Raises
        ------
        OutputException
            Exception if element cannot be found in indexSequence.

        """

        if isinstance(elementID, (int, np.integer)):
            return int(elementID)

        try:
            return indexSquence.index(elementID)

        # since this class can pull multiple attributes and elements in one function
        # call it is probably better to do some pre-validation of input arguments
        # before starting a potentially lengthy data pull
        except ValueError:
            raise ValueError(
                f"{elementType} ID: {elementID} does not exist in model output."
            )

    @staticmethod
    def _validateAttribute(
        attribute: Union[int, str, Sequence[Union[int, str]], None],
        validAttributes: dict,
    ) -> Tuple[list, list]:
        """
        Function to validate attribute arguments of element_series, element_attribute,
        and element_result functions.

        Parameters
        ----------
        attribute : Union[int, str, Sequence[Union[int, str]], None]
            The attribute to validate against validAttributes.
        validAttributes : dict
            THe dict of attributes against which to validate attribute.

        Returns
        -------
        Tuple[list, list]
            Two arrays, one of attribute names and one of attribute indicies.

        """
        # this kind of logic was needed in the series and results functions.
        # not sure if this is the best way, but it felt a bit DRYer to
        # put it into a funciton

        if attribute is None:
            attributeArray = validAttributes
        elif isinstance(attribute, arrayish):
            attributeArray = attribute
        else:
            attributeArray = [attribute]

        # allow mixed input of attributes
        # accept string names, integers, or enums values in the same list
        attributeIndexArray = []
        for i, attrib in enumerate(attributeArray):

            if isinstance(attrib, Enum):
                attributeArray[i] = attrib.name.lower()
                attributeIndexArray.append(attrib)

            elif isinstance(attrib, (int, np.integer)):
                # will raise index error if not in range
                attribName = list(validAttributes)[attrib]
                attributeArray[i] = attribName
                attributeIndexArray.append(validAttributes.get(attribName))

            elif isinstance(attrib, str):
                index = validAttributes.get(attrib)
                if index is None:
                    raise ValueError(
                        f"Attribute {attrib} not in valid attribute list: {list(validAttributes)}"
                    )
                attributeIndexArray.append(index)
            else:
                raise TypeError(
                    f"Input type: {type(attrib)} not valid. Must be one of int, str, or Enum"
                )

        attributeIndexArray = [validAttributes.get(atr, -1) for atr in attributeArray]

        return attributeArray, attributeIndexArray

    @staticmethod
    def _validateElement(
        element: Union[int, str, Sequence[Union[int, str]], None],
        validElements: Sequence[str],
    ) -> Tuple[list, list]:
        """
        Function to validate element arguments of element_series, element_attribute,
        and element_result functions.

        Parameters
        ----------
        element : Union[int, str, Sequence[Union[int, str]], None]
            The element name or index or None. If None, return all elements in
            validElements.
        validElements : Sequence[str]
            Tuple of elements against which to validate element.

        Returns
        -------
        Tuple[list, list]
            Two arrays, one of element names and one of element indicies.

        """
        # this kind of logic was needed in the series and results functions
        # not sure if this is the best way, but it felt a bit DRYer to
        # put it into a funciton

        if element is None:
            elementArray = list(validElements)
        elif isinstance(element, arrayish):
            elementArray = element
        else:
            elementArray = [element]

        elementIndexArray = []

        # allow mixed input of elements. string names can be mixed
        # with integer indicies in the same input list
        for i, elem in enumerate(elementArray):

            if isinstance(elem, (int, np.integer)):
                # will raise index error if not in range
                elemName = validElements[elem]
                elementArray[i] = elemName
                elementIndexArray.append(elem)

            elif isinstance(elem, str):
                elementIndexArray.append(Output._elementIndex(elem, validElements, ""))

            else:
                raise TypeError(
                    f"Input type {type(elem)} not valid. Must be one of int, str"
                )

        return elementArray, elementIndexArray

    def _checkPollutantName(self, name: str) -> str:
        """Check pollutant name against existing attribute dicts.
        Rename and and warn if existing attribute is duplicated.

        Parameters
        ----------
        name : str
            The name of pollutant.

        Returns
        -------
        str
            The validated name of pollutant.
        """

        elems = []
        if name in self.subcatch_attributes:
            elems.append("subcatchment")

        if name in self.node_attributes:
            elems.append("node")

        if name in self.link_attributes:
            elems.append("link")

        if name in self.system_attributes:
            elems.append("system")

        if len(elems) > 0:
            warnings.warn(
                f"Pollutent {name} is a duplicate of existing {','.join(elems)} attribute, renaming to pol_{name}"
            )
            return f"pol_{name}"

        return name

    def _open(self) -> bool:
        """Open a binary file.

        Parameters
        ----------

        Returns
        -------
        bool
            True if binary file was opened successfully.

        """
        if not os.path.exists(self._binfile):
            raise ValueError(f"Output file at: '{self._binfile}' does not exist")

        if self._handle is None:
            self._handle = output.init()

        if not self._loaded:

            self._loaded = True
            output.open(self._handle, self._binfile)
            self._start = from_jd(output.get_start_date(self._handle) + 2415018.5)
            self._start = self._start.replace(microsecond=0)
            self._report = output.get_times(self._handle, shared_enum.Time.REPORT_STEP)
            self._period = output.get_times(self._handle, shared_enum.Time.NUM_PERIODS)
            self._end = self._start + timedelta(seconds=self._period * self._report)

            # load pollutants if not already loaded
            if self._pollutants is None:
                # load pollutant data if it has not before
                total = self.project_size[4]
                self._pollutants = tuple(
                    self._checkPollutantName(
                        self._objectName(shared_enum.ElementType.POLLUT, index).lower()
                    )
                    for index in range(total)
                )

                # extend enums to include pollutants
                for i in range(1, total):
                    symbolic_name = "POLLUT_CONC_" + str(i)
                    extend_enum(self._subcatchAttrEnum, symbolic_name, 8 + i)
                    extend_enum(self._nodeAttrEnum, symbolic_name, 6 + i)
                    extend_enum(self._linkAttrEnum, symbolic_name, 5 + i)

                for i, nom in enumerate(self._pollutants):
                    symbolic_name = "POLLUT_CONC_" + str(i)

                    self.subcatch_attributes[nom] = self._subcatchAttrEnum[
                        symbolic_name
                    ]
                    self.node_attributes[nom] = self._nodeAttrEnum[symbolic_name]
                    self.link_attributes[nom] = self._linkAttrEnum[symbolic_name]

        return True

    def _close(self) -> bool:
        """Close an opened binary file.

        Parameters
        ----------

        Returns
        -------
        bool
            True if binary file was closed successfully.

        """
        if self._loaded:
            self._loaded = False
            self._delete_handle = True
            output.close(self._handle)

        return True

    ###### outfile property getters ######

    @property
    @output_open_handler
    def report(self) -> int:
        """Return the reporting timestep in seconds.

        Parameters
        ----------

        Returns
        -------
        int
            The reporting timestep in seconds.

        """
        return self._report

    @property
    @output_open_handler
    def start(self) -> datetime:
        """Return the reporting start datetime.

        Parameters
        ----------

        Returns
        -------
        datetime
            The reporting start datetime.

        """
        return self._start

    @property
    @output_open_handler
    def end(self) -> datetime:
        """Return the reporting end datetime.

        Returns
        -------
        datetime
            The reporting end datetime.
        """
        return self._end

    @property
    @output_open_handler
    def period(self) -> int:
        """Return the number of reporting timesteps in the binary output file.

        Returns
        -------
        int
            The number of reporting timesteps.
        """
        return self._period

    @property
    def project_size(self) -> List[int]:
        """Returns the number of each model element type available in out binary output file
        in the following order:

        [subcatchment, node, link, system, pollutant]

        Parameters
        ----------

        Returns
        -------
        list
            A list of numbers of each model type.

            [nSubcatchments, nNodes, nLinks, nSystems(1), nPollutants]

        """
        if self._project_size is None:
            self._load_project_size()
        return self._project_size

    @output_open_handler
    def _load_project_size(self) -> NoReturn:
        """Load model size into self._project_size"""
        self._project_size = output.get_proj_size(self._handle)

    @property
    def pollutants(self) -> Tuple[str]:
        """Return a tuple of pollutants available in SWMM binary output file.

        Parameters
        ----------

        Returns
        -------
         Tuple[str]
           A tuple of pollutant names.

        """

        # chose not to write a pollutant loader method
        # because loading such is kind of imperative to the functionality
        # of other data getter methods, which don't necessarily
        # call pollutants method. Instead, pollutant loading logic is
        # thrown in the _open() method, and this method calls open if
        # pollutants are not available.
        if self._pollutants is None:
            self._open()

        return self._pollutants

    @property
    @output_open_handler
    def _unit(self) -> Tuple[int]:
        """Return SWMM binary output file unit type from `swmm.toolkit.shared_enum.UnitSystem`.

        Parameters
        ----------

        Returns
        -------
        Tuple[int]
            Tuple of integers indicating system units, flow units, and units for each pollutant.

        """
        return tuple(output.get_units(self._handle))

    @property
    def units(self):
        """Return SWMM binary output file unit type from `swmm.toolkit.shared_enum.UnitSystem`.

        Parameters
        ----------

        Returns
        -------
        List[str]
            List of string names for system units, flow units, and units for each pollutant.

        """
        return [
            shared_enum.UnitSystem(self._unit[0]).name,
            shared_enum.FlowUnits(self._unit[1]).name,
        ] + [shared_enum.ConcUnits(i).name for i in self._unit[2:]]

    @property
    @output_open_handler
    def _version(self) -> int:
        """Return SWMM version used to generate SWMM binary output file results.

        Parameters
        ----------

        Returns
        -------
        int
            Integer representation of SWMM version used to make output file.

        """
        return output.get_version(self._handle)

    @output_open_handler
    def _objectName(self, object_type: int, index: int) -> str:
        """Get object name from SWMM binary output file using object type and object index.

        Parameters
        ----------
        object_type : int
            The object type from swmm.toolkit.shared_enum.ElementType.
        index : int
            The object index.

        Returns
        -------
        str
            object name

        """
        return output.get_elem_name(self._handle, object_type, index)

    ##### timestep setters and getters #####
    def _time2step(
        self,
        dateTime: Union[
            None,
            str,
            int,
            datetime,
            pd.Timestamp,
            np.datetime64,
            Sequence[Union[str, int, datetime, pd.Timestamp, np.datetime64]],
        ],
        ifNone: int = 0,
        method: str = "nearest",
    ) -> List[int]:
        """Convert datetime value to SWMM timestep index. By deafult, this returns the nearest timestep to
        to the requested date, so it will always return a time index available in the binary output file.


        Parameters
        ----------
        dateTime : datetime-like or string or sequence of such
            datetime to convert. Must be a datetime-like object or convertable
            with `pd.to_datetime`.

        ifNone : int
            The value to return if dateTime is None, defaults to 0.

        method: str
            The method name to pass to pandas `get_indexer`_, default to "nearest.

            .. _get_indexer: https://pandas.pydata.org/docs/reference/api/pandas.Index.get_indexer.html

        Returns
        -------
        Union[int, np.ndarray]
            SWMM model time step or array of time steps

        """
        if dateTime is None:
            return [ifNone]

        dt = np.asarray(dateTime).flatten()
        # if passing swmm time step, no indexing necessary
        if dt.dtype == int:
            return dt.tolist()

        # ensure datetime value
        dt = pd.to_datetime(dateTime)
        return self.timeIndex.get_indexer(dt, method=method).tolist()

    @property
    def timeIndex(self) -> pd.DatetimeIndex:
        """Returns DatetimeIndex of reporting timeseries in binary output file.

        Parameters
        ----------

        Returns
        -------
        pd.DatetimeIndex
            A pandas `DatetimeIndex`_ for each reporting timestep.

            .. _DatetimeIndex: https://pandas.pydata.org/docs/reference/api/pandas.DatetimeIndex.html?highlight=datetimeindex#pandas.DatetimeIndex

        """
        if self._timeIndex is None:
            self._load_timeIndex()
        return self._timeIndex

    @output_open_handler
    def _load_timeIndex(self) -> NoReturn:
        """Load model reporting times into self._times"""
        self._timeIndex = pd.DatetimeIndex(
            [
                self._start + timedelta(seconds=self._report) * step
                for step in range(1, self._period + 1)
            ]
        )

    ##### model element setters and getters #####
    def _subcatchmentIndex(
        self, subcatchment: Union[str, int, Sequence[Union[str, int]], None]
    ) -> Union[List[int], int]:
        """Get the swmm index for subcatchment.

        Parameters
        ----------
        subcatchment : Union[str, int, Sequence[Union[str, int]]]
            The name(s) of subcatchment(s).

        Returns
        -------
        Union[List[int], int]
           The SWMM index(s) of subcatchment(s).

        """

        if isinstance(subcatchment, (str, int, type(None))):
            return self._elementIndex(subcatchment, self.subcatchments, "subcatchment")
        else:
            return [
                self._elementIndex(sub, self.subcatchments, "subcatchment")
                for sub in subcatchment
            ]

    @property
    def subcatchments(self) -> Tuple[str]:
        """Return a tuple of subcatchments available in SWMM output binary file.

        Parameters
        ----------

        Returns
        -------
        Tuple[str]
            A tuple of model subcatchment names.

        """
        if self._subcatchments is None:
            self._load_subcatchments()
        return self._subcatchments

    @output_open_handler
    def _load_subcatchments(self) -> NoReturn:
        """Load model size into self._project_size"""
        total = self.project_size[0]

        self._subcatchments = tuple(
            self._objectName(shared_enum.ElementType.SUBCATCH, index)
            for index in range(total)
        )

    def _nodeIndex(
        self, node: Union[str, int, Sequence[Union[str, int]], None]
    ) -> Union[List[int], int]:
        """Get the swmm index for node.

        Parameters
        ----------
        node : Union[str, int, Sequence[Union[str, int]]]
            The name(s) of node(s)

        Returns
        -------
        Union[List[int], int]
            The SWMM index(s) of node(s).

        """

        if isinstance(node, (str, int, type(None))):
            return self._elementIndex(node, self.nodes, "node")
        else:
            return [self._elementIndex(nd, self.nodes, "node") for nd in node]

    @property
    def nodes(self) -> Tuple[str]:
        """Return a tuple of nodes available in SWMM binary output file.

        Parameters
        ----------

        Returns
        -------
        Tuple[str]
            A tuple of model node names.

        """
        if self._nodes is None:
            self._load_nodes()
        return self._nodes

    @output_open_handler
    def _load_nodes(self) -> NoReturn:
        """Load model nodes into self._nodes"""
        total = self.project_size[1]

        self._nodes = tuple(
            self._objectName(shared_enum.ElementType.NODE, index)
            for index in range(total)
        )

    def _linkIndex(
        self, link: Union[str, int, Sequence[Union[str, int]], None]
    ) -> Union[List[int], int]:
        """Get the swmm index for link.

        Parameters
        ----------
        link : Union[str, int, Sequence[Union[str, int]]]
            The name(s) of link(s)

        Returns
        -------
        Union[List[int], int]
            SWMM index(s) of link(s).

        """
        if isinstance(link, (str, int, type(None))):
            return self._elementIndex(link, self.links, "link")
        else:
            return [self._elementIndex(lnk, self.links, "link") for lnk in link]

    @property
    def links(self) -> Tuple[str]:
        """Return a tuple of links available in SWMM binary output file.

        Parameters
        ----------

        Returns
        -------
        Tuple[str]
            A tuple of model link names.

        """
        if self._links is None:
            self._load_links()
        return self._links

    @output_open_handler
    def _load_links(self) -> NoReturn:
        """Load model links into self._links"""
        total = self.project_size[2]
        self._links = tuple(
            self._objectName(shared_enum.ElementType.LINK, index)
            for index in range(total)
        )

    ####### series getters #######
    def _model_series(
        self,
        elementIndexArray: list,
        attributeIndexArray: list,
        startIndex: int,
        endIndex: int,
        columns: str,
        getterFunc: Callable,
    ):

        if columns not in ("elem", "attr", None):
            raise ValueError(
                f"columns must be one of 'elem','attr', or None. {columns} was given"
            )

        if columns is None:
            return np.concatenate(
                [
                    np.concatenate(
                        [
                            getterFunc(
                                self._handle, elemIdx, Attr, startIndex, endIndex
                            )
                            for Attr in attributeIndexArray
                        ],
                        axis=0,
                    )
                    for elemIdx in elementIndexArray
                ],
                axis=0,
            )

        elif columns.lower() == "attr":
            return np.concatenate(
                [
                    np.stack(
                        [
                            getterFunc(
                                self._handle, elemIdx, Attr, startIndex, endIndex
                            )
                            for Attr in attributeIndexArray
                        ],
                        axis=1,
                    )
                    for elemIdx in elementIndexArray
                ],
                axis=0,
            )

        elif columns.lower() == "elem":
            return np.concatenate(
                [
                    np.stack(
                        [
                            getterFunc(
                                self._handle, elemIdx, Attr, startIndex, endIndex
                            )
                            for elemIdx in elementIndexArray
                        ],
                        axis=1,
                    )
                    for Attr in attributeIndexArray
                ],
                axis=0,
            )

    def _model_series_index(
        self,
        elementArray: list,
        attributeArray: list,
        startIndex: int,
        endIndex: int,
        columns: str,
    ):
        if columns not in ("elem", "attr", None):
            raise ValueError(
                f"columns must be one of 'elem','attr', or None. {columns} was given"
            )

        if columns is None:
            dtIndex = np.tile(
                self.timeIndex[startIndex:endIndex],
                len(elementArray) * len(attributeArray),
            )
            indexArrays = [dtIndex]
            names = ["datetime"]
            cols = ["Result"]
            if len(elementArray) > 1:
                indexArrays.append(
                    np.asarray(elementArray).repeat(
                        (endIndex - startIndex) * len(attributeArray)
                    )
                )
                names.append("element")
            if len(attributeArray) > 1:
                indexArrays.append(
                    np.tile(np.asarray(attributeArray), len(elementArray)).repeat(
                        endIndex - startIndex
                    )
                )
                names.append("attribute")

        elif columns.lower() == "attr":
            dtIndex = np.tile(self.timeIndex[startIndex:endIndex], len(elementArray))
            indexArrays = [dtIndex]
            names = ["datetime"]
            cols = attributeArray
            if len(elementArray) > 1:
                indexArrays.append(
                    np.asarray(elementArray).repeat(endIndex - startIndex)
                )
                names.append("element")

        elif columns.lower() == "elem":
            dtIndex = np.tile(self.timeIndex[startIndex:endIndex], len(attributeArray))
            indexArrays = [dtIndex]
            names = ["datetime"]
            cols = elementArray

            if len(attributeArray) > 1:
                indexArrays.append(
                    np.asarray(attributeArray).repeat(endIndex - startIndex)
                )
                names.append("attribute")

        return (
            pd.MultiIndex.from_arrays(
                indexArrays,
                names=names,
            ),
            cols,
        )

    def subcatch_series(
        self,
        subcatchment: Union[int, str, Sequence[Union[int, str]], None],
        attribute: Union[int, str, Sequence[Union[int, str]], None] = (
            "rainfall",
            "runoff_rate",
            "gw_outflow_rate",
        ),
        start: Union[str, int, datetime, None] = None,
        end: Union[str, int, datetime, None] = None,
        columns: Optional[str] = "attr",
        asframe: bool = True,
    ) -> Union[pd.DataFrame, np.ndarray]:
        """Get one or more time series for one or more subcatchment attributes.
        Specify series start index and end index to get desired time range.

        Parameters
        ----------
        subcatchment : Union[int, str, Sequence[Union[int, str]], None]
            The subcatchment index or name.

        attribute : Union[int, str, Sequence[Union[int, str]], None],
            The attribute index or name.

            On of:

            **rainfall, snow_depth, evap_loss, infil_loss, runoff_rate, gw_outflow_rate,
            gw_table_elev, soil_moisture**.


            Defaults to: `('rainfall','runoff_rate','gw_outflow_rate').`


            You can also input the integer index of the attribute you would like to
            pull or the actual enum from swmm.toolkit.shared_enum.SubcatchAttribute.

            Setting to None indicates all attributes.

        start : Union[str,int, datetime, None], optional
            The start datetime or index of from which to return series, defaults to None.

            Setting to None indicates simulation start.

        end : Union[str,int, datetime, None], optional
            The end datetime or index of from which to return series, defaults to None.

            Setting to None indicates simulation end.

        columns: Optional[str], optional
            Decide whether or not to break out elements or attributes as columns. May be one of:

            None   : Return long-form data with one column for each data point

            'elem' : Return data with a column for each element. If more than one attribute are given, attribute names are added to the index.

            'attr' : Return data with a column for each attribute. If more than one element are given, element names are added to the index.

            defaults to 'attr'.

        asframe: bool
            A switch to return an indexed DataFrame. Set to False to get an array of values only, defaults to True.

        Returns
        -------
        Union[pd.DataFrame,np.ndarray]
            A DataFrame or ndarray of attribute values in each column for requested
            date range and subcatchments.

        """
        subcatchementArray, subcatchmentIndexArray = self._validateElement(
            subcatchment, self.subcatchments
        )

        attributeArray, attributeIndexArray = self._validateAttribute(
            attribute, self.subcatch_attributes
        )

        startIndex = self._time2step(start, 0)[0]
        endIndex = self._time2step(end, self._period)[0]

        values = self._model_series(
            subcatchmentIndexArray,
            attributeIndexArray,
            startIndex,
            endIndex,
            columns,
            output.get_subcatch_series,
        )

        if not asframe:
            return values

        dfIndex, cols = self._model_series_index(
            subcatchementArray, attributeArray, startIndex, endIndex, columns
        )
        return pd.DataFrame(values, index=dfIndex, columns=cols)

    @output_open_handler
    def node_series(
        self,
        node: Union[int, str, Sequence[Union[int, str]], None],
        attribute: Union[int, str, Sequence[Union[int, str]], None] = (
            "invert_depth",
            "flooding_losses",
            "total_inflow",
        ),
        start: Union[str, int, datetime, None] = None,
        end: Union[str, int, datetime, None] = None,
        columns: Optional[str] = "attr",
        asframe: bool = True,
    ) -> Union[pd.DataFrame, np.ndarray]:
        """Get one or more time series for one or more node attributes.
        Specify series start index and end index to get desired time range.

        Parameters
        ----------
        node : Union[int, str, Sequence[Union[int, str]], None]
            The node index or name.

        attribute : Union[int, str, Sequence[Union[int, str]], None],
            The attribute index or name.

            On of:

            **invert_depth, hydraulic_head, ponded_volume, lateral_inflow,
            total_inflow, flooding_losses**.

            defaults to: `('invert_depth','flooding_losses','total_inflow')`

            You can also input the integer index of the attribute you would like to
            pull or the actual enum from swmm.toolkit.shared_enum.NodeAttribute.

            Setting to None indicates all attributes.

        start : Union[str, int, datetime, None], optional
            The start datetime or index of from which to return series, defaults to None.

            Setting to None indicates simulation start.

        end : Union[str, int, datetime, None], optional
            The end datetime or index of from which to return series, defaults to None.

            Setting to None indicates simulation end.

        columns: Optional[str], optional
            Decide whether or not to break out elements or attributes as columns. May be one of:

            None   : Return long-form data with one column for each data point

            'elem' : Return data with a column for each element. If more than one attribute are given, attribute names are added to the index.

            'attr' : Return data with a column for each attribute. If more than one element are given, element names are added to the index.

            defaults to 'attr'.

        asframe: bool
            A switch to return an indexed DataFrame. Set to False to get an array of values only, defaults to True.

        Returns
        -------
        Union[pd.DataFrame,np.ndarray]
            A DataFrame or ndarray of attribute values in each column for requested
            date range and nodes.

        """
        nodeArray, nodeIndexArray = self._validateElement(node, self.nodes)

        attributeArray, attributeIndexArray = self._validateAttribute(
            attribute, self.node_attributes
        )

        startIndex = self._time2step(start, 0)[0]
        endIndex = self._time2step(end, self._period)[0]

        values = self._model_series(
            nodeIndexArray,
            attributeIndexArray,
            startIndex,
            endIndex,
            columns,
            output.get_node_series,
        )

        if not asframe:
            return values

        dfIndex, cols = self._model_series_index(
            nodeArray, attributeArray, startIndex, endIndex, columns
        )

        return pd.DataFrame(values, index=dfIndex, columns=cols)

    @output_open_handler
    def link_series(
        self,
        link: Union[int, str, Sequence[Union[int, str]], None],
        attribute: Union[int, str, Sequence[Union[int, str]], None] = (
            "flow_rate",
            "flow_velocity",
            "flow_depth",
        ),
        start: Union[int, str, datetime, None] = None,
        end: Union[int, str, datetime, None] = None,
        columns: Optional[str] = "attr",
        asframe: bool = True,
    ) -> Union[pd.DataFrame, np.ndarray]:
        """Get one or more time series for one or more link attributes.
        Specify series start index and end index to get desired time range.

        Parameters
        ----------
        link : Union[int, str, Sequence[Union[int, str]], None]
            The link index or name.

        attribute : Union[int, str, Sequence[Union[int, str]], None]
            The attribute index or name.

            On of:

            **flow_rate, flow_depth, flow_velocity, flow_volume, capacity**.

            defaults to: `('flow_rate','flow_velocity','flow_depth')`

            You can also input the integer index of the attribute you would like to
            pull or the actual enum from swmm.toolkit.shared_enum.LinkAttribute.

            Setting to None indicates all attributes.

        start_index : Union[str,int, datetime, None], optional
            The start datetime or index of from which to return series, defaults to None.

            Setting to None indicates simulation start.

        end_index : Union[str,int, datetime, None], optional
            The end datetime or index of from which to return series, defaults to None.

            Setting to None indicates simulation end.

        columns: Optional[str], optional
            Decide whether or not to break out elements or attributes as columns. May be one of:

            None   : Return long-form data with one column for each data point

            'elem' : Return data with a column for each element. If more than one attribute are given, attribute names are added to the index.

            'attr' : Return data with a column for each attribute. If more than one element are given, element names are added to the index.

            defaults to 'attr'.

        asframe: bool
            A switch to return an indexed DataFrame. Set to False to get an array of values only, defaults to True.

        Returns
        -------
        Union[pd.DataFrame,np.ndarray]
            A DataFrame or ndarray of attribute values in each column for requested
            date range and links.

        """
        linkArray, linkIndexArray = self._validateElement(link, self.links)

        attributeArray, attributeIndexArray = self._validateAttribute(
            attribute, self.link_attributes
        )

        startIndex = self._time2step(start, 0)[0]
        endIndex = self._time2step(end, self._period)[0]

        values = self._model_series(
            linkIndexArray,
            attributeIndexArray,
            startIndex,
            endIndex,
            columns,
            output.get_link_series,
        )

        if not asframe:
            return values

        dfIndex, cols = self._model_series_index(
            linkArray, attributeArray, startIndex, endIndex, columns
        )

        return pd.DataFrame(values, index=dfIndex, columns=cols)

    @output_open_handler
    def system_series(
        self,
        attribute: Union[int, str, Sequence[Union[int, str]], None] = None,
        start: Union[str, int, datetime, None] = None,
        end: Union[str, int, datetime, None] = None,
        asframe: bool = True,
    ) -> Union[pd.DataFrame, np.ndarray]:
        """Get one or more a time series for one or more system attributes.
        Specify series start index and end index to get desired time range.

        Parameters
        ----------
        attribute : Union[int, str, Sequence[Union[int, str]], None]
            The attribute index or name.

            On of:

            **air_temp, rainfall, snow_depth, evap_infil_loss, runoff_flow,
            dry_weather_inflow, gw_inflow, rdii_inflow, direct_inflow, total_lateral_inflow,
            flood_losses, outfall_flows, volume_stored, evap_rate**.

            defaults to `None`.

            You can also input the integer index of the attribute you would like to
            pull or the actual enum from swmm.toolkit.shared_enum.SystemAttribute.

            Setting to None indicates all attributes.

        start_index : Union[str, int, datetime, None], optional
            The start datetime or index of from which to return series, defaults to None.

            Setting to None indicates simulation start.

        end_index : Union[str, int, datetime, None], optional
            The end datetime or index of from which to return series, defaults to None.

            Setting to None indicates simulation end.

        asframe: bool
            switch to return an indexed DataFrame. Set to False to get an array of values only, defaults to True

        Returns
        -------
        Union[pd.DataFrame,np.ndarray]
            DataFrame or ndarray of attribute values in each column for request date range

        """

        attributeArray, attributeIndexArray = self._validateAttribute(
            attribute, self.system_attributes
        )

        startIndex = self._time2step(start, 0)[0]
        endIndex = self._time2step(end, self._period)[0]

        values = np.stack(
            [
                output.get_system_series(self._handle, sysAttr, startIndex, endIndex)
                for sysAttr in attributeIndexArray
            ],
            axis=1,
        )

        if not asframe:
            return values

        dfIndex = pd.Index(self.timeIndex[startIndex:endIndex], name="datetime")
        return pd.DataFrame(values, index=dfIndex, columns=attributeArray)

    ####### attribute getters #######

    @output_open_handler
    def subcatch_attribute(
        self,
        time: Union[str, int, datetime],
        attribute: Union[int, str, Sequence[Union[int, str]], None] = (
            "rainfall",
            "runoff_rate",
            "gw_outflow_rate",
        ),
        asframe: bool = True,
    ) -> Union[pd.DataFrame, np.ndarray]:
        """For all subcatchments at a given time, get a one or more attributes.

        Parameters
        ----------
        time : Union[str, int, datetime]
            The datetime or simulation index for which to pull data, defaults to None.

        attribute : Union[int, str, Sequence[Union[int, str]], None],
            The attribute index or name.

            On of:

            **rainfall, snow_depth, evap_loss, infil_loss, runoff_rate, gw_outflow_rate,
            gw_table_elev, soil_moisture**.

            Defaults to: `('rainfall','runoff_rate','gw_outflow_rate').`

            You can also input the integer index of the attribute you would like to
            pull or the actual enum from swmm.toolkit.shared_enum.SubcatchAttribute.

            Setting to None indicates all attributes.

        asframe: bool
            A switch to return an indexed DataFrame. Set to False to get an array of values only, defaults to True.

        Returns
        -------
        Union[pd.DataFrame, np.ndarray]
            A DataFrame or ndarray of attribute values in each column for requested simulation time.

        """

        attributeArray, attributeIndexArray = self._validateAttribute(
            attribute, self.subcatch_attributes
        )

        timeIndex = self._time2step([time])[0]

        values = np.stack(
            [
                output.get_subcatch_attribute(self._handle, timeIndex, scAttr)
                for scAttr in attributeIndexArray
            ],
            axis=1,
        )

        if not asframe:
            return values

        dfIndex = pd.Index(self.subcatchments, name="subcatchment")

        return pd.DataFrame(values, index=dfIndex, columns=attributeArray)

    @output_open_handler
    def node_attribute(
        self,
        time: Union[str, int, datetime],
        attribute: Union[int, str, Sequence[Union[int, str]], None] = (
            "invert_depth",
            "flooding_losses",
            "total_inflow",
        ),
        asframe: bool = True,
    ) -> Union[pd.DataFrame, np.ndarray]:
        """For all nodes at a given time, get one or more attributes.

        Parameters
        ----------
        time : Union[str, int, datetime]
            The datetime or simulation index for which to pull data, defaults to None

        attribute : Union[int, str, Sequence[Union[int, str]], None],
            The attribute index or name.

            On of:

            **invert_depth, hydraulic_head, ponded_volume, lateral_inflow,
            total_inflow, flooding_losses**.

            defaults to: `('invert_depth','flooding_losses','total_inflow')`

            You can also input the integer index of the attribute you would like to
            pull or the actual enum from swmm.toolkit.shared_enum.NodeAttribute.

            Setting to None indicates all attributes.

        asframe: bool
            A switch to return an indexed DataFrame. Set to False to get an array of values only, defaults to True.

        Returns
        -------
        Union[pd.DataFrame, np.ndarray]
            A DataFrame or ndarray of attribute values in each column for requested simulation time.

        """
        attributeArray, attributeIndexArray = self._validateAttribute(
            attribute, self.node_attributes
        )

        timeIndex = self._time2step([time])[0]

        values = np.stack(
            [
                output.get_node_attribute(self._handle, timeIndex, ndAttr)
                for ndAttr in attributeIndexArray
            ],
            axis=1,
        )

        if not asframe:
            return values

        dfIndex = pd.Index(self.nodes, name="node")

        return pd.DataFrame(values, index=dfIndex, columns=attributeArray)

    @output_open_handler
    def link_attribute(
        self,
        time: Union[str, int, datetime],
        attribute: Union[int, str, Sequence[Union[int, str]], None] = (
            "flow_rate",
            "flow_velocity",
            "flow_depth",
        ),
        asframe: bool = True,
    ) -> Union[pd.DataFrame, np.ndarray]:
        """For all links at a given time, get one or more attributes.

        Parameters
        ----------
        time : Union[str, int, datetime]
            The datetime or simulation index for which to pull data, defaults to None.

        attribute : Union[int, str, Sequence[Union[int, str]], None]
            The attribute index or name.

            On of:

            flow_rate, flow_depth, flow_velocity, flow_volume, capacity,

            defaults to `('flow_rate','flow_velocity','flow_depth')`

            You can also input the integer index of the attribute you would like to
            pull or the actual enum from swmm.toolkit.shared_enum.LinkAttribute.

            Setting to None indicates all attributes.

        asframe: bool
            A switch to return an indexed DataFrame. Set to False to get an array of values only, defaults to True.

        Returns
        -------
        pd.DataFrame
            A DataFrame of attribute values in each column for requested simulation time.

        """
        attributeArray, attributeIndexArray = self._validateAttribute(
            attribute, self.link_attributes
        )

        timeIndex = self._time2step([time])[0]

        values = np.stack(
            [
                output.get_link_attribute(self._handle, timeIndex, lnkAttr)
                for lnkAttr in attributeIndexArray
            ],
            axis=1,
        )

        if not asframe:
            return values

        dfIndex = pd.Index(self.links, name="link")

        return pd.DataFrame(values, index=dfIndex, columns=attributeArray)

    @output_open_handler
    def system_attribute(
        self,
        time: Union[str, int, datetime],
        attribute: Union[int, str, Sequence[Union[int, str]], None] = None,
        asframe=True,
    ) -> Union[pd.DataFrame, np.ndarray]:
        """For all nodes at given time, get a one or more attributes.

        Parameters
        ----------
        time : Union[str, int, datetime]
            The datetime or simulation index for which to pull data, defaults to None.

        attribute : Union[int, str, Sequence[Union[int, str]], None]
            The attribute index or name.

            On of:

            **air_temp, rainfall, snow_depth, evap_infil_loss, runoff_flow,
            dry_weather_inflow, gw_inflow, rdii_inflow, direct_inflow, total_lateral_inflow,
            flood_losses, outfall_flows, volume_stored, evap_rate**.

            defaults to `None`.

            You can also input the integer index of the attribute you would like to
            pull or the actual enum from swmm.toolkit.shared_enum.SystemAttribute.

            Setting to None indicates all attributes.

        asframe: bool
            A switch to return an indexed DataFrame. Set to False to get an array of values only, defaults to True.

        Returns
        -------
        Union[pd.DataFrame,np.ndarray]
            A DataFrame of attribute values in each column for requested simulation time.

        """

        attributeArray, attributeIndexArray = self._validateAttribute(
            attribute, self.system_attributes
        )

        timeIndex = self._time2step([time])[0]

        values = np.asarray(
            [
                output.get_system_attribute(self._handle, timeIndex, sysAttr)
                for sysAttr in attributeIndexArray
            ]
        )

        if not asframe:
            return values

        dfIndex = pd.Index(attributeArray, name="attribute")

        return pd.DataFrame(values, index=dfIndex, columns=["result"])

    ####### result getters #######

    @output_open_handler
    def subcatch_result(
        self,
        subcatchment: Union[int, str, Sequence[Union[int, str]], None],
        time: Union[int, str, Sequence[Union[int, str]], None],
        asframe: bool = True,
    ) -> Union[pd.DataFrame, np.ndarray]:
        """For a subcatchment at one or more given times, get all attributes.

        Only one of `subcatchment` or `time` can be multiple (eg. a list), not both.

        Parameters
        ----------
        subcatchment : Union[int, str, Sequence[Union[int, str]], None],
            The subcatchment(s) name(s) or index(s).

        time: Union[int, str, Sequence[Union[int, str]], None],
            THe datetime(s) or simulation index(s).

        asframe: bool
            A switch to return an indexed DataFrame. Set to False to get an array of values only, defaults to True.

        Returns
        -------
        Union[pd.DataFrame,np.ndarray]
            A DataFrame or ndarray of all attribute values subcatchment(s) at given time(s).

        """

        if isinstance(subcatchment, arrayish) and isinstance(time, arrayish):
            raise Exception("Can only have multiple of one of subcatchment and time")

        elif isinstance(subcatchment, arrayish):
            label = "subcatchment"
            labels, indices = self._validateElement(subcatchment, self.subcatchments)
            timeIndex = self._time2step([time])[0]

            values = np.vstack(
                [
                    output.get_subcatch_result(self._handle, timeIndex, idx)
                    for idx in indices
                ]
            )

        else:
            label = "datetime"
            times = self.timeIndex if time is None else np.atleast_1d(time)
            indices = self._time2step(times)

            # since the timeIndex matches on nearst, we rebuild
            # the label in case it wasn't exact
            labels = self.timeIndex[indices]
            subcatchmentIndex = self._subcatchmentIndex(subcatchment)

            values = np.atleast_2d(
                np.vstack(
                    [
                        output.get_subcatch_result(self._handle, idx, subcatchmentIndex)
                        for idx in indices
                    ]
                )
            )

        if not asframe:
            return values

        dfIndex = pd.Index(labels, name=label)

        return pd.DataFrame(
            values, index=dfIndex, columns=list(self.subcatch_attributes.keys())
        )

    @output_open_handler
    def node_result(
        self,
        node: Union[int, str, Sequence[Union[int, str]], None],
        time: Union[int, str, Sequence[Union[int, str]], None],
        asframe: bool = True,
    ) -> Union[pd.DataFrame, np.ndarray]:
        """For one or more nodes at one or more given times, get all attributes.

        Only one of `node` or `time` can be multiple (eg. a list), not both.

        Parameters
        ----------
        node : Union[int, str, Sequence[Union[int, str]], None],
            The node(s) name(s) or index(s).

        time: Union[int, str, Sequence[Union[int, str]], None],
            The datetime(s) or simulation index(s).

        asframe: bool
            A switch to return an indexed DataFrame. Set to False to get an array of values only, defaults to True.

        Returns
        -------
        Union[pd.DataFrame,np.ndarray]
            A DataFrame or ndarray of all attribute values nodes(s) at given time(s).

        """
        if isinstance(node, arrayish) and isinstance(time, arrayish):
            raise Exception("Can only have multiple of one of node and time")

        elif isinstance(node, arrayish):
            label = "node"
            labels, indices = self._validateElement(node, self.nodes)
            timeIndex = self._time2step([time])[0]
            values = np.vstack(
                [
                    output.get_node_result(self._handle, timeIndex, idx)
                    for idx in indices
                ]
            )

        else:
            label = "datetime"
            times = self.timeIndex if time is None else np.atleast_1d(time)
            indices = self._time2step(times)

            # since the timeIndex matches on nearst, we rebuild
            # the label in case it wasn't exact
            labels = self.timeIndex[indices]
            nodeIndex = self._nodeIndex(node)

            values = np.atleast_2d(
                np.vstack(
                    [
                        output.get_node_result(self._handle, idx, nodeIndex)
                        for idx in indices
                    ]
                )
            )

        if not asframe:
            return values

        dfIndex = pd.Index(labels, name=label)

        return pd.DataFrame(
            values, index=dfIndex, columns=list(self.node_attributes.keys())
        )

    @output_open_handler
    def link_result(
        self,
        link: Union[int, str, Sequence[Union[int, str]], None],
        time: Union[int, str, Sequence[Union[int, str]], None],
        asframe: bool = True,
    ) -> Union[pd.DataFrame, np.ndarray]:
        """For a link at one or more given times, get all attributes.

        Only one of link or time can be multiple.

        Parameters
        ----------
        link : Union[int, str, Sequence[Union[int, str]], None],
            The link(s) name(s) or index(s).

        time: Union[int, str, Sequence[Union[int, str]], None],
            The datetime(s) or simulation index(s).

        asframe: bool
            A switch to return an indexed DataFrame. Set to False to get an array of values only, defaults to True.

        Returns
        -------
        Union[pd.DataFrame,np.ndarray]
            A DataFrame or ndarray of all attribute values link(s) at given time(s).

        """
        if isinstance(link, arrayish) and isinstance(time, arrayish):
            raise Exception("Can only have multiple of one of link and time")

        elif isinstance(link, arrayish):
            label = "link"
            labels, indices = self._validateElement(link, self.links)
            timeIndex = self._time2step([time])[0]

            values = np.vstack(
                [
                    output.get_link_result(self._handle, timeIndex, idx)
                    for idx in indices
                ]
            )

        else:
            label = "datetime"
            times = self.timeIndex if time is None else np.atleast_1d(time)
            indices = self._time2step(times)

            # since the timeIndex matches on nearst, we rebuild
            # the label in case it wasn't exact
            labels = self.timeIndex[indices]

            linkIndex = self._linkIndex(link)
            values = np.atleast_2d(
                np.vstack(
                    [
                        output.get_link_result(self._handle, idx, linkIndex)
                        for idx in indices
                    ]
                )
            )

        if not asframe:
            return values

        dfIndex = pd.Index(labels, name=label)

        return pd.DataFrame(
            values, index=dfIndex, columns=list(self.link_attributes.keys())
        )

    @output_open_handler
    def system_result(
        self,
        time: Union[str, int, datetime],
        asframe=True,
    ) -> Union[pd.DataFrame, np.ndarray]:
        """For a given time, get all system attributes.

        Parameters
        ----------
        time : Union[str, int, datetime]
            The datetime or simulation index.

        asframe: bool
            A switch to return an indexed DataFrame. Set to False to get an array of values only, defaults to True.

        Returns
        -------
        Union[pd.DataFrame,np.ndarray]
            A DataFrame of attribute values in each row for requested simulation time.

        """

        timeIndex = self._time2step([time])[0]

        values = np.asarray(output.get_system_result(self._handle, timeIndex, 0))

        if not asframe:
            return values

        dfIndex = pd.Index(self.system_attributes, name="attribute")

        return pd.DataFrame(values, index=dfIndex, columns=["Result"])

    def getStructure(self, link, node):
        """
        Return a structure object for a given list of links and nodes.

        Parameters
        ----------
        link : Union[str, Sequence[str]]
            The list of links that belong to the structure.
        node : Union[str, Sequence[str]]
            The list of nodes that below to the structure.

        Returns
        -------
        Structure
            Structure comprised of the given links and nodes.
        """
        return Structure(self, link, node)

    # close outfile when object deleted
    # this doesn't always get called on sys.exit()
    # better to use output object with context
    # manager to ensure _open() and _close() are always closed
    # in some cases, you can get a memory leak message from swig:
    # >>> exit()
    # swig/python detected a memory leak of type 'struct Handle *', no destructor found.
    def __del__(self) -> NoReturn:
        """
        Destructor for outfile handle

        :return: Nothing
        :rtype: NoReturn
        """
        self._close()

    # method used for context manager with statement
    def __enter__(self):
        self._open()
        return self

    # method used for context manager with statement
    def __exit__(self, *arg) -> NoReturn:
        self._close()
