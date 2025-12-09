

class Provider:
    def __init__(self, name: str, capacity: int, price: int, location: str):
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Provider name must be a non-empty string.")

        if not isinstance(capacity, int):
            raise ValueError("Capacity must be an integer.")

        if not isinstance(price, int):
            raise ValueError("Price must be an integer.")

        if not isinstance(location, str) or not location.strip():
            raise ValueError("Location must be a non-empty string.")

        self.name = name
        self.capacity = capacity
        self.price = price
        self.location = location


def register_provider(name: str, capacity: int, price: int, location: str) -> Provider:

    return Provider(name=name, capacity=capacity, price=price, location=location)
