"""
pynorm - Python wrapper for NRL's libnorm
By: Tom Wambold <wambold@itd.nrl.navy.mil>
"""

from __future__ import absolute_import

from typing import Optional,Union
from builtins import object
import ctypes
import typing

import pynorm.constants as c
from pynorm.core import libnorm, NormError
from pynorm.object import Object
#from pynorm.instance import Instance

class Session(object):
    """This represents a session tied to a particular NORM instance"""

    ## Public functions
    def __init__(self, instance, address:str, port:int, localId=c.NORM_NODE_ANY, index:typing.Hashable=None):
        """
        instance - An instance of NormInstance
        address - String of multicast address to join
        port - valid unused port number
        localId - NormNodeId
        """
        self._instance  = instance
        # NormSessionHandle
        self._session:int = libnorm.NormCreateSession(instance, address.encode(), port, localId)
        self._index:typing.Hashable = index # user defined index for this session
        self.sendGracefulStop:bool = False
        self.gracePeriod:int = 0

        self.multiAddr:str = address
        self.port:int = port
        # extend
        self.id2obj:dict[int,Object] = {} #
        self.ackNodeIDs:set[int] = set() #所有AckNodeID的集合

    def destroy(self):
        '''
           not used?
        '''
        libnorm.NormDestroySession(self)
        del self._instance._sessions[self._session]

    def setUserData(self, data:str):
        """data should be a string"""
        libnorm.NormSetUserData(self, data.encode('utf-8'))

    def getUserData(self):
        data = libnorm.NormGetUserData(self)
        return data.decode('utf-8') if data else None

    def getNodeId(self):
        return libnorm.NormGetLocalNodeId(self)

    def setTxPort(self, txPort:int, enableReuse=False, txBindAddr=None):
        '''
        bool NormSetTxPort(NormSessionHandle sessionHandle,
                   UINT16            txPortNumber,
                   bool              enableReuse DEFAULT(false),
                   const char*       txBindAddress DEFAULT((const char*)0));  // if non-NULL, bind() to <txBindAddress>/<txPortNumber>
        '''

        libnorm.NormSetTxPort(self, txPort, enableReuse, 
                              txBindAddr.encode('utf-8') if txBindAddr else None )
        
    def setTxOnly(self, txOnly:bool=False, connectToSessionAddress:bool=False):
        '''
            void NormSetTxOnly(NormSessionHandle sessionHandle,
                       bool              txOnly,
                       bool              connectToSessionAddress)
        '''
        libnorm.NormSetTxOnly(self, txOnly, connectToSessionAddress)
        

    def setRxPortReuse(self, enable:bool, rxBindAddr:Optional[str]=None, senderAddr:Optional[str]=None, senderPort:int=0):
        '''
        This function allows the user to control the port reuse and binding behavior for the receive socket used for the given NORM sessionHandle. 
        When the enablReuse parameter is set to true, reuse of the NormSession port number by multiple NORM instances or sessions is enabled.
                        bool              enableReuse,
                        const char*       rxBindAddress = (const char*)0,
                        const char*       senderAddress = (const char*)0,
                        UINT16            senderPort = 0);
        '''
        libnorm.NormSetRxPortReuse(self, enable, 
                                   rxBindAddr.encode('utf-8') if rxBindAddr else None,
                                   senderAddr.encode('utf-8') if senderAddr else None,
                                   senderPort)

    def setMulticastInterface(self, iface:str):
        libnorm.NormSetMulticastInterface(self, iface.encode('utf-8'))
    
    def setSSM(self, srcAddr:str):
        libnorm.NormSetSSM(self, srcAddr.encode('utf-8'))
        
    def setTTL(self, ttl) -> bool:
        return libnorm.NormSetTTL(self, ttl)

    def setTOS(self, tos) -> bool:
        return libnorm.NormSetTOS(self, tos)

    def setLoopback(self, loopbackEnable:bool=False):
        libnorm.NormSetLoopback(self, loopbackEnable)

    def getReportInterval(self) -> int:
        return libnorm.NormGetReportInterval(self)

    def setReportInterval(self, interval:int):
        libnorm.NormSetReportInterval(self, interval)

    ## Sender functions
    def startSender(self, sessionId:int, bufferSpace:int, segmentSize:int, blockSize:int, numParity:int, fecId=0) -> bool:
        return libnorm.NormStartSender(self, sessionId, bufferSpace, segmentSize, blockSize, numParity, fecId)

    def stopSender(self) -> bool:
        return libnorm.NormStopSender(self)

    def setTxRate(self, txRate:float):
        libnorm.NormSetTxRate(self, txRate)
        
    def getTxRate(self) -> float:
        return libnorm.NormGetTxRate(self)

    def setTxSocketBuffer(self, size:int):
        libnorm.NormSetTxSocketBuffer(self, size)

    def setCongestionControl(self, ccEnable, adjustRate=True):
        '''
            必须在调用startSender前使用
        '''
        libnorm.NormSetCongestionControl(self, ccEnable, adjustRate)
        
    def setEcnSupport(self, ecnEnable, ignoreLoss=False, tolerateLoss=False):
        libnorm.NormSetEcnSupport(self, ecnEnable, ignoreLoss, tolerateLoss)
        
    def setFlowControl(self, flowControlFactor):
        libnorm.NormSetFlowControl(self, flowControlFactor)

    def setTxRateBounds(self, rateMin, rateMax) -> bool:
        '''
           If both rateMin and rateMax are greater than or equal to zero, 
           but (rateMax < rateMin), the rate bounds will remain unset or unchanged and the function will return false.
        '''
        return libnorm.NormSetTxRateBounds(self, rateMin, rateMax)

    def setTxCacheBounds(self, sizeMax:int, countMin:int, countMax:int):
        libnorm.NormSetTxCacheBounds(self, sizeMax, countMin, countMax)

    def setAutoParity(self, parity:int):
        libnorm.NormSetAutoParity(self, parity)

    def getGrttEstimate(self) -> float:
        return libnorm.NormGetGrttEstimate(self)

    def setGrttEstimate(self, grtt:float):
        return libnorm.NormSetGrttEstimate(self, grtt)

    def setGrttMax(self, grttMax):
        return libnorm.NormSetGrttMax(self, grttMax)

    def setGrttProbingMode(self, probingMode:c.ProbingMode):
        libnorm.NormSetGrttProbingMode(self, probingMode.value)

    def setGrttProbingInterval(self, intervalMin:int, intervalMax:int):
        libnorm.NormSetGrttProbingInterval(self, intervalMin, intervalMax)

    def setBackoffFactor(self, factor:int):
        libnorm.NormSetBackoffFactor(self, factor)

    def setGroupSize(self, size:int):
        libnorm.NormSetGroupSize(self, size)
        
    def setTxRobustFactor(self, robustFactor:int):
        libnorm.NormSetTxRobustFactor(self, robustFactor)

    def fileEnqueue(self, filename:str, info:bytes=b""):
        return Object(libnorm.NormFileEnqueue(self, filename.encode(), info, len(info)))

    def dataEnqueue(self, data:bytes, info:bytes=b""):
        return Object(libnorm.NormDataEnqueue(self, data, len(data), info, len(info)))

    def requeueObject(self, normObject):
        libnorm.NormRequeueObject(self, normObject)

    def streamOpen(self, bufferSize:int, info=b""):
        return Object(libnorm.NormStreamOpen(self, bufferSize, info, len(info)))

    def sendCommand(self, cmdBuffer:bytes, robust=False):
        return libnorm.NormSendCommand(self, cmdBuffer, len(cmdBuffer), robust)
	
    def cancelCommand(self):
        libnorm.NormCancelCommand(self)

    def setWatermark(self, normObject:Union[int,Object], overrideFlush=False):
        libnorm.NormSetWatermark(self, normObject, overrideFlush)
        
    def resetWatermark(self):
        libnorm.NormResetWatermark(self)
        
    def cancelWatermark(self):
        libnorm.NormCancelWatermark(self)

    def addAckingNode(self, nodeID:int):
        '''
           avoid adding any invalid nodeID 
        '''
        success:bool = libnorm.NormAddAckingNode(self, nodeID)
        if success:
            self.ackNodeIDs.add(nodeID)
        return success
    
    def removeAckingNode(self, nodeID:int) -> bool:
        try:
            self.ackNodeIDs.remove(nodeID)
        except Exception as e:
            return False
        libnorm.NormRemoveAckingNode(self, nodeID)
        return True
        
    #def getNextAckingNode(self, reset:bool=False):
        #'''
            #will not work
        #'''
        #return c.AckingStatus( libnorm.NormGetNextAckingNode(self, reset) )

    def getAckingStatus(self, nodeId:int=c.NORM_NODE_ANY) -> c.AckingStatus:
        return c.AckingStatus( libnorm.NormGetAckingStatus(self, nodeId) )

    ## Receiver functions
    def startReceiver(self, bufferSpace:int):
        '''
        The bufferSpace parameter is used to set a limit on the amount of bufferSpace allocated by the receiver per active NormSender within the session.
        The appropriate bufferSpace to use is a function of expected network delay*bandwidth product and packet loss characteristics. 
        '''
        libnorm.NormStartReceiver(self, bufferSpace)

    def stopReceiver(self):
        """This will be called automatically if the receiver is active"""
        libnorm.NormStopReceiver(self)

    def setRxCacheLimit(self, count):
        libnorm.NormSetRxCacheLimit(self, count)
        
    def setRxSocketBuffer(self, size:int):
        libnorm.NormSetRxSocketBuffer(self, size)

    def setSilentReceiver(self, silent:bool, maxDelay:Optional[int]=None):
        if maxDelay == None:
            maxDelay = -1
        libnorm.NormSetSilentReceiver(self, silent, maxDelay)

    def setDefaultUnicastNack(self, enable:bool):
        libnorm.NormSetDefaultUnicastNack(self, enable)
        
    def setDefaultSyncPolicy(self, policy:c.SyncPolicy):
        libnorm.NormSetDefaultSyncPolicy(self, policy.value)

    def setDefaultNackingMode(self, mode:c.NackingMode):
        libnorm.NormSetDefaultNackingMode(self, mode.value)

    def setDefaultRepairBoundary(self, boundary:int):
        libnorm.NormSetDefaultRepairBoundary(self, boundary)
        
    def setDefaultRxRobustFactor(self, rxRobustFactor:int):
        libnorm.NormSetDefaultRxRobustFactor(rxRobustFactor)
        
    def setMessageTrace(self, state):
        libnorm.NormSetMessageTrace(self, state)

    ## Properties
    nodeId = property(getNodeId)
    grtt = property(getGrttEstimate, setGrttEstimate)
    userData = property(getUserData, setUserData)
    reportInterval = property(getReportInterval, setReportInterval)

    ## Private functions
    def __del__(self):
        self.stopReceiver()
        self.stopSender()
        libnorm.NormDestroySession(self)

    @property
    def _as_parameter_(self):
        """Used when passing this object to ctypes functions"""
        return self._session

    def __cmp__(self, other):
        def cmp(a, b):
            return (a > b) - (a < b)        
        try:
            return cmp(self._as_parameter_, other._as_parameter)
        except AttributeError:
            return cmp(self._as_parameter_, other)

    def __hash__(self):
        return self._as_parameter_
