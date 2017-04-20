#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test Inconsistent LAC metric.

The LAC of the current base station differs from the LAC of many
neighboring cells.

Rationale:

    A mobile will only perform a normal location update when changing
    to a different area, i.e. a base station with a different LAC. An
    IMSI catcher needs to force a location update to be able to interact
    with the phone and derive the desired information. Therefore, it
    must span a cell with a LAC different to all neighboring cells,
    but with a much better signal strength than the other cells. For
    an IMSI catcher announcing realistic neighboring cells, this
    difference between the LAC of the serving cell and all neighboring
    cell can be detected.

False Positives:

    Femto cells may or may not announce a LAC different from all
    their neighboring cells. Their may be other special situations,
    like in-house cells where this is the case.

Example:

    A simple example would be a LAC being the only observed LAC.

    * Evil IMSI Catcher Reports:
        * CID 1337
        * LAC 13
    * All neighboring cells reported by Evil IMSI Catcher are:
        * LAC 7

    The evil cell is pretending to be in the location area code to
    not trigger a lonely LAC metric, and to not leave a trace of a
    strange cell wandering all over town.

    The information must be obtained form the Evil Cells reporting
    of neighboring cells.

Acronyms:

    IMSI: International Subscriber Identity
    LAC: Location Area Code
    CID: Cell Identification Code
    N-CELL-LAC: Neighboring Cell Location Area Code

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


@pytest.yield_fixture(autouse=True)
def run_around_tests():
    """This fixture will be run code before and after every test.

    Before each test create the database and the ``PACKETS`` table
    for the test data. Then run the tests, and after each test is
    completed delete the test database ensuring a new empty databse
    for each test.

    """
    # Code that will run before test
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS PACKETS(
        KEY TEXT PRIMARY KEY,
        LAC TEXT,
        CID TEXT,
        N_CELL_LAC TEXT
        )''')
    conn.commit()
    conn.close()

    # A test function will be run at this point
    yield

    # Code that will run after test
    os.remove("test.db")


def test_inconsistent_lac_simple():
    """Test that imposter cell is detected.

    Simple case from the example in the module docstring.

    """
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()

    key = 0

    good_lacs = [1] * 5
    good_cids = range(1, 5)
    n_cell_lacs = [1] * 5
    for lac, cid, n_cell_lac in zip(good_lacs, good_cids, n_cell_lacs):
        cursor.execute(
            """INSERT INTO PACKETS(
                KEY,
                LAC,
                CID,
                N_CELL_LAC
            ) VALUES (?, ?, ?, ?)
            """, (
                key,
                lac,
                cid,
                n_cell_lac
            )
        )
        key += 1

    evil_lac = [13] * 5
    evil_cid = [1337] * 5
    n_cell_lacs = [1] * 5
    for evil_lac, evil_cid, n_cell_lac in zip(evil_lac, evil_cid, n_cell_lacs):
        cursor.execute(
            """INSERT INTO PACKETS(
                KEY,
                LAC,
                CID,
                N_CELL_LAC
            ) VALUES (?, ?, ?, ?)
            """, (
                key,
                evil_lac,
                evil_cid,
                n_cell_lac
            )
        )
        key += 1

    conn.commit()
    conn.close()

    metrics = Metrics('test')
    metrics.data_dir = 'test.db'
    assert metrics.inconsistent_lac()


def test_not_inconsistent_lac_simple():
    """Test that imposter cell is detected.

    Simple case from the example in the module docstring.

    """
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()

    key = 0

    good_lacs = [1] * 5
    good_cids = range(1, 5)
    n_cell_lacs = [1] * 5
    for lac, cid, n_cell_lac in zip(good_lacs, good_cids, n_cell_lacs):
        cursor.execute(
            """INSERT INTO PACKETS(
                KEY,
                LAC,
                CID,
                N_CELL_LAC
            ) VALUES (?, ?, ?, ?)
            """, (
                key,
                lac,
                cid,
                n_cell_lac
            )
        )
        key += 1

    conn.commit()
    conn.close()

    metrics = Metrics('test')
    metrics.data_dir = 'test.db'
    assert not metrics.inconsistent_lac()
