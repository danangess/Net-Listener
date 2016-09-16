#!/usr/bin/env python

import os
import sys
import socket
import fcntl
import struct
# import re

try:
    import ConfigParser
except ImportError:
    import configparser as ConfigParser
parser = ConfigParser.ConfigParser()

import time
import signal
import threading
import subprocess
from subprocess import call
import gi
from gi.repository import GObject
from dbus.mainloop.glib import DBusGMainLoop

class Net():
    def __init__(self):
        pass
        # self.rx_bytes = {}
        # self.tx_bytes = {}
        # for inf in self.get_interfaces():
        #     (self.rx_bytes[inf], self.tx_bytes[inf]) = self.get_network_bytes(inf)

    def get_interface_connected(self):
        ifaces = self.get_interfaces_connected()
        for ifname in ifaces:
            if self.is_interface_connected(ifname):
                return ifname

        return False

    def get_interfaces_connected(self):
        ifaces = self.get_interfaces()
        connected = []
        for ifname in ifaces:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                socket.inet_ntoa(fcntl.ioctl(
                        s.fileno(),
                        0x8915,  # SIOCGIFADDR
                        struct.pack('256s', ifname[:15])
                )[20:24])
                connected.append(ifname)
                # print "%s is connected" % ifname
            except:
                pass
                # print "%s is not connected" % ifname
        return connected

    def get_local_address(self):
        ips = []
        for ip in subprocess.check_output("/sbin/ip address | grep -i 'inet ' | awk {'print $2'} | sed -e 's/\/[^\/]*$//'", shell=True).split("\n"):
            if len(ip.split('.')) == 4:
                ips.append(ip)

        return ips

    def get_local(self):
        ip = []
        # ip.append(socket.gethostbyname(socket.gethostname()))
        ip.append('127.0.0.1')
        ip.append('127.0.1.1')
        return ip


    def get_interfaces(self):
        return os.listdir('/sys/class/net/')

    def is_interface_connected(self, interface):
        if self.get_interface_address(interface) in self.get_local():
            return False

        (rx_bytes, tx_bytes) = self.get_network_bytes(interface)
        # timeout = time.time() + 7
        # while time.time() < timeout:
        #     (re_rx_bytes, re_tx_bytes) = self.get_network_bytes(interface)
        #     if rx_bytes < re_rx_bytes or tx_bytes < re_tx_bytes:
        #         return True
        time.sleep(1)
        if self.get_network_bytes(interface):
            (re_rx_bytes, re_tx_bytes) = self.get_network_bytes(interface)
            if rx_bytes < re_rx_bytes or tx_bytes < re_tx_bytes:
                return True
            else:
                self.test_connection()
                (re_rx_bytes, re_tx_bytes) = self.get_network_bytes(interface)
                if rx_bytes < re_rx_bytes or tx_bytes < re_tx_bytes:
                    return True

        return False

    def is_connected(self):
        iface = self.get_interface_connected()
        if iface and self.get_interface_address(iface) not in self.get_local():
            return iface
        else:
            return False

    def test_connection(self):
        sites = ['www.bing.com', 'www.google.com']
        try:
            for site in sites:
                # see if we can resolve the host name -- tells us if there is
                # a DNS listening
                host = socket.gethostbyname(site)
                # connect to the host -- tells us if the host is actually
                # reachable
                if host not in self.get_local_address():
                    s = socket.create_connection((host, 80), 2)

            return True
        except:
            pass

        return False

    # def get_interface_connected(self):
    #     # signal.signal(signal.SIGINT, signal.SIG_DFL)
    #     DBusGMainLoop(set_as_default=True)
    #     GObject.idle_add(self.get_interface_connected, priority=999)
    #     mainloop = GObject.MainLoop()
    #     interface = self.get_interfaces()
    #     for inf in interface:
    #         if self.is_interface_connected(inf):
    #             mainloop.quit()
    #             return inf
    #     mainloop.run()
    #     return False

    def get_interface_address(self, interface):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', interface[:15])
        )[20:24])

    # def get_network_bytes(self, interface):
    #     output = subprocess.Popen(['ifconfig', interface], stdout=subprocess.PIPE).communicate()[0]
    #     rx_bytes = re.findall('RX bytes:([0-9]*) ', output)[0]
    #     tx_bytes = re.findall('TX bytes:([0-9]*) ', output)[0]
    #     return (rx_bytes, tx_bytes)

    def get_network_bytes(self, interface):
        for line in open('/proc/net/dev', 'r'):
            if interface in line:
                data = line.split('%s:' % interface)[1].split()
                rx_bytes, tx_bytes = (data[0], data[8])
                return (rx_bytes, tx_bytes)


class Exec():
    def bing_desktop_wallpaper_changer(self):
        print "[executing] python /opt/bing-desktop-wallpaper-changer/main.py"
        call(["python", "/opt/bing-desktop-wallpaper-changer/main.py"])
        # os.system("python /opt/bing-desktop-wallpaper-changer/main.py")

    def link_bing_walpaper_today(self):
        lines = [line.rstrip('\n') for line in open('/home/danang/Pictures/BingWallpapers/image-details.txt')]
        txt = []
        for ln in lines:
            txt = ln.split()
        link = "/home/danang/Pictures/bing-walpapaer-today.jpg"
        target = "/home/danang/Pictures/BingWallpapers/"
        target += txt[0]
        if os.path.exists(link):
            os.unlink(link)
            os.symlink(target, link)
        # string = 'ln -s '+'"'+target+'"'+' '+'"'+link+'"'
        # os.system(string)

    def custom(self):
        pass


class Main():
    def __init__(self):
        self.connected = False

    def main(self):
        thread = threading.Timer(1, self.main)
        # thread.start()
        # global connected
        m = Net()
        connect = m.is_connected()
        if not self.connected and connect:
            print "Connecting via", connect
            self.connected = True
            # thread.cancel()
            run = Exec()
            run.bing_desktop_wallpaper_changer()
            run.link_bing_walpaper_today()
        elif not connect:
            print "Not Connected"
            self.connected = False
        else:
            print "Connected via", connect
        thread.start()

# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    main = Main()
    main.main()
