
from fastapi import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST
import pynorm
from pynorm.object import Object
from pynorm.constants import ObjectType
def object2dict(obj:Object) -> dict:
    '''
        将Object转换为字典 
    '''
    objType:ObjectType = obj.type
    item = {"handle":obj.handle, "bytesPending":obj.getBytesPending(),"info":obj.getInfo(), "type":objType.name  }
    if objType == ObjectType.FILE:
        item['fileName'] = obj.filename.decode() #对于未完成文件，为临时文件名称    
    return item

def get_session(instance:pynorm.Instance, linkID:int) -> pynorm.session.Session:
    if linkID not in instance._sessionIndex2Session:
        raise HTTPException(HTTP_400_BAD_REQUEST, detail=f"linkID {linkID} not exists!")
    session:pynorm.session.Session = instance._sessionIndex2Session[linkID]
    return session