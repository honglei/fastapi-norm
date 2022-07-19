'''
    
'''
import os
if os.name=='nt':
    os.add_dll_directory(os.path.dirname(__file__))


#import psuti_ext
#psuti_ext.listListenPortProc()

import asyncio
from fastapi_offline import FastAPIOffline

app = FastAPIOffline(
    title = "Norm Recv Test",
    description ='''
        
    '''
)

from config import settings

import os
# 创建日志目录、文件接收目录
dest_dirs = ["../log", settings.recvFileDir]
for dest_dir in dest_dirs:
    path = os.path.expanduser( dest_dir  ) 
    
    if not os.path.exists(path):
        os.makedirs(path)

from fastapi import APIRouter
api_router = APIRouter()

from api_v1 import web_instance, session_common,session_recv
api_router.include_router(web_instance.router, prefix="/instance", tags=["Instance"])
api_router.include_router(session_recv.router, prefix="/session", tags=["Router"])
api_router.include_router(session_common.router, prefix="/common", tags=["SessionCommon"])
app.include_router(api_router)


import deps
@app.on_event("startup")
async def on_startup() -> None:
    '''
        添加其他功能
    '''
    deps.init_receiver()


@app.on_event("shutdown")
async def on_shutdown() -> None:
    '''
    
    '''
    if deps.task:
        deps.task.cancel()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv)<2:
        print ("<cmd_name> <web_port>")
        exit(1)
    import uvicorn
    uvicorn.run(app,host='0.0.0.0',port=int(sys.argv[1]),loop='asyncio')
    
    
