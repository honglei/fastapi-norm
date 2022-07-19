'''

4.5.1. NormStartReceiver()
4.5.2. NormStopReceiver()

4.5.3. NormSetRxCacheLimit()
4.5.4. NormSetRxSocketBuffer()

4.5.5. NormSetSilentReceiver()
4.5.6. NormSetDefaultUnicastNack()
4.5.7. NormNodeSetUnicastNack()
4.5.8. NormSetDefaultSyncPolicy()

4.5.9. NormSetDefaultNackingMode()
4.5.10. NormNodeSetNackingMode()
4.5.11. NormObjectSetNackingMode()

4.5.12. NormSetDefaultRepairBoundary()
4.5.13. NormNodeSetRepairBoundary()
4.5.14. NormSetDefaultRxRobustFactor()
4.5.15. NormNodeSetRxRobustFactor()

4.5.16. NormStreamRead()
4.5.17. NormStreamSeekMsgStart()
4.5.18. NormStreamGetReadOffset()
'''

from fastapi import APIRouter
router = APIRouter()
from fastapi import Depends, HTTPException
from starlette.status import HTTP_400_BAD_REQUEST
import pynorm
import deps
import asyncio
import os
from .scheme import LinkBase  

from .norm_common import get_session

from util.netifaces_ext import get_interface_by_ip
@router.post("/session", )
async def create_recver_session(
    create:LinkBase, 
    linkID:int=1, # 后面用数据库
    instance:pynorm.Instance = Depends(deps.get_instance),
):
    '''
       添加接收Session
    '''
    if linkID in instance._sessionIndex2Session:
        raise HTTPException(HTTP_400_BAD_REQUEST, detail=f"linkID {linkID} already exists!")
    
    localAddr:str = create.localAddr
    loop = asyncio.get_running_loop()
    iface:str|None  = await loop.run_in_executor(None, get_interface_by_ip, localAddr)
    if not iface:
        raise HTTPException(HTTP_400_BAD_REQUEST, detail=f"{localAddr} is not valid local Addr")     
    
    if os.name =="nt":
        iface = None
    
    session = deps.create_recver_session(instance=instance,multiAddr=create.destAddr, port=create.destPort, 
                                         localAddr=create.localAddr, 
                                         iface = iface,
                                         loopbackEnable=create.loopbackEnable,
                                         sessionIndex=linkID)
    return {"sessionHandle": session._session}

@router.delete("/session", )
async def delete_recver_session(
    linkID:int, 
    instance:pynorm.Instance = Depends(deps.get_instance),
):
    '''
       移除接收链路 
    '''
    if linkID not in instance._sessionIndex2Session:
        raise HTTPException(HTTP_400_BAD_REQUEST, detail=f"linkID {linkID} not exists!")
    session = instance.destroySessionByIndex(linkID)
    return {"sessionHandle": session._session }


@router.put("/defaultRepairBoundary", )
async def set_default_repair_boundary(
    linkID:int, 
    boundary:pynorm.RepairBoundary ,
    instance:pynorm.Instance = Depends(deps.get_instance),
):
    '''
        BOUNDARY_BLOCK  = 0 
        BOUNDARY_OBJECT = 1
void NormSetDefaultRepairBoundary(NormSessionHandle  sessionHandle,
                                  NormRepairBoundary repairBoundary);
    '''
    session =get_session(instance,linkID)
    session.setDefaultRepairBoundary(boundary)
    #return {"sessionHandle": session._session }

@router.put("/defaultRxRobustFactor", )
async def set_default_rx_robust_factor(
    linkID:int, 
    rxRobustFactor:int ,
    instance:pynorm.Instance = Depends(deps.get_instance),
):
    '''
    void NormSetDefaultRxRobustFactor(NormSessionHandle sessionHandle,
                                      int     rxRobustFactor);
    '''
    session =get_session(instance,linkID)
    session.setDefaultRxRobustFactor (rxRobustFactor)
    #return {"sessionHandle": session._session }



@router.post("/start_receiver", )
async def start_receiver( 
    linkID:int,
    bufferSpace:int=5*1024*1024,
    instance:pynorm.Instance = Depends(deps.get_instance),
):
    '''
        启用Session的接收，创建链路时自动启用
    '''
    session =get_session(instance,linkID)
    session.startReceiver(bufferSpace=bufferSpace)
    return {"sessionHandle": session._session}


@router.post("/stop_receiver", )
async def stop_receiver( 
    linkID:int,
    instance:pynorm.Instance = Depends(deps.get_instance),
):
    if linkID in instance._sessionIndex2Session:
        raise HTTPException(HTTP_400_BAD_REQUEST, detail=f"linkID {create.linkID} already exists!")
    session:pynorm.session.Session =  instance._sessionIndex2Session[linkID]
    session.stopReceiver( )
    return {"sessionHandle": session._session}


@router.put("/silentReceiver", )
async def set_silent_receiver(
    linkID:int, 
    silent:bool,
    maxDelay:int=-1,
    instance:pynorm.Instance = Depends(deps.get_instance),
):
    '''
        将Sesssion设置为静默模式 
        
         the host does not generate any protocol messages while operating as a receiver 
         Silent receivers are dependent upon proactive FEC transmission or using repair information requested by other non-silent receivers within the group to achieve reliable transfers.
    '''
    if linkID not in instance._sessionIndex2Session:
        raise HTTPException(HTTP_400_BAD_REQUEST, detail=f"linkID {linkID} not exists!")
    session:pynorm.session.Session = instance._sessionIndex2Session(linkID)
    session.setSilentReceiver(silent,maxDelay=maxDelay)
    return {"sessionHandle": session._session }    








