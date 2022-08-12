# -*- encoding=utf-8 -*-
# This file was generated automatically

from .logusto import Logusto, LogConfig
from loguru import logger

__version__ = (1, 0, 0, 0)

logusto = Logusto(
    __name__,
    version_tuple=__version__,
    log_config=LogConfig(level=3, retention_days=3)
    )

def start():
    try:
        print("dadata_project v"+".".join(map(str, __version__)))
        # YOUR CODE HERE
        pass
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    start()
                