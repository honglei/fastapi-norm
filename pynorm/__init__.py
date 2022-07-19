"""
pynorm - Python wrapper for NRL's libnorm
By: Tom Wambold <wambold@itd.nrl.navy.mil>
"""


from pynorm.core import libnorm, NormError
from pynorm.constants import *

from pynorm.instance import Instance

def setDebugLevel(level: DebugLevel):
    libnorm.NormSetDebugLevel(level.value)

def getDebugLevel() -> DebugLevel:
    return DebugLevel( libnorm.NormGetDebugLevel() )
