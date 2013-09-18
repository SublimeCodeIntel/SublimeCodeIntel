##############################################################################
# Copyright (c) 2007 Zope Foundation and Contributors.
# All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
##############################################################################
"""Cached Methods
"""

class cachedIn(object):
    """Cached method with given cache attribute."""

    def __init__(self, attribute_name, factory=dict):
        self.attribute_name = attribute_name
        self.factory = factory

    def __call__(self, func):

        def decorated(instance, *args, **kwargs):
            cache = self.cache(instance)
            key = self._get_cache_key(*args, **kwargs)
            try:
                v = cache[key]
            except KeyError:
                v = cache[key] = func(instance, *args, **kwargs)
            return v

        decorated.invalidate = self.invalidate
        return decorated

    def invalidate(self, instance, *args, **kwargs):
        cache = self.cache(instance)
        key = self._get_cache_key(*args, **kwargs)
        try:
            del cache[key]
        except KeyError:
            pass

    def cache(self, instance):
        try:
            cache = getattr(instance, self.attribute_name)
        except AttributeError:
            cache = self.factory()
            setattr(instance, self.attribute_name, cache)
        return cache

    @staticmethod
    def _get_cache_key(*args, **kwargs):
        kw = kwargs.items()
        key = (args, tuple(sorted(kw)))
        return key
