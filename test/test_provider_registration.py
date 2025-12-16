import pytest
from src.providers import register_provider, Provider
from src.errors import ValidationError

def test_register_provider_success():
    provider = register_provider(
        name="Royal Event Hall",
        capacity=200,
        price=1500000,
        location="Central UB"
    )
    assert isinstance(provider, Provider)
    assert provider.name == "Royal Event Hall"
    assert provider.capacity == 200
    assert provider.price == 1500000


def test_register_provider_invalid_capacity():
    # Changed from ValueError to ValidationError
    with pytest.raises(ValidationError):
        register_provider(
            name="Test Hall",
            capacity="two hundred",
            price=500000,
            location="UB"
        )
