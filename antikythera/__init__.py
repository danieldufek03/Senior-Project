import pkg_resources
import sqlite3
try:
    __version__  = pkg_resources.get_distribution(__name__).version
    _logger      = logging.getLogger(__name__)
    __author__   = "TeamAwesome"
    self.datadir = appdirs.user_data_dir(__name__, __author__)
    
    self.datadir.run('PRAGMA busy_timeout', 60000)
except:
    __version__ = 'unknown'
