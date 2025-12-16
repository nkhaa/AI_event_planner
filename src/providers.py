import sqlite3
from src.db import DB_PATH
from src.errors import ValidationError


class Provider:
    def __init__(
        self,
        name,
        capacity,
        price,
        packages=None,
        image_url=None,
        available_dates=None,
        location=None
    ):
        self.name = name
        self.capacity = capacity
        self.price = price
        self.packages = packages
        self.image_url = image_url
        self.available_dates = available_dates
        self.location = location


def register_provider(
    name,
    capacity,
    price,
    location,
    packages=None,
    image_url=None,
    available_dates=None
):
    if not isinstance(name, str) or not name.strip():
        raise ValidationError("Provider name must be a non-empty string")
    if not isinstance(capacity, int):
        raise ValidationError("Capacity must be an integer")
    if not isinstance(price, int):
        raise ValidationError("Price must be an integer")
    if not isinstance(location, str) or not location.strip():
        raise ValidationError("Location must be a non-empty string")

    return Provider(
        name=name.strip(),
        capacity=capacity,
        price=price,
        packages=packages,
        image_url=image_url,
        available_dates=available_dates,
        location=location.strip()
    )


# Alias for API usage
create_provider = register_provider


def save_provider(provider: Provider):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO providers
        (name, capacity, price, packages, image_url, available_dates, location)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            provider.name,
            provider.capacity,
            provider.price,
            provider.packages,
            provider.image_url,
            provider.available_dates,
            provider.location
        )
    )

    conn.commit()
    conn.close()
