import os
import pathlib
import ws
import Utility.DB_Prepare


init_file = ".first.run"
env = "prod"  # Change ENV to anything other than prod to change to development mode.


cw = os.getcwd()  # save current directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))  # change to current files location

if not os.path.exists(init_file): # this is first run
    Utility.DB_Prepare.main()  # setup DB
    pathlib.Path(init_file).touch()


ws.main(env)
