"""Heroku Worker deamon"""

from cwear.bridge.bridge import HumanApiDeviceCloudBridge
import logging
import sys
import time

logger = logging.getLogger("boot")


def _setup_root_logger():
    stream_handler = logging.StreamHandler(sys.stdout)
    root_logger = logging.getLogger("")
    root_logger.addHandler(stream_handler)
    root_logger.setLevel("INFO")
    formatter = logging.Formatter("%(asctime)s | %(name)-12s | %(message)s",
                                  "%m/%d %H:%M:%S")
    stream_handler.setFormatter(formatter)

if __name__ == "__main__":
    _setup_root_logger()
    logger.critical('--------------------------BOOT--------------------------')
    bridge = HumanApiDeviceCloudBridge()

    while True:
        bridge.update()
        time.sleep(10)
