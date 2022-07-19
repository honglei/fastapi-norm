from pydantic import BaseSettings

class Settings(BaseSettings):
    recvFileDir:str|None =r"../recvFiles"  
    loopbackEnable:bool = True

    class Config:
        case_sensitive = True



settings = Settings()
