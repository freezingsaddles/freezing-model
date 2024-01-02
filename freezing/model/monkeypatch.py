import sys


def collections():
    """
    Monkeypatch collections to get Alembic to work

    The alembic package is throwing errors because some aliases in collections
    were removed in Python 3.10.

    Adapted from MIT licensed code at:
        https://github.com/healthvana/h2/commit/d67c6ca10eb7f79c0737c37fdecfe651307a7414
    Thanks to:
        https://github.com/jazzband/django-push-notifications/issues/622#issuecomment-1234497703
    """
    if sys.version_info.major >= 3 and sys.version_info.minor >= 10:
        import collections
        from collections import abc

        collections.Iterable = abc.Iterable
        collections.Mapping = abc.Mapping
        collections.MutableSet = abc.MutableSet
        collections.MutableMapping = abc.MutableMapping
