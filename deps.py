

import os
if os.name=='nt':
    os.add_dll_directory(os.path.dirname(__file__))
from random import randint
import ipaddress
import typing

import pynorm    
from pynorm.constants import EventType,NackingMode



#from util.netifaces_ext import get_interface_by_ip
def create_sender_session(instance:pynorm.Instance, 
                          destAddr:str,
                          destPort:int, 
                          localAddr:str|None=None, 
                          localPort:int=0,                            
                          iface:str|None=None, # the interface of <localAddr>
                          srcAddr:str|None=None, #usef for setSSM
                          sessionIndex:typing.Hashable=None,
                          ccEnable:bool = True,
                          rateMin:float|None=-1,
                          rateMax:float|None=-1,
                          txRate:float|None =None,
                          bufferSpace:int = 100*1024*1024,
                          segmentSize:int = 1400,
                          blockSize:int = 128,
                          numParity:int = 0,
                          loopbackEnable:bool = False
                          
                          ) -> pynorm.session.Session:

    session = instance.createSession(destAddr, destPort,  localId=ipaddress.IPv4Address(localAddr)._ip, index=sessionIndex  )
    if localAddr or localPort:
        session.setTxPort(localPort,txBindAddr=localAddr) #
    if iface:
        session.setMulticastInterface(iface)
    if srcAddr:
        session.setSSM(srcAddr=srcAddr)    
    session.setTxOnly(txOnly=True) 
    if txRate:
        session.setTxRate(txRate*1000)
    session.setCongestionControl(ccEnable=True) # 
    if loopbackEnable:
        session.setLoopback(True)
    if rateMin>=0 or rateMax>=0:
        session.setTxRateBounds(rateMin=rateMin*1000,rateMax=rateMax*1000)

    sessionID = randint(0, 1000)
    success:bool = session.startSender(sessionID, bufferSpace, segmentSize=segmentSize, blockSize=blockSize, numParity=numParity ) 
    print (f"startSender:{success}")
    session.setGroupSize(4)
    return session 


def create_recver_session(instance:pynorm.Instance, multiAddr:str, port:int, 
                                localAddr:str, 
                                iface:str=None, # the interface of <localAddr>, 
                                srcAddr:str=None, #SSM的源地址
                                sessionIndex:typing.Hashable=None,
                          defaultUnicastNack:bool = True,
                          silentReceiver:bool = False, # 静默终端 
                          bufferSpace:int = 50*1024*1024,
                          loopbackEnable:bool =False,
                          ):
    '''
       iface : only used for Linux, Win10 does not need it.
    '''

    
    session:pynorm.session.Session = instance.createSession(multiAddr, port, localId=ipaddress.IPv4Address(localAddr)._ip, index=sessionIndex)
    if iface and os.name=='posix':
        session.setMulticastInterface(iface)
    
    session.setTxPort(port, enableReuse=True, txBindAddr=localAddr )  #"10.65.39.223" #NACK包都使用此处配置的IP地址和端口 
    session.setRxPortReuse(enable=True,rxBindAddr=multiAddr) # 收包根据不同组播地址区分Session
    
    #must called before startSender or startReceiver
    if srcAddr:
        session.setSSM(srcAddr=srcAddr) #必须在启动Sende或Receiver之前调用

    session.setSilentReceiver(silent=silentReceiver)
    session.setDefaultUnicastNack(enable=defaultUnicastNack) # 以单播的形式进行响应  
    session.setDefaultNackingMode(mode=NackingMode.NORMAL)
    
    if loopbackEnable:
        session.setLoopback(True)
        
    session.startReceiver(bufferSpace=bufferSpace)
    return session

def get_instance():
    return instance


import asyncio
def get_task():
    return task

task:asyncio.Task|None = None

if os.name=='nt':
    import win32api
    import win32event
import traceback

   
instance:pynorm.Instance = pynorm.Instance()
from pynorm.constants import EventType,ObjectType

from config import settings

import atexit

@atexit.register
def shutdown2():
    global instance
    instance.destroy()
    #loop = asyncio.get_event_loop()
    #loop.run_until_complete(stop_all_processes())   
    

