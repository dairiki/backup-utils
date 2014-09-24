# -*- coding: utf-8 -*-
#
# Copyright (c) 2014 Geoffrey T. Dairiki <dairiki@dairiki.org>
# All rights reserved.
#
"""
"""
from __future__ import absolute_import

from datetime import datetime, timedelta
from operator import attrgetter

import pytest


def make_backup(dt):
    from backup_utils.rules import Backup
    return Backup(dt, dt.isoformat('T'))

def date_range(start, end, step=timedelta(days=1)):
    dt = start
    while dt < end:
        yield dt
        dt += step

@pytest.fixture
def now():
    return datetime(2014, 7, 4, 12, 43)

@pytest.fixture
def daily_backups(now):
    return [ make_backup(dt)
             for dt in date_range(datetime(2012, 6, 1, 8, 0), now) ]

@pytest.fixture
def hourly_backups(now):
    return [ make_backup(dt)
             for dt in date_range(datetime(2014, 6, 1, 8, 0), now,
                                  timedelta(hours=1)) ]

def test_Rule_raises_type_error():
    from backup_utils.rules import Rule
    with pytest.raises(TypeError):
        Rule(duration=42)

def test_KeepAll(hourly_backups, now):
    from backup_utils.rules import KeepAll
    duration = timedelta(hours=3)
    rule = KeepAll(duration=duration, now=now)
    keepers = sorted(rule.keepers(hourly_backups))
    assert list(map(attrgetter('filename'), keepers)) == [
        '2014-07-04T10:00:00',
        '2014-07-04T11:00:00',
        '2014-07-04T12:00:00',
        ]

def test_KeepDaily(daily_backups, now):
    from backup_utils.rules import KeepDaily
    duration = timedelta(days=3)
    rule = KeepDaily(duration=duration, now=now)
    keepers = sorted(rule.keepers(daily_backups))
    assert list(map(attrgetter('filename'), keepers)) == [
        '2014-07-02T08:00:00',
        '2014-07-03T08:00:00',
        '2014-07-04T08:00:00',
        ]

def test_KeepWeekly(daily_backups, now):
    from backup_utils.rules import KeepWeekly
    duration = timedelta(days=21)
    rule = KeepWeekly(duration=duration, now=now)
    keepers = sorted(rule.keepers(daily_backups))
    assert list(map(attrgetter('filename'), keepers)) == [
        '2014-06-14T08:00:00',
        '2014-06-21T08:00:00',
        '2014-06-28T08:00:00',
        '2014-07-04T08:00:00',
        ]

def test_KeepMonthly(daily_backups, now):
    from backup_utils.rules import KeepMonthly
    duration = timedelta(days=3 * 31)
    rule = KeepMonthly(duration=duration, now=now)
    keepers = sorted(rule.keepers(daily_backups))
    assert list(map(attrgetter('filename'), keepers)) == [
        '2014-05-01T08:00:00',
        '2014-06-01T08:00:00',
        '2014-07-01T08:00:00',
        ]

def test_KeepYearly(daily_backups, now):
    from backup_utils.rules import KeepYearly
    duration = timedelta(days=3 * 365)
    rule = KeepYearly(duration=duration, now=now)
    keepers = sorted(rule.keepers(daily_backups))
    assert list(map(attrgetter('filename'), keepers)) == [
        '2012-06-01T08:00:00',
        '2013-01-01T08:00:00',
        '2014-01-01T08:00:00',
        '2014-07-04T08:00:00',
        ]

def test_keepers():
    from backup_utils.rules import keepers

    rules = [
        MockRule(['keeper']),
        ]

    assert keepers([], rules) == set(['keeper'])

class MockRule(object):
    def __init__(self, keepers):
        self._keepers = keepers

    def keepers(self, backups):
        return self._keepers
