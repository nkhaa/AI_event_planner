class Provider:
    def __init__(self, name, capacity, price, location):
        self.name = name
        self.capacity = capacity
        self.price = price
        self.location = location


def register_provider(name, capacity, price, location):
    if not all([name, location]):
        raise ValueError("Нэр болон байршил хоосон байж болохгүй.")

    if not isinstance(capacity, int) or capacity <= 0:
        raise ValueError("Хүчин чадал эерэг тоо байх ёстой.")

    if not isinstance(price, int) or price <= 0:
        raise ValueError("Үнэ эерэг тоо байх ёстой.")

    return Provider(name, capacity, price, location)

