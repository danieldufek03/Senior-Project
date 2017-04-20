#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the lonely location area code metric.

A cell is the only cell observed in its location area.

Rationale:

    A mobile will only perform a normal location update when changing
    to a different area, i.e. a base station with a different LAC. An
    IMSI catcher needs to force a location update to be able to interact
    with the phone and derive the desired information. Therefore, it
    must span a cell with a LAC different to all neighboring cells,
    but with a much better signal strength than the other cells. An
    IMSI catcher creating a new LAC for its fake cell will be the
    only cell operating in this location area. The lack of system
    information for other cells of this location area can be detected.

False Positives:

    When traveling at high speeds or in areas with poor coverage the
    mobile may record system information for only a single cell of
    location area.

    "Unexpected neighbors also do happen often with subway cells. In
    some cases the BTS is in a central place, and the RF heads are far
    away, connected with optical fiber. In these cases cell IDs and
    LACs are carried over many kilometers into places where they
    usually do not belong, and often not all neighbors are set
    correctly, due to restrictions in neighbor list size. I can
    imagine that such circumstances could trigger a false positive."

Example:

    A simple example would be a group or two of cells sharing a LAC
    and another LAC detected with only a single CID belonging to it.

    * LAC 1 contains CIDs: 1, 2, 3
    * LAC 2 contains CIDs: 4, 5, 6, 6, 8
    * LAC 3 contains CIDs: 9

    Here LAC 3, containing only a single CID is suspicious.

Reference:

    SnoopSnitch Metrics:
        https://opensource.srlabs.de/projects/snoopsnitch/wiki/IMSI_Catcher_Score#A5-Lonesome-location-area
    SRLabs: https://lists.srlabs.de/pipermail/gsmmap/2015-March/001272.html

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

    Before each test create the database and the ``SYSTEM`` table
    for the test data. Then run the tests, and after each test is
    completed delete the test database ensuring a new empty databse
    for each test.

    """
    # Code that will run before test
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS SYSTEM(
        KEY TEXT PRIMARY KEY,
        LAC TEXT,
        CID TEXT
        )''')
    conn.commit()
    conn.close()

    # A test function will be run at this point
    yield

    # Code that will run after test
    os.remove(DB_FILE)


def test_lonely_lac():
    """Test that lonely LAC is not detected on single LAC.

    Builds The Table:

        +-----+-----+-------+
        | KEY | LAC |  CID  |
        +=====+=====+=======+
        |  0  |  1  |  122  |
        +-----+-----+-------+
        |  1  |  1  |  122  |
        +-----+-----+-------+
        |  2  |  1  |  132  |
        +-----+-----+-------+
        |  3  |  1  |  132  |
        +-----+-----+-------+
        |  4  |  2  |  1337 |
        +-----+-----+-------+
        |  5  |  2  |  1337 |
        +-----+-----+-------+

    This is to test that a LAC with two entries of the same CID
    still triggers the metric. Here LAC 2 only has a single CID
    1337 in it, but it has been detected multiple times.

    ==========  ==========
    LAC 1 CIDs LAC 2 CIDs
    ==========  ==========
    122        1337
    132
    ==========  ==========

    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    key = 0
    lacs = [1, 1, 1, 1, 2, 2]
    cids = [122, 122, 132, 132, 1337, 1337]

    for lac, cid in zip(lacs, cids):
        cursor.execute(
            """INSERT INTO SYSTEM(
                KEY,
                LAC,
                CID
            ) VALUES (?, ?, ?)
            """, (
                key,
                lac,
                cid,
            )
        )
        key += 1

    conn.commit()
    conn.close()

    metrics = Metrics('test')
    metrics.data_dir = DB_FILE
    assert metrics.lonely_cell_id()


def test_not_lonely_lac():
    """Test that lonely LAC is not detected on single LAC.

    Builds The Table:

        +-----+-----+-------+
        | KEY | LAC |  CID  |
        +=====+=====+=======+
        |  0  |  1  |  122  |
        +-----+-----+-------+
        |  1  |  1  |  122  |
        +-----+-----+-------+
        |  2  |  1  |  132  |
        +-----+-----+-------+
        |  3  |  1  |  132  |
        +-----+-----+-------+
        |  4  |  1  |  1337 |
        +-----+-----+-------+
        |  5  |  1  |  1337 |
        +-----+-----+-------+

    Only a single LAC with 3 CIDs in it.

    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    key = 0
    lacs = [1, 1, 1, 1, 1, 1]
    cids = [122, 122, 132, 132, 1337, 1337]

    for lac, cid in zip(lacs, cids):
        cursor.execute(
            """INSERT INTO SYSTEM(
                KEY,
                LAC,
                CID
            ) VALUES (?, ?, ?)
            """, (
                key,
                lac,
                cid,
            )
        )
        key += 1

    conn.commit()
    conn.close()

    metrics = Metrics('test')
    metrics.data_dir = DB_FILE
    assert not metrics.lonely_cell_id()


def test_lonely_lac_simple():
    """Test that lonely location area codes are detected.

    The example from the module docstring.

    Builds The Table:

        +-----+-----+-------+
        | KEY | LAC |  CID  |
        +=====+=====+=======+
        |  0  |  1  |   1   |
        +-----+-----+-------+
        |  1  |  1  |   2   |
        +-----+-----+-------+
        |  2  |  1  |   3   |
        +-----+-----+-------+
        |  3  |  2  |   4   |
        +-----+-----+-------+
        |  4  |  2  |   5   |
        +-----+-----+-------+
        |  5  |  2  |   6   |
        +-----+-----+-------+
        |  6  |  2  |   7   |
        +-----+-----+-------+
        |  7  |  2  |   8   |
        +-----+-----+-------+
        |  8  |  3  |   9   |
        +-----+-----+-------+

    LAC 3 only has a single CID belonging to it which should
    trigger the metric.

    ==========  ==========  ==========
    LAC 1 CIDs LAC 2 CIDs  LAC 3 CIDs
    ==========  ==========  ==========
    1          4            9
    2          5
    3          6
               7
               8
    ==========  ==========  ==========

    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    key = 0

    lac_one = 1
    lac_one_cids = ['1', '2', '3']
    for cid in lac_one_cids:
        cursor.execute(
            """INSERT INTO SYSTEM(
                KEY,
                LAC,
                CID
            ) VALUES (?, ?, ?)
            """, (
                key,
                lac_one,
                cid,
            )
        )
        key += 1

    lac_two = 2
    lac_two_cids = ['4', '5', '6', '7', '8']
    for cid in lac_two_cids:
        cursor.execute(
            """INSERT INTO SYSTEM(
                KEY,
                LAC,
                CID
            ) VALUES (?, ?, ?)
            """, (
                key,
                lac_two,
                cid,
            )
        )
        key += 1

    evil_lac = 3
    evil_cids = ['9']
    for cid in evil_cids:
        cursor.execute(
            """INSERT INTO SYSTEM(
                KEY,
                LAC,
                CID
            ) VALUES (?, ?, ?)
            """, (
                key,
                evil_lac,
                cid,
            )
        )
        key += 1

    conn.commit()
    conn.close()

    metrics = Metrics('test')
    metrics.data_dir = DB_FILE
    assert metrics.lonely_cell_id()
