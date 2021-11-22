import pytest
import numpy as np


@pytest.fixture()
def bounding_box():
    return np.array([[0.,0.], [10.,0.], [0.,10.], [10.,10.]])