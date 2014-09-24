# -*- coding: utf-8 -*-
"""
"""
from __future__ import absolute_import

from datetime import datetime
from subprocess import PIPE

import pytest

def test_parse_archive():
    from backup_utils.tarsnap import _parse_archive
    backup = _parse_archive('foo bar\t2014-07-04 12:34:56\n')
    assert backup.time == datetime(2014, 7, 4, 12, 34, 56)
    assert backup.filename == 'foo bar'

def test_parse_archive_failure():
    from backup_utils.tarsnap import _parse_archive
    with pytest.raises(ValueError):
        _parse_archive('\t2014-07-04 12:34:56\n')

def test_list_archives(monkeypatch):
    from backup_utils import tarsnap

    popen = MockPopen(stdout=[
        'foo bar2\t2014-07-04 12:34:57\n',
        'foo bar1\t2014-07-04 12:34:56\n',
        ])
    monkeypatch.setattr(tarsnap, 'Popen', popen)

    assert tarsnap.list_archives() == [
        tarsnap.Backup(datetime(2014, 7, 4, 12, 34, 56), 'foo bar1'),
        tarsnap.Backup(datetime(2014, 7, 4, 12, 34, 57), 'foo bar2'),
        ]
    assert popen.calls == [
        ((['tarsnap', '--list-archives', '-v'],), {'stdout': PIPE}),
        ]

def test_list_archives_failure(monkeypatch):
    from backup_utils import tarsnap

    popen = MockPopen(returncode=1)
    monkeypatch.setattr(tarsnap, 'Popen', popen)
    with pytest.raises(RuntimeError):
        tarsnap.list_archives()

def test_run(monkeypatch, capsys):
    from backup_utils import tarsnap

    commands = []
    def check_call(cmds):
        commands.append(cmds)
    monkeypatch.setattr(tarsnap, 'check_call', check_call)

    tarsnap.run(['a', 'b'])

    out, err = capsys.readouterr()
    assert out == 'a b\n'
    assert commands == [
        ['a', 'b'],
        ]

def test_tarsnap_clean(monkeypatch):
    from backup_utils import tarsnap

    def list_archives():
        return [
            tarsnap.Backup(datetime(2014, 7, 4, 12, 34, 56), 'foo bar1'),
            tarsnap.Backup(datetime(2014, 7, 4, 12, 34, 57), 'foo bar2'),
            ]

    def keepers(backups):
        return set([sorted(backups)[-1]])

    commands = []
    def run(cmd):
        commands.append(cmd)

    monkeypatch.setattr(tarsnap, 'list_archives', list_archives)
    monkeypatch.setattr(tarsnap, 'keepers', keepers)
    monkeypatch.setattr(tarsnap, 'run', run)

    tarsnap.tarsnap_clean()

    assert commands == [
        ['tarsnap', '-d', '-f', 'foo bar1'],
        ]


class MockPopen(object):
    def __init__(self, stdout=[], returncode=0):
        self.stdout = stdout
        self.returncode = returncode
        self.calls = []

    def __call__(self, *args, **kw):
        self.calls.append((args, kw))
        return self

    def wait(self):
        return self.returncode
