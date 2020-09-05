#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .__about__ import __version__


from datetime import datetime, timezone


def get_today() -> datetime:
    return datetime.now(tz=timezone.utc)
