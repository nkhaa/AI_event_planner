def niilber(a, b):
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError("Тоо оруулах шаардлагатай!")
    return a + b
