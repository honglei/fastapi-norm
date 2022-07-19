'''
    
'''
import netifaces
import socket

def get_interface_by_ip(ip:str):
    '''
       get the name of network interface with <ip> address,
       return None is the <ip> is not the ip of this platform.
       
       根据IP地址获取对应的接口，
       耗时Win7 0.07秒  Deepin/SW 0.001秒 
    '''
    for iface in netifaces.interfaces():
        allAddrs = netifaces.ifaddresses(iface)        
        if addrs:= allAddrs.get(socket.AF_INET):
            for addr in addrs:
                if addr['addr'] == ip:
                    return iface


if __name__ =="__main__":
    import time
    beg = time.time()
    iface = get_interface_by_ip(ip='10.65.39.191')
    print(f"{iface=}  {time.time()-beg}")