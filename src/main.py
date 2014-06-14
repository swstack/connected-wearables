"""Heroku Worker deamon"""

from cwear.bridge.bridge import HumanApiDeviceCloudBridge
import logging
import sys
import time
from cwear.bridge.humanapi import HumanAPI
from cwear.db.model import DatabaseManager, CwearApplication

logger = logging.getLogger("boot")


def _setup_root_logger():
    stream_handler = logging.StreamHandler(sys.stdout)
    root_logger = logging.getLogger("")
    root_logger.addHandler(stream_handler)
    root_logger.setLevel("INFO")
    formatter = logging.Formatter("%(asctime)s | %(name)-12s | %(message)s",
                                  "%m/%d %H:%M:%S")
    stream_handler.setFormatter(formatter)

def get_cwear_applications(db):
    return db.query(CwearApplication).all()

if __name__ == "__main__":
    _setup_root_logger()
    logger.critical('--------------------------BOOT--------------------------')
    dbmgr = DatabaseManager()
    db = dbmgr.get_db_session()
    bridge = HumanApiDeviceCloudBridge(dbmgr)

    while True:
        # Get the cwear applications and iterate over them
        cwear_applications = get_cwear_applications(db)
        for application in cwear_applications:
            bridge.update(application)
        time.sleep(1.0)