async def proc_sender_event(event:pynorm.event.Event):
    '''
        处理接收端事件
    '''
    objType:ObjectType = event.object.type
    if event.type == EventType.TX_OBJECT_SENT:
        pass
    elif event.type == EventType.TX_WATERMARK_COMPLETED:
        if objType:
            event.session.id2obj.pop(event.object._object)
        #if ObjectType.FILE == objType:
            #file_path = event.object.info.decode()
            #print (f"{file_path} WATERMARK_COMPLETED ")
    elif event.type == EventType.TX_OBJECT_PURGED:
        # 参见 NormSetTxCacheBounds 说明 
        if objType:
            event.session.id2obj.pop(event.object._object)        
            
        
        
async def proc_receiver_event(event:pynorm.event.Event):
    '''
        处理发送端事件 
    '''
    print(event.type)
    objType:ObjectType = event.object.type
    if event.type == EventType.RX_OBJECT_INFO:
        
        if objType == ObjectType.FILE:
            session:pynorm.session.Session = event.session
            
            session.id2obj[event.object.handle] = event.object
            
            print('Downloading file %s' % event.object.filename)

    elif event.type == EventType.RX_OBJECT_UPDATED:
        '''
            TODO：用于计算对象的大小
        '''
        pass
        

    elif event.type == EventType.RX_OBJECT_COMPLETED:
        '''
            对象接收完成
        '''        
        if ObjectType.DATA == objType:
            
            print (f"{event.session.name} len:{len(event.object.getData()) }")
            
        elif ObjectType.FILE == objType:
            file_path = event.object.info.decode()
            fileName = os.path.split(file_path)[-1]

            path = os.path.join(settings.recvFileDir, fileName )
            oldPath = event.object.filename

            print (f"{oldPath=}")
            try:
                if os.path.isfile(path):
                    os.remove(path)
                os.rename(src=oldPath, dst=path)
            except Exception as e:
                print ( traceback.format_exc() )                        
            print('File %s completed' % event.object.filename)
            
        #event.session.id2obj.pop(event.object.handle)
            
    elif event.type == EventType.RX_OBJECT_ABORTED:
        
        if ObjectType.FILE == objType:
            filePath = event.object.filename
            event.object.cancel()
            #remove temparary file if recv aborted.
            os.remove(filePath) #移除 临时文件 
            print('File %s aborted' % filePath)
        #event.session.id2obj.pop(event.object.handle)
    
    
import typing
import pynorm
import select
from pynorm import DebugLevel as NormDebugLevel
async def watch_norm_events(proc_event: typing.Callable[[pynorm.event.Event],None ], timeout:int=1):
    global instance
    instance.setDebugLevel(level=NormDebugLevel.ALWAYS) #2 Warning 3 INFO 4 DEBUG

    handle = instance.getDescriptor()
    while True:
        try:
            if os.name =='nt':
                value:int = await asyncio.to_thread(win32event.WaitForSingleObject, handle,100)
                if value == win32event.WAIT_TIMEOUT:
                    await asyncio.sleep(0)
                    continue
                elif value == win32event.WAIT_FAILED:
                    print ( f"error:{win32api.GetLastError()}" )
                elif value == win32event.WAIT_ABANDONED:
                    pass 
                elif value == win32event.WAIT_OBJECT_0:       
                    event: pynorm.event.Event = instance.getNextEvent( )
                    await proc_event(event)
                    print(event) 
            else:
                readable, writable, exceptional = await asyncio.to_thread(select.select, [handle],[],[handle]) 
                if readable:
                    event: pynorm.event.Event = instance.getNextEvent( )
                    await proc_event(event)                
                    
        except Exception as e:
            print ( traceback.format_exc() )
    print("watch_norm_events finished" )
    return 0


def init_server():
    global task
    task = asyncio.create_task( watch_norm_events( proc_sender_event) )
    
def init_receiver():
    '''
        设置接收路径 
    '''
    global task,instance
    recvPath:str = os.path.expanduser( settings.recvFileDir  ) 
    instance.setCacheDirectory( recvPath )
    task = asyncio.create_task( watch_norm_events( proc_receiver_event) )    


async def main():
    global instance
    
    print("start:")
    task: asyncio.Task = asyncio.create_task( watch_norm_events() )
    
    session:pynorm.session.Session = create_sender_session(instance, destAddr='224.1.2.3', destPort=6003, localAddr="10.65.39.191", localPort=0)
    
    filePath = r'E:\PythonPrj\NORM\norm-master\doc\npcUsage.pdf'
    session.fileEnqueue(filePath, info=filePath.encode() )
    #await asyncio.sleep(2)
    
    
    
    
if __name__ == "__main__":
    #trio.run( main )
    loop = asyncio.new_event_loop()
    loop.run_until_complete( main())
    loop.run_forever()

    
    
    