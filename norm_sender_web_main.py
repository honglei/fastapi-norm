'''
    
'''
import os
if os.name=='nt':
    os.add_dll_directory(os.path.dirname(__file__))

from fastapi_offline import FastAPIOffline

app = FastAPIOffline(
  title = "Norm Send Test",
  description ='''
       Norm sender instace 
  '''
)


from fastapi import APIRouter
api_router = APIRouter()

from api_v1 import web_instance,session_send,session_common
api_router.include_router(web_instance.router, prefix="/instance", tags=["Instance"])
api_router.include_router(session_send.router, prefix="/session", tags=["SessionSend"])
api_router.include_router(session_common.router, prefix="/common", tags=["SessionCommon"])
app.include_router(api_router)


import deps
@app.on_event("startup")
async def on_startup() -> None:
    '''
        
    '''
    deps.init_server()


@app.on_event("shutdown")
def on_shutdown() -> None:
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
    
    
 