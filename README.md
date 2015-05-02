Blender + Python 3 + LeapMotion + Oculus Rift under Arch Linux
==============================================================

LeapMotion and Python 3 API
---------------------------

**NOTE:** *Do not plug the Leap into a USB 3.0 port, for some unknown reason, it
will be massively slower, than on a standard USB 2.0 port*

- Install repository based SDK and drivers:

        $ yaourt -S leap-motion-sdk leap-motion-driver

- Start and enable driver on start-up:

        $ sudo systemctl start leapd.service
        $ sudo systemctl enable leapd.service

- Download the SDK from [here](https://developer.leapmotion.com)
- Install `swig`:

        $ sudo pacman -Syu swig

- Navigate to the folder where the SDK was downloaded to:

        $ cd <path-to-downloads>/LeapDeveloperKit_<version-number>_linux/LeapSDK/include

- Wrap the source file with `swig`

        $ swig -c++ - python -o LeapPython.cpp -interface LeapPython Leap.i

  It is very likely, that the generated code has one "slappy" solution, which
  needs to be fixed, otherwise the compiler will complain about this with the
  following error:

        LeapPython.cpp:14510:30: error: taking the address of a temporary object of type 'std::string' (aka 'basic_string<char>') [-Waddress-of-temporary]

        result = (std::string *) &Leap_Device_serialNumber_get(arg1);
                                 ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        1 error generated.

  This can be fixed by changing the line which throws the error to the following
  two lines:

        std::string serial_number = Leap_Device_serialNumber_get(arg1);
        result = (std::string *) &serial_number;

- Compile the generated `.cpp` code:

        $ g++ -fPIC -I /usr/include/python3.4m/ LeapPython.cpp /usr/lib/Leap/libLeap.so -shared -o LeapPython.so

- Migrate the Python module from Python 2 to Python 3:

        $ 2to3 -w Leap.py

- Rename originally installed components as backups:

        $ cd /usr/lib/Leap
        $ sudo mv Leap.py _Leap.py
        $ sudo mv LeapPython.so _LeapPython.so
        $ sudo mv libLeap.so

- Copy new files at installation:

        $ sudo cp <path-to-downloads>/LeapDeveloperKit_<version-number>_linux/LeapSDK/include/Leap.py .
        $ sudo cp <path-to-downloads>/LeapDeveloperKit_<version-number>_linux/LeapSDK/include/LeapPython.so .
        $ sudo cp <path-to-downloads>/LeapDeveloperKit_<version-number>_linux/LeapSDK/lib/x64/libLeap.so .

- Add library path to the environment:

        $ nano ~/.bashrc
        $ export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/lib/Leap/
        $ source ~/.bashrc

- The following lines should be included into every python file which is using
  the `Leap` module:

        from sys import path as sys_path
        sys_path.insert(0, '/usr/lib/Leap')
        import Leap

- Enjoy ;)

*Sources: [support.leapmotion.com](https://support.leapmotion.com/entries/39433657-Generating-a-Python-3-3-0-Wrapper-with-SWIG-2-0-9) and [leap and python3 on ubuntu](http://www.warp1337.com/content/leap-motion-sdk-python3-python-33-ubuntu)*



Oculus Rift and Python 3 API
----------------------------

- Download the SDK from [here](https://developer.oculus.com/downloads), at this
  very moment, the latest version available is: `0.5.0.1-beta`

- Navigate to the download folder and install the SDK:

        $ make
        $ sudo make install

- Using Oculus SDK 0.4.4: Navigate to `ovr_sdk_linux_0.4.4` and type:

        $ sudo rmmod uvcvideo
        $ sudo modprobe uvcvideo quirks=0
        $ sudo ./oculusd

- Using Oculus SDK 0.5.0.1-beta: Navigate to `ovr_sdk_linux_0.5.0.1` and type:

        $ sudo Service/OVRServer/Bin/Linux/x86_64/ReleaseStatic/ovrd

- Run the app you want...

*Sources: [oculus c api 0.5](https://codelab.wordpress.com/2014/09/07/oculusvr-sdk-and-simple-oculus-rift-dk2-opengl-test-program/) and [forum tips on segfault](https://forums.oculus.com/viewtopic.php?t=16593)
