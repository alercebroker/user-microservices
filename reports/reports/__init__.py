import importlib.metadata

try:  # pragma: no cover
    __version__ = importlib.metadata.version(__package__)
except importlib.metadata.PackageNotFoundError:  # pragma: no cover
    __version__ = "dev"
