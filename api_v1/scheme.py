
from pydantic import BaseModel, validator,Field
from ipaddress import IPv4Address
        
class Reply(BaseModel):
    success:bool
    error:str|None
    
class FailureReply(BaseModel):
    success:bool= Field(default=False)
    error:str 
    
class AddObjectRsp(BaseModel):
    success:bool= Field(default=True)
    handler:int
    
    
class LinkBase(BaseModel):
    '''
    
    '''
    destAddr:IPv4Address = Field(default="224.1.2.3", description="组播地址") 
    destPort:int = Field(default=6003,description="组播包的目的端口")
    localAddr:IPv4Address = Field(default="10.65.39.191", description="信息分发所在机器的真实IP地址，发送方为 发送IP组播包的源地址， 接收方为 对组播包接收情况进行响应的单播包的源地址")
    loopbackEnable:bool|None = Field(default=False,description="自发自收模式，仅测试时启用")
    srcAddr:IPv4Address|None =Field(default=None, description="用于SSM只当组播包的源地址")
    @validator("destAddr", always=True)
    def not_valid_destAddr(cls, v:IPv4Address):
        """To validate ip-address."""
        assert v.is_multicast
        return str(v) 
    @validator("localAddr","srcAddr", always=True)
    def not_valid_localAddr(cls, v:IPv4Address):
        """To validate ip-address."""
        return str(v)  