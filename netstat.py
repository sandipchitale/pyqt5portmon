import subprocess
from random import betavariate


def split_string_at_ranges(string, ranges):
    """Splits a string at specified column ranges.

    Args:
        string: The string to split.
        ranges: A list of tuples, where each tuple represents a start and end index (inclusive) for a column range.

    Returns:
        A tuple of substrings.
    """
    result = []
    for start, end in ranges:
        result.append(string[start:end].strip())

    return tuple(result)

"""
Linux:
                                                                                                    1
          1         2         3         4         5         6         7         8         9         0
01234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name   
"""
class NetstatRecord:
    NETSTAT_COLUMN_RANGES = ((0, 5), (20, 43), (44, 67), (68, 79), (80, 120))
    def __init__(self, protocol, localAddress, localPort, foreignAddress, foreignPort, state, pid):
        self.protocol = protocol
        self.localAddress = localAddress
        self.localPort = localPort
        self.foreignAddress = foreignAddress
        # self.foreignPort = "" if foreignPort == "*" else foreignPort
        self.foreignPort = foreignPort
        self.state = state
        self.pid = "-" if pid == "-" else pid.split("/")[0]

    def __str__(self):
        return f"{self.localAddress} {self.localPort} {self.foreignAddress} {self.foreignPort} {self.state} {self.pid}"

    def __repr__(self):
        return self.__str__()

class Netstat:

    def __init__(self):
        pass

    def netstat(self):
        netstatRecords = []

        # Run a command and capture its output
        try:
            result = subprocess.run(["netstat", "-anpt46"], capture_output=True, text=True)
            if result.returncode == 0:
                netstatLines = result.stdout.splitlines(False)

                for netstatLine in netstatLines[2:]:  # skip the first two lines
                    netstatColumns = split_string_at_ranges(netstatLine, NetstatRecord.NETSTAT_COLUMN_RANGES)
                    netstatRecords.append(NetstatRecord(
                        netstatColumns[0],                    # protocol
                        netstatColumns[1].split(":")[0],      # local address only
                        int(netstatColumns[1].split(":")[1]), # local port
                        netstatColumns[2].split(":")[0],      # foreign address only
                        netstatColumns[2].split(":")[1],      # foreign port
                        netstatColumns[3],                    # state
                        netstatColumns[4]))                   # raw pid
                return netstatRecords
            else:
                raise ChildProcessError(f"Exit code: {result.exitCode} Error: {result.stdout}")
        except BaseException as be:
            raise be
def main():
    netstat = Netstat()
    try:
        netstatRecords = netstat.netstat()
        for netstatRecord in netstatRecords:
            print(netstatRecord)
    except ChildProcessError as cpe:
        print(cpe)
    except BaseException as be:
        print(be)

if __name__ == '__main__':
    main()