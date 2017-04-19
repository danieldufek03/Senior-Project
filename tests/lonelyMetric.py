import sqlite3
conn = sqlite3.connect('myData.db')
c = conn.cursor()
queryList = []
lonelyList = []

c.execute("DROP TABLE PACKETS")

c.execute('''CREATE TABLE IF NOT EXISTS PACKETS(
    IMSI TEXT PRIMARY KEY,
    LAC TEXT,
    CID TEXT
    )''')

c.execute(
    """INSERT INTO PACKETS(
        IMSI,
        LAC,
        CID
    ) VALUES (?, ?, ?)
    """, (
        '12378',
        '100100',
        '122',
    )
)

c.execute(
    """INSERT INTO PACKETS(
        IMSI,
        LAC,
        CID
    ) VALUES (?, ?, ?)
    """, (
        '456',
        '100100',
        '122',
    )
)

c.execute(
    """INSERT INTO PACKETS(
        IMSI,
        LAC,
        CID
    ) VALUES (?, ?, ?)
    """, (
        '789',
        '100100',
        '132',
    )
)

c.execute(
    """INSERT INTO PACKETS(
        IMSI,
        LAC,
        CID
    ) VALUES (?, ?, ?)
    """, (
        '132',
        '100100',
        '132',
    )
)

c.execute(
    """INSERT INTO PACKETS(
        IMSI,
        LAC,
        CID
    ) VALUES (?, ?, ?)
    """, (
        '143',
        '100100',
        '1337',
    )
)

c.execute(
    """INSERT INTO PACKETS(
        IMSI,
        LAC,
        CID
    ) VALUES (?, ?, ?)
    """, (
        '154',
        '100100',
        '1337',
    )
)
conn.commit()
c.execute("SELECT DISTINCT LAC FROM PACKETS")
for row in c.fetchall():
    queryList.append(row)
for LAC in queryList:
    c.execute("""SELECT *
    FROM (
    SELECT LAC, CID
    FROM PACKETS
    WHERE PACKETS.LAC = ?
    )
    GROUP BY CID
    HAVING COUNT(CID) = 1""", LAC)
for row in c.fetchall():
    print("LONELY LIST CONTENT: ", row)
    lonelyList.append(row)
sizeOflonelyList = len(lonelyList)
print("SIZE of lonelyList: ", sizeOflonelyList)
conn.close()
