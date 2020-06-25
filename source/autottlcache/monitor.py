import sched
import threading
import time
import weakref
import logging


logger = logging.getLogger(__name__)


MONITOR_POLLING_INTERVAL_SECONDS = 1.0


class CacheMonitor:

    _lock = threading.Lock()
    _instance: weakref.ReferenceType = None

    def __new__(cls, cache):
        with cls._lock:
            if cls._instance is not None:
                instance = cls._instance()
                if instance is not None:
                    return instance

            logger.debug("Instantiating CacheMonitor")
            instance = object.__new__(cls)
            instance._scheduler = sched.scheduler()
            instance._is_cancelled = threading.Event()
            instance._thread = threading.Thread(
                target=_run,
                name="Cache monitoring",
                kwargs=dict(
                    scheduler=instance._scheduler,
                    is_cancelled=instance._is_cancelled
                )
            )
            cls._instance = weakref.ref(instance)
            instance._thread.start()
            while not instance._thread.is_alive():
                logger.debug("Waiting for monitoring thread to start")
                pass
            logger.debug("Attaching CacheMonitor finalizer")
            weakref.finalize(instance, _finalize_cache_monitor, instance._is_cancelled)
            return instance

    def __init__(self, cache):
        cache_ref = weakref.ref(cache)
        self._schedule_next(cache_ref, now=time.monotonic())

    def _schedule_next(self, cache_ref, now):
        cache = cache_ref()
        if cache is not None:
            scheduled_time = now + (cache.ttl / 10)
            self._scheduler.enterabs(scheduled_time, priority=0, action=self._expire, kwargs=dict(
                cache_ref=cache_ref, now=scheduled_time
            ))

    def _expire(self, cache_ref, now):
        cache = cache_ref()
        if cache is not None:
            self._schedule_next(cache_ref, now)
            logger.debug("Expiring cache %r" % cache)
            cache.expire()


def _run(scheduler, is_cancelled):
    logger.debug("Cache monitoring thread started")
    while not is_cancelled.is_set():
        deadline = scheduler.run(blocking=False)
        tick = MONITOR_POLLING_INTERVAL_SECONDS if (deadline is None) else min(deadline, MONITOR_POLLING_INTERVAL_SECONDS)
        logger.debug("Cache monitoring thread sleeping for %s seconds", tick)
        time.sleep(tick)
    logger.debug("Cache monitoring thread ending")


def _finalize_cache_monitor(is_cancelled):
    is_cancelled.set()
    logger.debug("Cancelled cache monitoring thread")