"""Tests for `swmm-pandas` package."""


import os
from datetime import datetime

import numpy as np
import pandas as pd
import pytest
from numpy.core.numeric import allclose

from swmm.pandas import Output
from swmm.pandas.output.enums import subcatch_attribute

this_dir, this_filename = os.path.split(__file__)
outPath = os.path.join(this_dir, "Model.out")


@pytest.fixture(scope="module")
def outfile():
    out = Output(outPath)
    yield out
    out._close()


def testOpenWarning(outfile):
    """Test outfile has a pollutant named rainfall. This should raise warning"""
    with pytest.warns(UserWarning):
        outfile._open()


def test_output_props(outfile):
    assert outfile.project_size == [3, 9, 8, 1, 3]
    assert isinstance(outfile._version, int)
    assert outfile.start == datetime(1900, 1, 1, 0, 0)
    assert outfile.end == datetime(1900, 1, 2, 0, 0)
    assert len(outfile.node_attributes) == 9
    assert len(outfile.subcatch_attributes) == 11
    assert len(outfile.link_attributes) == 8
    assert outfile.period == 288
    assert outfile.pollutants == ("groundwater", "pol_rainfall", "sewage")
    assert outfile.report == 300
    assert outfile._unit == (0, 0, 0, 0, 0)


# test series getters
# check values against those validated in EPA SWMM GUI Release 5.1.015
def test_subcatch_series(outfile):
    arr = outfile.subcatch_series(
        ["SUB1", "SUB2"], ["runoff_rate", "pol_rainfall"], asframe=False
    )
    assert type(arr) == np.ndarray
    df = outfile.subcatch_series(["SUB1", "SUB2"], ["runoff_rate", "pol_rainfall"])
    ts = pd.Timestamp("1/1/1900 01:05")
    assert type(df) == pd.DataFrame
    refarray = np.array([[0.005574, 100], [0.021814, 100]])
    assert np.allclose(
        df.loc[[(ts, "SUB1"), (ts, "SUB2")], :].to_numpy(), refarray, atol=0.000001
    )


def test_node_series(outfile):
    arr = outfile.node_series(
        ["JUNC3", "JUNC4"], ["invert_depth", "sewage"], asframe=False
    )
    assert type(arr) == np.ndarray
    df = outfile.node_series(["JUNC3", "JUNC4"], ["invert_depth", "sewage"])
    ts = pd.Timestamp("1/1/1900 01:05")
    assert type(df) == pd.DataFrame
    refarray = np.array([[0.632486, 81.739952], [0.840065, 82.240310]])
    assert np.allclose(
        df.loc[[(ts, "JUNC3"), (ts, "JUNC4")], :].to_numpy(), refarray, atol=0.000001
    )


def test_link_series(outfile):
    arr = outfile.link_series(
        ["COND4", "PUMP1"], ["flow_rate", "groundwater"], asframe=False
    )
    assert type(arr) == np.ndarray
    df = outfile.link_series("PUMP1", ["flow_rate", "groundwater"])
    ts = pd.Timestamp("1/1/1900 01:05")
    assert type(df) == pd.DataFrame
    refarray = np.array([1.038260, 10.866543])
    assert np.allclose(df.loc[ts, :].to_numpy(), refarray, atol=0.000001)


def test_system_series(outfile):
    arr = outfile.system_series(["gw_inflow", "flood_losses"], asframe=False)
    assert type(arr) == np.ndarray
    df = outfile.system_series(["gw_inflow", "flood_losses"])
    ts = pd.Timestamp("1/1/1900 13:30")
    assert type(df) == pd.DataFrame
    refarray = np.array([0.154941, 3.971512])
    assert np.allclose(df.loc[ts].to_numpy(), refarray, atol=0.000001)


# test attribute getters
# check values against those validated in EPA SWMM GUI Release 5.1.015
def test_subcatch_attribute(outfile):
    ts = pd.Timestamp("1/1/1900 13:30")
    arr = outfile.subcatch_attribute(ts, None, asframe=False)
    assert type(arr) == np.ndarray
    df = outfile.subcatch_attribute(ts, None)
    assert df.shape == (3, 11)
    refarray = np.array(
        [
            0.156000,
            0.000000,
            0.000000,
            0.324994,
            2.800647,
            0.115297,
            -3.141794,
            0.280193,
            0.000000,
            100.000000,
            0.000000,
        ]
    )
    assert np.allclose(df.loc["SUB3"].to_numpy(), refarray, atol=0.000001)


def test_node_attribute(outfile):
    ts = pd.Timestamp("1/1/1900 13:30")
    arr = outfile.node_attribute(ts, None, asframe=False)
    assert type(arr) == np.ndarray
    df = outfile.node_attribute(ts, None)
    assert df.shape == (9, 9)
    refarray = np.array(
        [
            13.421694,
            9.951694,
            10073.076200,
            0.000000,
            3.270415,
            0.803252,
            0.528808,
            95.420525,
            3.958632,
        ]
    )
    assert np.allclose(df.loc["JUNC3"].to_numpy(), refarray, atol=0.000001)


def test_link_attribute(outfile):
    ts = pd.Timestamp("1/1/1900 13:30")
    arr = outfile.link_attribute(ts, None, asframe=False)
    assert type(arr) == np.ndarray
    df = outfile.link_attribute(ts, None)
    assert df.shape == (8, 8)
    refarray = np.array(
        [
            8.769582,
            1.500000,
            3.470112,
            1851.105590,
            1.000000,
            0.861774,
            92.784477,
            6.229438,
        ]
    )
    assert np.allclose(df.loc["COND4"].to_numpy(), refarray, atol=0.000001)


