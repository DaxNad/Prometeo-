class AtlasError(Exception):
    pass


class AdapterNotAvailable(AtlasError):
    pass


class SolveFailed(AtlasError):
    pass

