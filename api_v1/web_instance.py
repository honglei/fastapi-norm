

from fastapi import APIRouter
router = APIRouter()
from fastapi import Depends, HTTPException
from starlette.status import HTTP_400_BAD_REQUEST
import pynorm
import deps


#@router.get("/stop")
#async def start_instance(
    #instance:pynorm.Instance = Depends(deps.get_instance),
#):
    #'''
        #norm本身存在问题，不使用该接口 
    #'''
    #instance.stop()
    
#@router.get("/restart")
#async def start_instance(
    #instance:pynorm.Instance = Depends(deps.get_instance),
#):
    #'''
        #norm本身存在问题，不使用该接口，会导致程序崩溃，原因待查 
    #'''
    #instance.restart()


import asyncio
from pynorm.constants import ObjectType
from .norm_common import object2dict
@router.get("/status")
async def instance_status(
    task :asyncio.Task = Depends(deps.get_task),
    instance:pynorm.Instance = Depends(deps.get_instance),
    ):
    '''
        get the status of Event Read task, and the status of all links.
        
        获取 Event读取任务的状态，该任务不应该关闭，如果关闭则收不到事件；
    '''
    sessions =[]
    for k,v in  instance._sessionIndex2Session.items():
        v:pynorm.session.Session
        sessions.append( {"linkID":k, "handle":v._session, "multiAddr":v.multiAddr,"port":v.port, "grtt":v.grtt,"reportInterval":v.reportInterval})
        
    return {
        "task_cancelled": task.cancelled(), 
        "done":task.done(),
        "sessions":sessions,
        "objects":[ object2dict(v)  for v in instance._objects.values() if v.type!=ObjectType.NONE ]
        
    }



    


    




    

