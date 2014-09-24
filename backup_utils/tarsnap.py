# -*- coding: utf-8 -*-
#
# Copyright (c) 2014 Geoffrey T. Dairiki <dairiki@dairiki.org>
# All rights reserved.
#
"""
"""
from __future__ import absolute_import

from datetime import datetime
import re
from subprocess import check_call, Popen, PIPE

from .rules import keepers, Backup

ARCHIVE_re = re.compile(r'''
    (?P<filename> .+)
    \t
    (?P<year> \d{4}) - (?P<month> \d\d) - (?P<day> \d\d)
    [\ T]
    (?P<hour> \d\d) : (?P<minute> \d\d) : (?P<second> \d\d)
    \s* \Z
''', re.X)

def _parse_archive(line):
    m = re.match(ARCHIVE_re, line)
    if not m:
        raise ValueError(
            "Can not parse output from tarsnap --list-archives:\n  %r",
            line.rstrip())
    filename = m.group('filename')
    timeparts = dict(
        (part, int(m.group(part) or 0))
        for part in ('year', 'month', 'day', 'hour', 'minute', 'second'))
    return Backup(datetime(**timeparts), filename)

def list_archives():
    p = Popen(['tarsnap', '--list-archives', '-v'], stdout=PIPE)
    archives = sorted(_parse_archive(line) for line in p.stdout)
    if p.wait() != 0:
        raise RuntimeError(
            "tarsnap --list-archives command failed with return code %s",
            p.returncode)
    return archives

def run(cmd):
    print(' '.join(cmd))
    check_call(cmd)

def tarsnap_clean():
    backups = set(list_archives())
    stale = backups - keepers(backups)

    if stale:
        cmd = ['tarsnap', '-d']
        for backup in sorted(stale):
            cmd.extend(['-f', backup.filename])
        run(cmd)
