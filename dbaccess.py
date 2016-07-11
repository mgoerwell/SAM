import web
import common


def test_database():
    result = 0;
    try:
        rows = common.db.query("SELECT * FROM Syslog LIMIT 1;")
    except Exception as e:
        result = e[0]
        # see http://dev.mysql.com/doc/refman/5.7/en/error-messages-server.html for codes
        # if e[0] == 1049:  # Unknown database 'samapper'
        #     Common.create_database()
        #     return self.GET(name)
        # elif e[0] == 1045:  # Access Denied for '%s'@'%s' (using password: (YES|NO))
        #     rows = [e[1], "Check you username / password? (dbconfig_local.py)"]
    return result

def create_database():
    connection = web.database(
        dbn='mysql',
        user=common.dbconfig.params['user'],
        pw=common.dbconfig.params['passwd'],
        port=common.dbconfig.params['port'])

    connection.query("CREATE DATABASE IF NOT EXISTS samapper;")
    connection.query("USE samapper;")
    connection.query("DROP TABLE IF EXISTS Links;")
    connection.query("DROP TABLE IF EXISTS Nodes;")
    connection.query("DROP TABLE IF EXISTS Syslog;")
    connection.query("""
        CREATE TABLE Syslog (
            entry INT UNSIGNED NOT NULL AUTO_INCREMENT,
            SourceIP INT UNSIGNED NOT NULL,
            SourcePort INT NOT NULL,
            DestinationIP INT UNSIGNED NOT NULL,
            DestinationPort INT NOT NULL,
            Occurances INT DEFAULT 1 NOT NULL,
            CONSTRAINT PKSyslog PRIMARY KEY (entry))
            ;""")
    connection.query("""
        CREATE TABLE Nodes (
            IPAddress INT UNSIGNED NOT NULL,
            CONSTRAINT PKNodes PRIMARY KEY (IPAddress))
            ;""")
    connection.query("""
        CREATE TABLE Links (
            SourceIP INT UNSIGNED NOT NULL,
            DestinationIP INT UNSIGNED NOT NULL,
            DestinationPort INT NOT NULL,
            CONSTRAINT PKLinks PRIMARY KEY (SourceIP, DestinationIP, DestinationPort),
            CONSTRAINT FKSrc FOREIGN KEY (SourceIP) REFERENCES Nodes (IPAddress),
            CONSTRAINT FKDest FOREIGN KEY (DestinationIP) REFERENCES Nodes (IPAddress))
            ;""")

def determineRange(ip1 = -1, ip2 = -1, ip3 = -1):
    min = 0x00000000;
    max = 0xFFFFFFFF;
    quot = 1;
    if ip1 != 0 and ip1 < 255 and ip1 > 0:
        min = (ip1 << 24)   # 172.0.0.0
        if ip2 != 0 and ip2 < 255 and ip2 > 0:
            min |= (ip2 << 16)  # 172.19.0.0
            if ip3 != 0 and ip3 < 255 and ip3 > 0:
                min |= (ip3 << 8)
                max = min | 0xFF
                quot = 0x1
            else:
                max = min | 0xFFFF
                quot = 0x100
        else:
            max = min | 0xFFFFFF
            quot = 0x10000
    else:
        quot = 0x1000000
    return (min, max, quot)


def connections(subnet=8):
    denominator = 2**(32-subnet);
    rows = common.db.query("""
    SELECT SourceIP DIV 16777215 AS 'Source', DestinationIP DIV 16777215 AS 'Destination', COUNT(*) AS 'Occurrences'
        FROM Syslog
        GROUP BY Source, Destination
        ORDER BY Occurrences ASC;""")
    return rows


def getNodes(ipSegment1 = -1, ipSegment2 = -1, ipSegment3 = -1):
    range = determineRange(ipSegment1, ipSegment2, ipSegment3);

    # test with 172.21.47

    vars = dict(min=range[0], max=range[1], quot=range[2])

    rows = common.db.query("""
    SELECT (ip - $min) DIV $quot AS 'address', COUNT(*) AS 'count'
        FROM (
            (SELECT SourceIP AS ip
            FROM Syslog)
            UNION ALL
            (SELECT DestinationIP AS ip
            FROM Syslog)
        ) as result
        WHERE ip >= $min
            AND ip <= $max
        GROUP BY address;""", vars=vars)
    return rows
