#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .__about__ import __version__


from datetime import datetime, timezone
from pgark.mylog import mylogger


def current_time() -> datetime:
    return datetime.now(tz=timezone.utc)
