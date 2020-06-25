import threading
import time
from collections import MutableMapping

from cachetools import TTLCache

from autottlcache.monitor import CacheMonitor


class AutoTTLCache(MutableMapping):

    def __init__(self, items=None, *, maxsize, ttl, timer=time.monotonic, getsizeof=None):
        self._cache_lock = threading.Lock()
        self._cache = TTLCache(maxsize, ttl, timer=timer, getsizeof=getsizeof)
        if items is not None:
            self._cache.update(items)
        self._monitor = CacheMonitor(self)

    @property
    def ttl(self):
        with self._cache_lock:
            return self._cache.ttl

    @property
    def maxsize(self):
        with self._cache_lock:
            return self._cache.maxsize

    @property
    def timer(self):
        with self._cache_lock:
            return self._cache.timer

    def expire(self):
        with self._cache_lock:
            self._cache.expire()

    def __contains__(self, key):
        with self._cache_lock:
            return key in self._cache

    def __setitem__(self, k, v):
        with self._cache_lock:
            self._cache[k] = v

    def __delitem__(self, k):
        with self._cache_lock:
            del self._cache[k]

    def __getitem__(self, k):
        with self._cache_lock:
            return self._cache[k]

    def __len__(self) -> int:
        with self._cache_lock:
            return len(self._cache)

    def __iter__(self):
        with self._cache_lock:
            keys = list(self._cache)
        yield from keys

    # TODO: __reduce__ and __setstate__

    def __repr__(self):
        return f"{type(self).__name__}(max_size={self.maxsize}, ttl={self.ttl})"

    def clear(self):
        with self._cache_lock:
            self._cache.clear()

    def get(self, *args, **kwargs):
        with self._cache_lock:
            self._cache.get(*args, **kwargs)

    def pop(self, *args, **kwargs):
        with self._cache_lock:
            self._cache.pop(*args, **kwargs)

    def setdefault(self, *args, **kwargs):
        with self._cache_lock:
            self._cache.setdefault(*args, **kwargs)

    def popitem(self):
        with self._cache_lock:
            self._cache.popitem()
