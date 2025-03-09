# Tap Race

This is a simple multiplayer game for Android, developed in Python using Kivy. The primary objective of the project was to gain experience in device comunnication using the socket library, manage concurrent threads with the threading module, design the frontend with KivyMD, and utilize Buildozer to create the `.apk` file. 

## Environment Set Up:

1. Install dependencies:
    ```bash
    $ pip install kivy
    $ pip install https://github.com/kivymd/KivyMD/archive/master.zip
    $ pip install netifaces
    $ pip install buildozer cython setuptools
    ```
## Buildozer Usage
1. Create a new subdirectory within the project directory to move the `.py` files, and any other file used in the Python code, then change to the new directory
    ```bash
    $ mkdir myapp
    $ mv main.py server.py client.py myutils.py layout.kv nasalization.ttf myapp
    $ cd myapp
    ```
2. On the new directory, create the buildozer.spec file by running the following command:
    ```bash
    $ buildozer init
    ```
3. Customize the buildozer.spec file:
    ```bash
    $ nano buildozer.spec
    ```
   - Set the following parameters:
    ```yml
    # (str) Title of your application
    title = TapRace
    
    # (str) Package name
    package.name = tapraceapp 

    # (list) Source files to include (let empty to include all the files)
    source.include_exts = py, png, jpg, kv, atlas, ttf
   
    # (list) Application requirements
    # comma separated e.g. requirements = sqlite3,kivy
    requirements = python3,
        kivy,
        https://github.com/kivymd/KivyMD/archive/master.zip,
        materialyoucolor,
        exceptiongroup,
        asyncgui,
        asynckivy,
        netifaces

    # (list) Permissions
    # (See https://python-for-android.readthedocs.io/en/latest/buildoptions/#build-options-1 for all the supported syntaxes and properties)
    android.permissions = INTERNET
    ```
4. Start a Android/debug build with:
    ```bash
    $ buildozer -v android debug 
    ```
5. If `buildozer.spec` has changed, run:
    ```bash
    $ buildozer android clean
    $ buildozer -v android debug 
    ```
