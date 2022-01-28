import os
from sqlite3 import Timestamp

import pytest
from swmm.pandas import Report
from pandas import Timedelta, Timestamp, DataFrame
from numpy import allclose, all, array, nan
from swmm.pandas import test_rpt_path


@pytest.fixture(scope="module")
def rptfile():
    return Report(test_rpt_path)


def test_analysis_options(rptfile):
    reference = DataFrame(
        {
            "Setting": {
                "Flow Units": "CFS",
                "Rainfall/Runoff": "YES",
                "RDII": "NO",
                "Snowmelt": "YES",
                "Groundwater": "YES",
                "Flow Routing": "YES",
                "Ponding Allowed": "YES",
                "Water Quality": "YES",
                "Infiltration Method": "GREEN_AMPT",
                "Flow Routing Method": "DYNWAVE",
                "Surcharge Method": "EXTRAN",
                "Starting Date": "01/01/1900 00:00:00",
                "Ending Date": "01/02/1900 00:00:00",
                "Antecedent Dry Days": "0.0",
                "Report Time Step": "00:05:00",
                "Wet Time Step": "00:05:00",
                "Dry Time Step": "01:00:00",
                "Routing Time Step": "15.00 sec",
                "Variable Time Step": "YES",
                "Maximum Trials": "10",
                "Number of Threads": "1",
                "Head Tolerance": "0.005000 ft",
            }
        },
    )
    reference.index.name = "Option"
    opts = rptfile.analysis_options
    assert all(opts.sort_index() == reference)


def test_runoff_quantity_continuity(rptfile):
    reference = array(
        [
            [0.0, 0.0],
            [14.998, 3.0],
            [0.0, 0.0],
            [9.339, 1.868],
            [5.489, 1.098],
            [0.0, 0.0],
            [0.0, 0.0],
            [0.187, 0.037],
            [-0.108, nan],
        ]
    )

    test = rptfile.runoff_quantity_continuity

    assert allclose(test, reference, equal_nan=True)


def test_runoff_quality_continuity(rptfile):
    reference = array(
        [
            [0.000000e00, 0.000000e00, 0.000000e00],
            [0.000000e00, 0.000000e00, 0.000000e00],
            [0.000000e00, 4.075669e03, 0.000000e00],
            [0.000000e00, 0.000000e00, 0.000000e00],
            [0.000000e00, 2.537844e03, 0.000000e00],
            [0.000000e00, 0.000000e00, 0.000000e00],
            [0.000000e00, 1.491499e03, 0.000000e00],
            [0.000000e00, 5.071200e01, 0.000000e00],
            [0.000000e00, -1.080000e-01, 0.000000e00],
        ]
    )

    test = rptfile.runoff_quality_continuity
    assert allclose(test, reference)


def test_groundwater_continuity(rptfile):
    reference = array(
        [
            [1.272478e03, 2.544960e02],
            [9.339000e00, 1.868000e00],
            [0.000000e00, 0.000000e00],
            [0.000000e00, 0.000000e00],
            [0.000000e00, 0.000000e00],
            [2.770000e-01, 5.500000e-02],
            [1.281540e03, 2.563080e02],
            [0.000000e00, nan],
        ]
    )

    test = rptfile.groundwater_continuity
    assert allclose(test, reference, equal_nan=True)


def test_flow_routing_continuity(rptfile):
    reference = array(
        [
            [1.787, 0.582],
            [5.487, 1.788],
            [0.277, 0.09],
            [0.0, 0.0],
            [0.0, 0.0],
            [6.977, 2.274],
            [0.529, 0.172],
            [0.0, 0.0],
            [0.0, 0.0],
            [0.0, 0.0],
            [0.055, 0.018],
            [-0.158, nan],
        ]
    )

    test = rptfile.flow_routing_continuity
    assert allclose(test, reference, equal_nan=True)


