# autottlcache

A time-to-live (TTL) cache dictionary with auto-expiry.

# Installation

To install from PyPI:

    $ pip install autottlcache
  
  
# Usage


The TTL cache behaves very much like a dictionary. In fact, it is a `MutableMapping` so supports the
dictionary interface. It has one important difference though, which is that the items within it will
expire and automatically be removed.

Let's create an `AutoTTLCache` with a a maximum size of twelve entires, and a TTL of 30 seconds:

    >>> from autottlcache import AutoTTLCache
    >>> cache = AutoTTLCache(maxsize=12, ttl=30.0)
    
We can add entries to the cache:

    >>> cache[1] = 56
    >>> cache[2] = 89
    >>> cache[3] = 99
    >>> cache[4] = 10
    >>> cache[5] = 20

And watch them expire, by repeatedly asking the cache to list its keys:

    >>> list(cache.keys())
    [2, 3, 4, 5]
    
We took long enough adding the keys that the first one had already expired:
    
    >>> list(cache.keys())
    [3, 4, 5]
    
Now the second one has gone too:
    
    >>> list(cache.keys())
    [3, 4, 5]
    
This time we're quick enough to get in before the third one expires:
 
    >>> list(cache.keys())
    [3, 4, 5]
    >>> list(cache.keys())
    [3, 4, 5]
    >>> list(cache.keys())
    [3, 4, 5]
    >>> list(cache.keys())
    [4, 5]
    >>> list(cache.keys())
    [4, 5]
    >>> list(cache.keys())
    [4, 5]
    >>> list(cache.keys())
    [5]
    >>> list(cache.keys())
    [5]
    >>> list(cache.keys())
    [5]
    >>> list(cache.keys())
    [5]
    >>> list(cache.keys())
    [5]
    >>> list(cache.keys())
    []
    
All gone.

Stale items are removed from the cache either when an operation on the cache object is invoked, such
as when an item is retrieved, or by a continuously running background thread that periodically
removes expired items. The cache will be checked with a frequency of ten times the TTL period, so
an item in a cache with a TTL of 30 seconds should live no longer than 33 seconds.

## Programming style

Owing to the fact that items will auto-expire, to avoid race conditions you should strongly prefer
an _Easier to Ask for Forgiveness than Permission_ (EAFP) programming style, rather than a _Look
Before You Leap_ (LBYL) style.

Risky race-condition:

    from autottlcache import AutoTTLCache
    cache = AutoTTLCache(maxsize=100, ttl=30)
    cache["daffodils"] = Image("daffodils-3280x2040.png")
    
    # ...
    
    if "daffodils" in cache:
        # What happens if "daffodils" expires here?
        image = cache["daffodils"]  # This could raise a key error which is unhandled
    else:
        print("No flowers for you!")
        
        
Better to use a single operation to retrieve an object, and handle the failure:

    from autottlcache import AutoTTLCache
    cache = AutoTTLCache(maxsize=100, ttl=30)
    cache["daffodils"] = Image("daffodils-3280x2040.png")
    
    # ...
    
    try:
        image = cache["daffodils"]
    except KeyError:
        print("No flowers for you!")
    else:
        display(image)
        
        
## Resource use

A single additional thread will be running during any periods for which one or more `AutoTTLCache`
objects are extant. The thread will start when the first `AutoTTLCache` is created, and will
terminate shortly after the last `AutoTTLCache` is finalized.


# Development

To release, there is a short manual process:

    $ bumpversion patch
    $ python setup.py sdist bdist_wheel
    $ twine upload dist/* --config-file=path/to/sixty-north.pypirc
  