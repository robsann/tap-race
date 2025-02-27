# Environment Set Up:

1. Install dependencies:
    ```bash
    $ pip install kivy
    $ pip install https://github.com/kivymd/KivyMD/archive/master.zip
    ```
## Buildozer Usage
1. Create a new subdirectory within the project directory to move the `.py` files, then run Buildozer from within this directory:
    ```bash
    $ mkdir myapp
    $ mv main.py myapp
    $ cd myapp
    ```
2. Create the buildozer.spec file by running the following command:
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
   
    # (list) Application requirements
    # comma separated e.g. requirements = sqlite3,kivy
    requirements = ...
    ```
4. Start a Android/debug build with:
    ```bash
    $ buildozer -v android debug 
    ```
5. If `buildozer.spec` has changed, run:
    ```bash
    $ buildozer android clean 
    ```