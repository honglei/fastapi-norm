from fastapi import APIRouter
router = APIRouter()
from fastapi import Depends, HTTPException
from starlette.status import HTTP_400_BAD_REQUEST
import pynorm
import deps
from pynorm.constants import ObjectType

from .norm_common import object2dict



#bool NormSetRxSocketBuffer(NormSessionHandle sessionHandle,
                           #unsigned int      bufferSize);


@router.get("/objects_status")
async def objects_status(linkID:int,
                   instance:pynorm.Instance = Depends(deps.get_instance),   
                      ):
    if session:=instance._sessionIndex2Session.get(linkID):
        session:pynorm.session.Session
        #pynorm.object.Object.type
        results = []
        for objHandle, obj in session.id2obj.items():
            results.append( object2dict(obj) )
            
        return results 
    else:
        raise HTTPException(HTTP_400_BAD_REQUEST, detail=f"linkID {linkID} not exists!")
    
    
@router.get("/one_object_status")
async def one_object_status(linkID:int,
                    fileHandle:int,
                   instance:pynorm.Instance = Depends(deps.get_instance),   
                      ):
    '''
       获取Session的Object对象的状态信息
    '''
    
    if session:=instance._sessionIndex2Session.get(linkID):
        if obj :=  session.id2obj.get(fileHandle):
            obj:pynorm.object.Object
            return { "bytesPending":obj.bytesPending, "info":obj.info,"filename":obj.filename }
        else:
            raise HTTPException(HTTP_400_BAD_REQUEST, detail=f"fileHandle {fileHandle} not exists!")
    else:
        raise HTTPException(HTTP_400_BAD_REQUEST, detail=f"linkID {linkID} not exists!")


@router.get("/cancel_object")
async def cancel_object(linkID:int,
                    objHandle:int,
                   instance:pynorm.Instance = Depends(deps.get_instance),   
                      ):
    '''
       取消Session中 handle 为<objHandle>的对象  
    '''
    if session:=instance._sessionIndex2Session.get(linkID):
        if obj :=  session.id2obj.get(objHandle):
            obj.cancel()
            session.id2obj.pop( objHandle ) 
            return { "bytesPending":obj.getBytesPending(),"info":obj.getInfo() }
        else:
            raise HTTPException(HTTP_400_BAD_REQUEST, detail=f"fileHandle {objHandle} not exists!")
    else:
        raise HTTPException(HTTP_400_BAD_REQUEST, detail=f"linkID {linkID} not exists!")
    
    
@router.get("/remove_objects")
async def remove_objects( linkID:int,
                    instance:pynorm.Instance = Depends(deps.get_instance),
                ):
    '''
         清除掉 bytesPending=0 的对象 
    '''
    if session:=instance._sessionIndex2Session.get(linkID):
        session:pynorm.session.Session
        removeIDs = []
        for k,v in session.id2obj.items():
            if v.bytesPending ==0:
                removeIDs.append(k)
        for k in removeIDs:
            obj =session.id2obj.pop(k)
            #obj.cancel()
    else:
        raise HTTPException(HTTP_400_BAD_REQUEST, detail=f"linkID {linkID} not exists!")