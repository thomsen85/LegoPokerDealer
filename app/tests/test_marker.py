import numpy as np

from app.content.markers import Marker


def test_center_point(bounding_box):
    marker = Marker(1, 0, bounding_box)
    expected = np.array([5.0, 5.0])
    np.testing.assert_allclose(marker.center_point, expected)
    
    
def test_normalized_directional_vector(bounding_box):
    marker = Marker(1, 0, bounding_box)
    expected = np.array([0., -1.])
    
    np.testing.assert_allclose(marker.normalized_directional_vector, expected)