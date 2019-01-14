import logging
import wdr

(
    AdminApp, AdminConfig, AdminControl, AdminTask, Help
) = wdr.WsadminObjects().getObjects()

logger = logging.getLogger('wdr.bla')


def listBLAs():
    return AdminTask.listBLAs().splitlines()

def listAssets():
    return AdminTask.listAssets().splitlines()

class BlaAction:
    def __init__(self):
        self._options = {}

    def listCompUnits(self):
        return AdminTask.listCompUnits(self.name).splitlines()

class CompUnitAction:
    def __init__(self):
        self._options = {}

    def __getattr__(self, name):
        if name == '__methods__':
            return {}
        elif name == '__members__':
            return self._options.keys()
        else:
            if name[0] == '-':
                name = name[1:]
            if not self._options.has_key(name):
                self._options[name] = None
            return self._options[name]

    def __getitem__(self, item):
        return self.__getattr__(item)

    def __setattr__(self, name, value):
        if name == '_options':
            self.__dict__[name] = value
            return value
        else:
            self._options[name] = value
            return value

    def __setitem__(self, item, value):
        return self.__setattr__(item, value)

    def __delitem__(self, name):
        del self._options[name]
        return None

    def __delattr__(self, name):
        del self._options[name]
        return None

    def getOptions(self):
        options = []
        for (k, v) in self._options.items():
            options.append('-%s' % k)
            if v is not None:
                options.append(v)
        return options


class CreateBLA(BlaAction):
    def __init__(self):
        BlaAction.__init__(self)

    def __call__(self, name, description):
        logger.debug(
            'creating empty BLA %s with description %s', name, description
        )
        AdminTask.createEmptyBLA(name, description)


class DeleteBLA(BlaAction):
    def __init__(self):
        BlaAction.__init__(self)

    def __call__(self, name):
        logger.debug('deleting BLA %s', name)
        AdminTask.deleteBLA(name)


class AddCompUnit(CompUnitAction):
    def __init__(self):
        CompUnitAction.__init__(self)

    def __call__(self, name):
        options = self.getOptions()
        logger.debug('updating application %s with options %s', name, options)
        AdminTask.update(name, 'app', ['-operation', 'update'] + options)