def test_flow_routing_continuity(rptfile):
    reference = array(
        [
            [1.787, 0.582],
            [5.487, 1.788],
            [0.277, 0.09],
            [0.0, 0.0],
            [0.0, 0.0],
            [6.977, 2.274],
            [0.529, 0.172],
            [0.0, 0.0],
            [0.0, 0.0],
            [0.0, 0.0],
            [0.055, 0.018],
            [-0.158, nan],
        ]
    )

    test = rptfile.flow_routing_continuity
    assert allclose(test, reference, equal_nan=True)


def test_quality_routing_continuity(rptfile):
    reference = array(
        [
            [0.000000e00, 0.000000e00, 4.854910e02],
            [0.000000e00, 1.490454e03, 0.000000e00],
            [7.523300e01, 0.000000e00, 0.000000e00],
            [0.000000e00, 0.000000e00, 0.000000e00],
            [0.000000e00, 0.000000e00, 0.000000e00],
            [7.346500e01, 1.347329e03, 4.751520e02],
            [9.100000e-01, 1.361150e02, 6.717000e00],
            [0.000000e00, 0.000000e00, 0.000000e00],
            [0.000000e00, 0.000000e00, 0.000000e00],
            [0.000000e00, 0.000000e00, 0.000000e00],
            [2.271000e00, 5.967000e00, 6.828000e00],
            [-1.878000e00, 7.000000e-02, -6.600000e-01],
        ]
    )

    test = rptfile.quality_routing_continuity
    assert allclose(test, reference)


def test_highest_continuity_errors(rptfile):
    reference = array([["Node", 1.52]], dtype=object)
    test = rptfile.highest_continuity_errors.to_numpy()
    assert (reference == test).all()


def test_time_step_critical_elements(rptfile):
    reference = array([["Link", 60.11], ["Link", 39.32]], dtype=object)
    test = rptfile.time_step_critical_elements.to_numpy()
    assert (reference == test).all()


def test_highest_flow_instability_indexes(rptfile):
    reference = array([["Link", 1]], dtype=object)
    test = rptfile.highest_flow_instability_indexes.to_numpy()
    assert (reference == test).all()


def test_runoff_summary(rptfile):
    reference = array(
        [
            [3.0, 0.0, 0.0, 2.28, 0.91, 0.25, 0.71, 0.1, 2.96, 0.236],
            [3.0, 0.0, 0.0, 2.12, 1.2, 0.26, 0.86, 0.4, 11.17, 0.287],
            [3.0, 0.0, 0.0, 1.7, 1.82, 0.34, 1.25, 1.29, 32.64, 0.418],
        ]
    )

    test = rptfile.runoff_summary
    assert allclose(test, reference)


def test_groundwater_summary(rptfile):
    reference = array(
        [
            [2.28, 0.0, 0.0, 0.04, 0.01, 0.28, 2.88, 0.28, 3.37],
            [2.12, 0.0, 0.0, 0.04, 0.04, 0.28, 0.32, 0.28, 0.79],
            [1.7, 0.0, 0.0, 0.07, 0.13, 0.28, -3.31, 0.28, -2.93],
        ]
    )

    test = rptfile.groundwater_summary
    assert allclose(test, reference)


def test_washoff_summary(rptfile):
    reference = array([[0.0, 80.229, 0.0], [0.0, 331.693, 0.0], [0.0, 1079.577, 0.0]])

    test = rptfile.washoff_summary
    assert allclose(test, reference)


def test_node_depth_summary(rptfile):
    reference = array(
        [
            ["JUNCTION", 0.75, 10.25, 11.75, Timedelta("0 days 12:30:00"), 10.25],
            ["JUNCTION", 1.61, 4.39, 3.35, Timedelta("0 days 12:30:00"), 4.39],
            ["JUNCTION", 3.74, 13.49, 10.02, Timedelta("0 days 13:44:00"), 13.49],
            ["JUNCTION", 5.1, 21.71, 16.46, Timedelta("0 days 12:45:00"), 21.71],
            ["JUNCTION", 4.66, 15.03, 8.53, Timedelta("0 days 13:14:00"), 15.03],
            ["JUNCTION", 1.14, 1.66, 1.66, Timedelta("0 days 11:40:00"), 1.65],
            ["OUTFALL", 0.7, 0.95, 1.05, Timedelta("0 days 11:40:00"), 0.95],
            ["OUTFALL", 0.0, 0.0, -1.04, Timedelta("0 days 00:00:00"), 0.0],
            ["STORAGE", 7.5, 21.75, 6.5, Timedelta("0 days 12:24:00"), 21.75],
        ],
        dtype=object,
    )

    test = rptfile.node_depth_summary
    assert all(test == reference)