def test_system_attribute(outfile):
    ts = pd.Timestamp("1/1/1900 13:30")
    arr = outfile.system_attribute(ts, "rainfall", asframe=False)
    assert type(arr) == np.ndarray
    df = outfile.system_attribute(ts, "rainfall")
    assert df.shape == (1, 1)
    assert round(df.loc["rainfall", "result"], 2) == 0.16


# test result getters
# check values against those validated in EPA SWMM GUI Release 5.1.015
def test_subcatch_result(outfile):
    ts = pd.Timestamp("1/1/1900 13:30")
    arr = outfile.subcatch_result("SUB3", ts, asframe=False)
    assert type(arr) == np.ndarray
    df = outfile.subcatch_result("SUB3", ts)
    assert df.shape == (1, 11)
    refarray = refarray = np.array(
        [
            0.156000,
            0.000000,
            0.000000,
            0.324994,
            2.800647,
            0.115297,
            -3.141794,
            0.280193,
            0.000000,
            100.000000,
            0.000000,
        ]
    )
    assert np.allclose(df.to_numpy(), refarray, atol=0.000001)


def test_node_result(outfile):
    ts = pd.Timestamp("1/1/1900 13:30")
    ts2 = pd.Timestamp("1/1/1900 15:30")
    arr = outfile.node_result("JUNC3", [ts, ts2], asframe=False)
    assert type(arr) == np.ndarray
    df = outfile.node_result("JUNC3", [ts, ts2])
    assert df.shape == (2, 9)
    refarray = np.array(
        [
            [
                13.421694,
                9.951694,
                10073.076172,
                0.000000,
                3.270415,
                0.803252,
                0.528808,
                95.420525,
                3.958632,
            ],
            [
                2.997494,
                -0.472506,
                0.000000,
                0.000000,
                1.357396,
                0.000000,
                5.058118,
                75.098473,
                19.795525,
            ],
        ]
    )
    assert np.allclose(df.to_numpy(), refarray, atol=0.000001)


def test_link_result(outfile):
    ts = 161
    arr = outfile.link_result(["COND4", "COND2"], ts, asframe=False)
    assert type(arr) == np.ndarray
    df = outfile.link_result(["COND4", "COND2"], ts)
    assert df.shape == (2, 8)
    refarray = np.array(
        [
            [
                8.769582,
                1.500000,
                3.470112,
                1851.105591,
                1.000000,
                0.861774,
                92.784477,
                6.229438,
            ],
            [
                -2.467724,
                0.750000,
                -3.210221,
                460.856079,
                1.000000,
                0.509358,
                95.575531,
                3.825584,
            ],
        ]
    )
    assert np.allclose(df.to_numpy(), refarray, atol=0.000001)


def test_system_result(outfile):
    ts = pd.Timestamp("1/1/1900 13:30")
    arr = outfile.system_result(ts, asframe=False)
    assert type(arr) == np.ndarray
    df = outfile.system_result(ts)
    assert df.shape == (15, 1)
    refarray = np.array(
        [
            70.000000,
            0.156000,
            0.000000,
            0.255805,
            3.695478,
            1.00800,
            0.154941,
            0.000000,
            0.000000,
            4.85842,
            3.971513,
            9.427255,
            56656.34375,
            0.000000,
            0.000000,
        ]
    )

    assert np.allclose(df.Result.to_numpy(), refarray, atol=0.000001)


@pytest.mark.parametrize(
    "inputAttribute,inputValidAttribute,expectedAttribute,expectedIndex,out",
    [
        (
            "rainfall",
            subcatch_attribute,
            ["rainfall"],
            [subcatch_attribute["rainfall"]],
            "outfile",
        ),
        (
            ["rainfall", 3],
            subcatch_attribute,
            ["rainfall", "infil_loss"],
            [subcatch_attribute["rainfall"], subcatch_attribute["infil_loss"]],
            "outfile",
        ),
        (
            ["rainfall", 3, subcatch_attribute["soil_moisture"]],
            subcatch_attribute,
            ["rainfall", "infil_loss", "soil_moisture"],
            [
                subcatch_attribute["rainfall"],
                subcatch_attribute["infil_loss"],
                subcatch_attribute["soil_moisture"],
            ],
            "outfile",
        ),
    ],
)
def test_validateAttribute(
    inputAttribute,
    inputValidAttribute,
    expectedAttribute,
    expectedIndex,
    out,
    request,
):
    outfile = request.getfixturevalue(out)
    attributeArray, attributeIndexArray = outfile._validateAttribute(
        inputAttribute, inputValidAttribute
    )
    assert attributeArray == expectedAttribute
    assert attributeIndexArray == expectedIndex


@pytest.mark.parametrize(
    "inputElement,inputValidElements,expectedElement,expectedElementIndex,out",
    [
        (
            "COND1",
            ("COND1", "COND2", "COND3"),
            ["COND1"],
            [0],
            "outfile",
        ),
        (
            ["COND3", 0],
            ("COND1", "COND2", "COND3"),
            ["COND3", "COND1"],
            [2, 0],
            "outfile",
        ),
        (
            None,
            ("COND1", "COND2", "COND3"),
            ["COND1", "COND2", "COND3"],
            [0, 1, 2],
            "outfile",
        ),
    ],
)
def test_validateElement(
    inputElement,
    inputValidElements,
    expectedElement,
    expectedElementIndex,
    out,
    request,
):
    outfile = request.getfixturevalue(out)
    elementArray, elementIndexArray = outfile._validateElement(
        inputElement, inputValidElements
    )
    assert elementArray == expectedElement
    assert elementIndexArray == expectedElementIndex


# def test_elementIndex(
#     elementID, indexSquence, elementType, expectedIndex, out, request
# ):
#     outfile = request.getfixturevalue(out)
#     assert outfile._elementIndex(elementID,indexSquence) == expectedIndex
