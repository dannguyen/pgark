#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Custom exceptions (copied from pastpages/savepagenow)
"""


class TodoError(Exception):
    """raise this when I'm doing something I haven't implemented yet!"""

    pass


class ServerStatusError(Exception):
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


### todo: these should only have Wayback scope??
class SubmissionError(Exception):
    pass


class AbnormalSubmitResponse(SubmissionError):
    pass


class SaveJobError(SubmissionError):
    pass


# class _CachedPage(Exception):
#     """
#     holdover from savepagenow:
#     This error is raised when archive.org declines to make a new capture
#     and instead returns the cached version of most recent archive.
#     """

#     pass
