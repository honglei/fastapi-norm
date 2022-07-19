# fastapi-norm

The demo application use FastApi(https://github.com/tiangolo/fastapi) to wrap and test Norm(https://github.com/USNavalResearchLaboratory/norm),  
We use linkID as the user-defined  index for Norm sessions. Two fastapi application are provide:

  norm_sender_web_main.py  
  norm_recv_web_main.py

On Win10, you need install Microsoft Visual C++ Redistributable packages for Visual Studio 2015, 2017, 2019, and 2022,
See https://docs.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170, If you have some conflicts, try using 
MicrosoftProgram_Install_and_Uninstall.meta.diagcab to uninstall and reinstall  Visual C++ Redistributable package. 

On linux, file `libnorm.so` is compile under Debian10, and this lib should be in ctypes search paths, like in environment variable LD_LIBRARY_PATH

the subdir is  pynorm lib,  right now support Python3 only,  the following changes are made:

* constants.py --- using enum.Enum instead and remove "NORM_" prefix
* session.py --- add type hints, add some missing functions, add return boolean value if libnorm support.
* add a user-defined index for search sessions in instance.  

