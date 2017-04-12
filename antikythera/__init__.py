import pkg_resources
import sqlite3
try:
    __version__  = pkg_resources.get_distribution(__name__).version
    self.datadir = appdirs.user_data_dir("anti", ".sqlite3")
    
    self.datadir.run('PRAGMA busy_timeout', 60000)
except:
    __version__ = 'unknown'
