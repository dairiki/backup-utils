# -*- coding: utf-8 -*-
#
# Copyright (c) 2014 Geoffrey T. Dairiki <dairiki@dairiki.org>
# All rights reserved.
#
""" Rules for determining which backups to keep
"""
from __future__ import absolute_import

from collections import namedtuple, defaultdict
from datetime import datetime, time, timedelta
from itertools import chain

Backup = namedtuple('Backup', ['time', 'filename'])

NOW = datetime.now()

class Rule(object):
    def __init__(self, duration, now=NOW):
        if not isinstance(duration, timedelta):
            raise TypeError("'duration' must be a timedelta")
        self.duration = duration
        self.now = now
        self.min_time = now - duration

    def keepers(self, backups):
        """ Return the backups kept by this rule.
        """
        raise NotImplementedError()     # pragma: NO COVER

class KeepAll(Rule):
    def keepers(self, backups):
        for backup in backups:
            if backup.time >= self.min_time:
                yield backup

class BinnedRule(Rule):
    def keepers(self, backups):
        bybin = defaultdict(list)
        for backup in backups:
            bin_, delta = self.find_bin(backup)
            if bin_ >= self.min_time:
                bybin[bin_].append((abs(delta), backup))
        for binned in bybin.values():
            delta, backup = min(binned)
            yield backup

    def find_bin(self, backup):
        dt = backup.time
        dt0 = self.floor(dt)
        dt1 = self.ceil(dt)
        assert dt0 <= dt <= dt1
        delta0 = dt - dt0
        delta1 = dt1 - dt
        return (dt1, delta1) if delta1 < delta0 else (dt0, delta0)

    def floor(self, dt):
        raise NotImplementedError()     # pragma: NO COVER

    def ceil(self, dt):
        raise NotImplementedError()     # pragma: NO COVER


class KeepDaily(BinnedRule):
    def floor(self, dt):
        return datetime.combine(dt.date(), time(0))

    def ceil(self, dt):
        return datetime.combine(dt.date() + timedelta(days=1), time(0))

class KeepWeekly(BinnedRule):
    isoweekday = 6                 # Saturday

    def floor(self, dt):
        d = dt.date()
        d -= timedelta(days=(d.isoweekday() - self.isoweekday) % 7)
        assert d.isoweekday() == self.isoweekday
        return datetime.combine(d, time(0))

    def ceil(self, dt):
        d = dt.date()
        d += timedelta(days=7 - (d.isoweekday() - self.isoweekday) % 7)
        assert d.isoweekday() == self.isoweekday
        return datetime.combine(d, time(0))


class KeepMonthly(BinnedRule):
    def floor(self, dt):
        return datetime(dt.year, dt.month, 1, 0, 0)

    def ceil(self, dt):
        if dt.month == 12:
            return datetime(dt.year + 1, 1, 1, 0, 0)
        else:
            return datetime(dt.year, dt.month + 1, 1, 0, 0)

class KeepYearly(BinnedRule):
    def floor(self, dt):
        return datetime(dt.year, 1, 1, 0, 0)

    def ceil(self, dt):
        return datetime(dt.year + 1, 1, 1, 0, 0)

RULES = [
    KeepAll(timedelta(days=1)),
    KeepDaily(timedelta(days=3)),
    KeepWeekly(timedelta(days=32)),
    KeepMonthly(timedelta(days=365)),
    KeepYearly(timedelta(days=5 * 365)),
    ]

def keepers(backups, rules=RULES):
    return set(chain.from_iterable(rule.keepers(backups) for rule in rules))
