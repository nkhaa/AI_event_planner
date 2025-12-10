from src.errors import ValidationError, AppError
from src.logger import logger

class Provider:
    def __init__(self, name, capacity, price, location):

        if not isinstance(name, str) or not name.strip():
            logger.error("Invalid provider name")
            raise ValidationError("Provider name must be a non-empty string")

        if not isinstance(capacity, int):
            logger.error(f"Invalid capacity: {capacity}")
            raise ValidationError("Capacity must be an integer")

        if not isinstance(price, int):
            logger.error(f"Invalid price: {price}")
            raise ValidationError("Price must be an integer")

        if not isinstance(location, str) or not location.strip():
            logger.error("Invalid location")
            raise ValidationError("Location cannot be empty")

        self.name = name
        self.capacity = capacity
        self.price = price
        self.location = location


def register_provider(name, capacity, price, location):
    try:
        provider = Provider(name, capacity, price, location)
        logger.info(f"Provider registered: {name}")
        return provider
    except ValidationError as e:
        logger.error(f"Registration failed: {e.message}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise AppError("Unexpected provider registration error") from e
