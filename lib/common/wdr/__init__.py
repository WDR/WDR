import logging
import sys

__all__ = ['config', 'control', 'task', 'manifest', 'util']

logger = logging.getLogger('wdr')

MAJOR_VERSION = 0
MINOR_VERSION = 8
PATCH_VERSION = 0


class WsadminObjects:
    __wsadminObjects = None

    def __init__(self):
        if self.__wsadminObjects is None:
            rootFrame = sys._getframe()
            while rootFrame.f_back:
                rootFrame = rootFrame.f_back
            values = []
            for v in (
                'AdminApp', 'AdminConfig', 'AdminControl', 'AdminTask', 'Help'
            ):
                try:
                    values.append(rootFrame.f_globals[v])
                except:
                    logger.warning('unable to retrieve wsadmin object: %s', v)
                    values.append(None)
            self.__wsadminObjects = values

    def getObjects(self):
        return tuple(self.__wsadminObjects)


(
    AdminApp, AdminConfig, AdminControl, AdminTask, Help
) = WsadminObjects().getObjects()


def versionInfo():
    logger.info(
        'using WDR (https://wdr.github.io/WDR/) version %d.%d.%d',
        MAJOR_VERSION, MINOR_VERSION, PATCH_VERSION
    )
    if AdminControl and AdminControl.adminClient:
        logger.info(
            'the client is connected to host %s:%s using %s connector',
            AdminControl.host, AdminControl.port, AdminControl.type
        )
        logger.info(
            'the target process is %s/%s/%s',
            AdminControl.cell, AdminControl.node, AdminControl.processName
        )
    else:
        logger.warning('the client is not connected to live server instance')
