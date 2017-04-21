#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the imposter cell metric.

A cell is received on different ARFCNs (frequencies) within a short time.

Rationale:

    To avoid leaving traces of a new, non-existent cell, an IMSI
    catcher may choose to reuse the cell ID and LAC of an existing
    cell in an area, but using a different frequency. The IMSI
    catcher must have a location area different from the current
    serving cell, such that the MS performs a location update once
    it close enough. The use of the cell ID on different frequencies
    may be detected by the analysis if system information of the
    original cell was received earlier.

False Positives:

    A cell may be reconfigured to use a different frequency, but this
    should happen very rarely.

Example:

    A simple example would be a single two identical CID and LAC pairs
    advertising different ARFCNs.

    * Good Cell
        * LAC 1
        * CID 7
        * ARFCN 42
    * Evil Cell
        * LAC 1
        * CID 7
        * ARFCN 1337

    The evil cell is pretending to be in the location area code to
    not trigger a lonely LAC metric, and to not leave a trace of a
    strange cell wandering all over town.

Reference:

    SnoopSnitch Metrics:
        https://opensource.srlabs.de/projects/snoopsnitch/wiki/IMSI_Catcher_Score#A4-Same-LACCID-on-different-ARFCNs

"""
import os
import sqlite3

import pytest

from antikythera.metrics import Metrics

__author__ = "Team Awesome"
__copyright__ = "Team Awesome"
__license__ = "GPLv3+"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, 'test.sqlite3')


@pytest.yield_fixture(autouse=True)
def run_around_tests():
    """This fixture will be run code before and after every test.

    Before each test create the database and the ``LAC_CID`` table
    for the test data. Then run the tests, and after each test is
    completed delete the test database ensuring a new empty databse
    for each test.

    """
    # Code that will run before test
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS LAC_CID(
        KEY TEXT PRIMARY KEY,
        LAC TEXT,
        CID TEXT,
        ARFCN TEXT
        )''')
    conn.commit()
    conn.close()

    # A test function will be run at this point
    yield

    # Code that will run after test
    os.remove(DB_FILE)


def test_imposter_cell_simple():
    """Test that imposter cell is detected.

    Simple case from the example in the module docstring. Same
    LAC, same CID, but different ARFCNs is an imposter.

    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    key = 0
    lacs = [1, 1]
    cids = [7, 7]
    arfcns = [42, 1337]

    for lac, cid, arfcn in zip(lacs, cids, arfcns):
        cursor.execute(
            """INSERT INTO LAC_CID(
                KEY,
                LAC,
                CID,
                ARFCN
            ) VALUES (?, ?, ?, ?)
            """, (
                key,
                lac,
                cid,
                arfcn
            )
        )
        key += 1

    conn.commit()
    conn.close()

    metrics = Metrics('test')
    metrics.data_dir = DB_FILE
    assert metrics.imposter_cell()


def test_imposter_cell_many():
    """Test that imposter cell is detected.

    Mutliple entries of good cells, and five entries of a single
    evil cell.

    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    key = 0

    # Multiple copies of good cell
    lacs = [1] * 5
    cids = [7] * 5
    arfcns = [42] * 5

    # Multiple copies of evil cell
    lacs += [1] * 5
    cids += [7] * 5
    arfcns += [1337] * 5

    # Some random cells
    lacs += [1] * 20
    cids += range(20, 40)
    arfcns += range(20, 40)

    # A few in the different LAC
    lacs += [2] * 5
    cids += [7, 7, 8, 9, 10]
    arfcns += range(50, 55)

    for lac, cid, arfcn in zip(lacs, cids, arfcns):
        cursor.execute(
            """INSERT INTO LAC_CID(
                KEY,
                LAC,
                CID,
                ARFCN
            ) VALUES (?, ?, ?, ?)
            """, (
                key,
                lac,
                cid,
                arfcn
            )
        )
        key += 1

    conn.commit()
    conn.close()

    metrics = Metrics('test')
    metrics.data_dir = DB_FILE
    assert metrics.imposter_cell()


def test_imposter_cell_two():
    """Test that imposter cell is detected.

    Test two evil cells.

    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    key = 0

    # Multiple copies of good cell
    lacs = [1] * 5
    cids = [7] * 5
    arfcns = [42] * 5

    # Multiple copies of evil cell
    lacs += [1] * 5
    cids += [7] * 5
    arfcns += [1337] * 5

    # Second Good Cell
    lacs += [1] * 5
    cids += [42] * 5
    arfcns += [4444] * 5

    # Second Evil Cell
    lacs += [1] * 5
    cids += [42] * 5
    arfcns += [8888] * 5

    for lac, cid, arfcn in zip(lacs, cids, arfcns):
        cursor.execute(
            """INSERT INTO LAC_CID(
                KEY,
                LAC,
                CID,
                ARFCN
            ) VALUES (?, ?, ?, ?)
            """, (
                key,
                lac,
                cid,
                arfcn
            )
        )
        key += 1

    conn.commit()
    conn.close()

    metrics = Metrics('test')
    metrics.data_dir = DB_FILE
    assert metrics.imposter_cell()


def test_not_imposter_same_cell():
    """Test that same cell brodcasts are not detected.

    Same LAC, same CID, same ARFCN is just the same cell.

    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    key = 0
    lacs = [1, 1]
    cids = [7, 7]
    arfcns = [42, 42]

    for lac, cid, arfcn in zip(lacs, cids, arfcns):
        cursor.execute(
            """INSERT INTO LAC_CID(
                KEY,
                LAC,
                CID,
                ARFCN
            ) VALUES (?, ?, ?, ?)
            """, (
                key,
                lac,
                cid,
                arfcn
            )
        )
        key += 1

    conn.commit()
    conn.close()

    metrics = Metrics('test')
    metrics.data_dir = DB_FILE
    assert not metrics.imposter_cell()


def test_not_imposter_different_cell():
    """Test that different cell broadcasts are not detected.

    All cells on different frequencies are not imposters.

    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    key = 0
    lacs = [1, 1, 1, 2]
    cids = [7, 8, 9, 10]
    arfcns = [42, 43, 44, 45]

    for lac, cid, arfcn in zip(lacs, cids, arfcns):
        cursor.execute(
            """INSERT INTO LAC_CID(
                KEY,
                LAC,
                CID,
                ARFCN
            ) VALUES (?, ?, ?, ?)
            """, (
                key,
                lac,
                cid,
                arfcn
            )
        )
        key += 1

    conn.commit()
    conn.close()

    metrics = Metrics('test')
    metrics.data_dir = DB_FILE
    assert not metrics.imposter_cell()


def test_not_imposter_same_freq():
    """Test that same cell brodcasts are not detected.

    Same ARFCN, different LAC.

    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    key = 0
    lacs = [1, 2]
    cids = [7, 20]
    arfcns = [42, 42]

    for lac, cid, arfcn in zip(lacs, cids, arfcns):
        cursor.execute(
            """INSERT INTO LAC_CID(
                KEY,
                LAC,
                CID,
                ARFCN
            ) VALUES (?, ?, ?, ?)
            """, (
                key,
                lac,
                cid,
                arfcn
            )
        )
        key += 1

    conn.commit()
    conn.close()

    metrics = Metrics('test')
    metrics.data_dir = DB_FILE
    assert not metrics.imposter_cell()
