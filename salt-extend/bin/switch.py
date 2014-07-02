import re
import commands
import socket
import struct

def getSwitch():
    def is_private(ip):
        f = struct.unpack('!I',socket.inet_pton(socket.AF_INET,ip))[0]
        private = (
            [ 2130706432, 4278190080 ], # 127.0.0.0,   255.0.0.0   http://tools.ietf.org/html/rfc3330
            [ 3232235520, 4294901760 ], # 192.168.0.0, 255.255.0.0 http://tools.ietf.org/html/rfc1918
            [ 2886729728, 4293918720 ], # 172.16.0.0,  255.240.0.0 http://tools.ietf.org/html/rfc1918
            [ 167772160,  4278190080 ], # 10.0.0.0,    255.0.0.0   http://tools.ietf.org/html/rfc1918
        )
        for net in private:
            if (f & net[1] == net[0]):
                return True
        return False

    data = commands.getoutput("ip addr show | awk '/inet /{print $2,$4}'").split('\n')
    bcast = []
    for ip in data:
        if not re.match(r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$', ip.split("/")[0]):
            continue
        if not is_private(ip.split("/")[0]):
            bcast.append(ip.split()[1])

    switchlist = []
    for brd in bcast:
        result = commands.getoutput('ping -b -c2 %s | grep "icmp_seq"' % brd)
        switch = re.findall(r'\d+.\d+.\d+.\d+',result)
        switchlist += list(set(switch))

    return {"switch": switchlist}