def test_node_inflow_summary(rptfile):
    reference = array(
        [
            ["JUNCTION", 2.96, 2.96, Timedelta("0 days 12:30:00"), 0.102, 0.102, 0.461],
            [
                "JUNCTION",
                11.42,
                16.41,
                Timedelta("0 days 12:30:00"),
                0.545,
                0.857,
                0.5529999999999999,
            ],
            ["JUNCTION", 0.0, 5.0, Timedelta("0 days 12:41:00"), 0.0, 0.502, 1.54],
            [
                "JUNCTION",
                33.53,
                33.53,
                Timedelta("0 days 12:30:00"),
                1.81,
                2.1,
                0.013000000000000001,
            ],
            ["JUNCTION", 0.0, 12.32, Timedelta("0 days 11:51:00"), 0.0, 1.87, 0.405],
            ["JUNCTION", 0.0, 5.8, Timedelta("0 days 11:40:00"), 0.0, 1.7, 0.198],
            ["OUTFALL", 0.0, 5.8, Timedelta("0 days 11:40:00"), 0.0, 1.7, 0.0],
            [
                "OUTFALL",
                0.0,
                16.39,
                Timedelta("0 days 12:30:00"),
                0.0,
                0.5760000000000001,
                0.0,
            ],
            [
                "STORAGE",
                0.0,
                12.32,
                Timedelta("0 days 11:51:00"),
                0.0,
                1.86,
                -0.8909999999999999,
            ],
        ],
        dtype=object,
    )

    test = rptfile.node_inflow_summary
    assert all(test == reference)


def test_node_surcharge_summary(rptfile):
    reference = array(
        [
            ["JUNCTION", 1.49, 9.251, 0.0],
            ["JUNCTION", 4.15, 11.99, 0.0],
            ["JUNCTION", 4.48, 19.712, 0.0],
            ["JUNCTION", 4.78, 13.026, 0.0],
            ["JUNCTION", 8.01, 0.659, 7.341],
        ],
        dtype=object,
    )

    test = rptfile.node_surchage_summary
    assert all(test == reference)


def test_node_flooding_summary(rptfile):
    reference = array(
        [
            [0.07, 0.87, Timedelta("0 days 11:49:00"), 0.0, 0.001],
            [3.19, 2.8, Timedelta("0 days 12:38:00"), 0.081, 1.99],
            [3.1, 18.33, Timedelta("0 days 12:15:00"), 0.318, 7.912000000000001],
            [
                3.08,
                4.37,
                Timedelta("0 days 12:24:00"),
                0.07400000000000001,
                1.8259999999999998,
            ],
            [2.47, 4.21, Timedelta("0 days 13:14:00"), 0.172, 0.0],
        ],
        dtype=object,
    )

    test = rptfile.node_flooding_summary
    assert all(test == reference)


def test_storage_volume_summary(rptfile):
    reference = array(
        [
            [
                3.0980000000000003,
                34,
                0,
                0,
                8.982999999999999,
                100,
                Timedelta("0 days 12:24:00"),
                5.8,
            ]
        ],
        dtype=object,
    )

    test = rptfile.storage_volume_summary
    assert all(test == reference)


def test_outfall_loading_summary(rptfile):
    reference = array(
        [
            [
                9.88800e01,
                3.26000e00,
                5.80000e00,
                1.69800e00,
                6.92630e01,
                8.99065e02,
                4.48553e02,
            ],
            [
                2.54900e01,
                5.81000e00,
                1.63900e01,
                5.76000e-01,
                4.20700e00,
                4.48265e02,
                2.66240e01,
            ],
        ]
    )

    test = rptfile.outfall_loading_summary

    assert allclose(test, reference)


