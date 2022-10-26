"""Tests for `swmm-pandas` input class."""


import os
from datetime import datetime

import numpy as np
import pandas as pd
import pytest

from swmm.pandas import Input, test_inp_path


# @pytest.fixture(scope="module")
def inpfile():

    inp = Input(test_inp_path)
    return inp

if __name__ == "__main__":
    inp = inpfile()
    
    