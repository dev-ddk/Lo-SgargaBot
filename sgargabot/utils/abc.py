class Singleton(type):
    """Singleton metaclass

    A metaclass implementing the Singleton pattern, allowing only one instance with type `type` to exist.
    """

    _instances: dict[type, object] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