def test_link_flow_summary(rptfile):
    reference = array(
        [
            ["CONDUIT", 2.93, Timedelta("0 days 12:30:00"), 3.74, 1.92, 1.0],
            ["CONDUIT", 2.48, Timedelta("0 days 13:45:00"), 3.23, 1.86, 1.0],
            ["CONDUIT", 5.0, Timedelta("0 days 12:41:00"), 4.0, 2.42, 1.0],
            ["CONDUIT", 12.32, Timedelta("0 days 11:51:00"), 4.87, 2.73, 1.0],
            ["CONDUIT", 12.32, Timedelta("0 days 11:51:00"), 7.84, 17.51, 1.0],
            ["CONDUIT", 5.8, Timedelta("0 days 11:40:00"), 7.44, 2.41, 0.97],
            ["PUMP", 5.8, Timedelta("0 days 11:40:00"), 1.0, nan, nan],
            ["WEIR", 16.39, Timedelta("0 days 12:30:00"), 0.43, nan, nan],
        ],
        dtype=object,
    )

    test = rptfile.link_flow_summary.to_numpy()

    assert all(reference[:, [0, 2]] == test[:, [0, 2]])
    assert allclose(
        reference[:, [1, 3, 4, 5]].astype(float),
        test[:, [1, 3, 4, 5]].astype(float),
        equal_nan=True,
    )


def test_flow_classification_summary(rptfile):
    reference = array(
        [
            [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.84, 0.0],
            [1.0, 0.0, 0.0, 0.0, 0.31, 0.0, 0.0, 0.68, 0.0, 0.0],
            [1.0, 0.0, 0.0, 0.0, 0.5, 0.0, 0.0, 0.49, 0.06, 0.0],
            [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.77, 0.0],
            [1.0, 0.0, 0.0, 0.0, 0.27, 0.0, 0.0, 0.73, 0.0, 0.0],
            [2.32, 0.01, 0.0, 0.0, 0.99, 0.0, 0.0, 0.0, 0.0, 0.0],
        ]
    )

    test = rptfile.flow_classification_summary

    assert allclose(reference, test)


def test_conduit_surcharge_summary(rptfile):
    reference = array(
        [
            [1.490e00, 1.490e00, 4.520e00, 7.400e-01, 7.400e-01],
            [4.150e00, 4.520e00, 4.150e00, 3.920e00, 1.600e-01],
            [4.150e00, 4.150e00, 4.480e00, 1.870e00, 1.000e-02],
            [4.480e00, 4.480e00, 4.780e00, 3.750e00, 3.750e00],
            [3.790e00, 4.780e00, 3.790e00, 2.351e01, 3.740e00],
            [1.000e-02, 1.000e-02, 8.000e00, 8.070e00, 1.000e-02],
        ]
    )

    test = rptfile.conduit_surcharge_summary

    assert allclose(reference, test)


def test_pumping_summary(rptfile):
    reference = array([[97.74, 1.0, 0.0, 3.26, 5.8, 1.701, 53.62, 0.0, 18.1]])

    test = rptfile.pumping_summary

    assert allclose(reference, test)


def test_link_pollutant_load_summary(rptfile):
    reference = array(
        [
            [4.389000e00, 7.990000e01, 1.040000e-01],
            [1.744300e01, 2.922210e02, 9.695600e01],
            [1.730500e01, 3.115090e02, 9.600500e01],
            [6.991400e01, 1.037475e03, 4.530560e02],
            [6.948400e01, 1.035609e03, 4.490460e02],
            [6.926300e01, 8.990650e02, 4.485530e02],
            [6.957100e01, 8.992150e02, 4.508830e02],
            [4.207000e00, 4.482650e02, 2.662400e01],
        ]
    )

    test = rptfile.link_pollutant_load_summary

    assert allclose(reference, test)


def test_analysis_begun_and_end(rptfile):
    assert type(rptfile.analysis_begun) == Timestamp
    assert type(rptfile.analysis_end) == Timestamp
