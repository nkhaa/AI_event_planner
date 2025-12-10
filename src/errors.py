class AppError(Exception):

    def __init__(self, message, details=None):
        super().__init__(message)
        self.message = message
        self.details = details


class ValidationError(AppError):
    pass


class NotFoundError(AppError):
    pass
