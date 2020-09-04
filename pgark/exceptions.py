#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Custom exceptions (copied from pastpages/savepagenow)
"""


class CachedPage(Exception):
    """
    This error is raised when archive.org declines to make a new capture
    and instead returns the cached version of most recent archive.
    """
    pass





class SaveJobError(Exception):
    pass



class WaybackRuntimeError(Exception):
    """
    An error returned by the Wayback Machine.
    """
    pass


class WaybackRobotsError(WaybackRuntimeError):
    """
    This error is raised when archive.org has been blocked by the site's robots.txt access control instructions.
    """
    pass

class WaybackSubmitError(WaybackRuntimeError):
    pass
