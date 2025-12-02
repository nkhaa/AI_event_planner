import pytest
from src.sum import niilber

def test_sum_invalid_type():
    with pytest.raises(TypeError):
        niilber("a", 5)
