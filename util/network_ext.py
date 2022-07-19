# -*- coding:utf-8 -*-
# Copyright (c) 2014-2017 Jiang Honglei <jhonglei@qq.com>

'''
   关于网络方面的功能扩展
'''

import socket
import os
import ipaddress    
          
def get_localIPAddr2Dst(dstIP):
    '''
       获取本机中与Dst通讯的IP地址。
       假定：dstIP与 localIPAddr 在同一个网段
       实现方式：
            在Win下使用wmi实现，在Linux使用pyroute2实现;
            获取本机的所有IP地址和掩码，组成IPv4Network,如果匹配，则返回对应的本机IP地址。
    '''
    if "nt" == os.name:
        return _win32_get_ipAddr2CMU(dstIP)
    elif "posix"==os.name:
        return _posix_get_ipAddr2CMU(dstIP)

import re
ipv4_re = re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
import ipaddress
def _win32_get_ipAddr2CMU(cmuIP):
    '''
    '''
    import wmi
    c = wmi.WMI()
    for link in c.Win32_NetworkAdapterConfiguration(IPEnabled=1):
        for index,ip   in enumerate(link.IPAddress):
            if ipv4_re.match(ip):
                mask = link.IPSubnet[index]
                ip_network = ipaddress.IPv4Network("{0}/{1}".format(ip, mask), strict=False)
                if ipaddress.IPv4Address(cmuIP) in ip_network:
                    return ip
    return None

def _posix_get_ipAddr2CMU(cmuIP):
    '''
         get the NCP's IP Addr that used to conncet to CMU.
         Assume cmuIPAddr and NCP's IP Addr in the same IPv4Network.
        '''    
    from pyroute2.iproute import IPRoute
    ip = IPRoute()
    for item in ip.get_addr():
        if socket.AF_INET.value == item['family']:
            attrs = dict(item['attrs'])
            ip_addr = attrs['IFA_ADDRESS']
            ip_mask = item['prefixlen']
            #print(ip_addr, ip_mask)
            ip_net = ipaddress.IPv4Network("{ip_addr}/{ip_mask}".format(**locals()),strict=False)
            if ipaddress.IPv4Address(cmuIP) in ip_net:
                return ip_addr
    return None    

#### neifaces在Server2008下所获取的掩码错误
#import netifaces
#for link in netifaces.interfaces():
    #addrs = netifaces.ifaddresses( link )
    #ip_addrs = addrs.get(netifaces.AF_INET)  
    #if None == ip_addrs:
        #continue
    #print (ip_addrs)
    #for item in ip_addrs:
        #ipaddress.IPv4Address( "{addr}/{netmask}")

### 以下方式不能
#import fcntl 
#import struct        
#hostname=socket.gethostname()
#ips = socket.gethostbyname(hostname)
#s = socket.socket( socket.AF_INET, socket.SOCK_DGRAM, )
#socket.inet_ntoa( fcntl.ioctl( s.fileno() , 
                               #0x8915, #SIOGIFADDR
                               #struct.pack('256s', b"enp9s0f0" ) 
                               #)[20:24] )    

import os
if 'posix' == os.name:
    from pyroute2.iproute import IPRoute
    
def _posix_is_local_ip(ipAddr):
    '''
        check whether ipAddr is a local ip
    '''    
    ip = IPRoute()
    for item in ip.get_addr():
        if socket.AF_INET.value == item['family']:
            attrs = dict(item['attrs'])
            ip_addr = attrs['IFA_ADDRESS']
            if ipAddr == ip_addr:
                return True
    return False
def _win32_is_local_ip(ipAddr):
    for ip_pack in socket.gethostbyname_ex(socket.gethostname()):
        if type(ip_pack) ==list and ipAddr in ip_pack:
            return True
    return False

def is_local_ip(ipAddr):
    if ipAddr in ("localhost","127.0.0.1","::1"):
        return True    
    if 'nt'  == os.name:    
        return _win32_is_local_ip(ipAddr)
    elif 'posix' == os.name:
        return _posix_is_local_ip(ipAddr)

def get_local_ip_list():
    '''
      get the ip list of local host.
    获取本机的IP地址列表
    '''
    local_ip_list =[]
    if 'nt'  == os.name:    
        for ip_pack in socket.gethostbyname_ex(socket.gethostname()):
            if type(ip_pack) ==list:
                local_ip_list+=ip_pack
    elif 'posix' == os.name:
        ip = IPRoute()
        for item in ip.get_addr():
            if socket.AF_INET.value == item['family']:
                attrs = dict(item['attrs'])
                ip_addr = attrs['IFA_ADDRESS']
                #ip_mask = item['prefixlen']
                local_ip_list.append(ip_addr)
    return local_ip_list

if __name__ == "__main__":
    ipAddr="10.65.39.201"
    result = is_local_ip(ipAddr)
    print (f"{ipAddr=} {result=}")
    ip = get_localIPAddr2Dst(dstIP="10.65.39.141")
    print(get_local_ip_list() )