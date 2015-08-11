import logging
import wdr

(
    AdminApp, AdminConfig, AdminControl, AdminTask, Help
) = wdr.WsadminObjects().getObjects()

logger = logging.getLogger('wdr.app')


def listApplications():
    return AdminApp.list().splitlines()


class AppAction:
    def __init__(self):
        self._options = {}

    def listModules(self):
        return AdminApp.listModules(self.name).splitlines()

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


class Install(AppAction):
    def __init__(self):
        AppAction.__init__(self)

    def __call__(self, earFile):
        options = self.getOptions()
        logger.debug(
            'installing application %s with options %s', earFile, options
        )
        AdminApp.install(earFile, options)


class Uninstall(AppAction):
    def __init__(self):
        AppAction.__init__(self)

    def __call__(self, name):
        logger.debug('uninstalling application %s', name)
        AdminApp.uninstall(name)


class UpdateApp(AppAction):
    def __init__(self):
        AppAction.__init__(self)

    def __call__(self, name):
        options = self.getOptions()
        logger.debug('updating application %s with options %s', name, options)
        AdminApp.update(name, 'app', ['-operation', 'update'] + options)


class UpdateFile(AppAction):
    def __init__(self):
        AppAction.__init__(self)

    def __call__(self, name):
        options = self.getOptions()
        logger.debug(
            'file updating application %s with options %s', name, options
        )
        AdminApp.update(name, 'file', options)


class UpdateModulefile(AppAction):
    def __init__(self):
        AppAction.__init__(self)

    def __call__(self, name):
        options = self.getOptions()
        logger.debug(
            'file updating application %s with options %s', name, options
        )
        AdminApp.update(name, 'file', options)


class UpdatePartialapp(AppAction):
    def __init__(self):
        AppAction.__init__(self)

    def __call__(self, name):
        options = self.getOptions()
        logger.debug(
            'partial updating application %s with options %s', name, options
        )
        AdminApp.update(name, 'partial', options)


class Edit(AppAction):
    def __init__(self):
        AppAction.__init__(self)

    def __call__(self, name):
        options = self.getOptions()
        logger.debug('editing application %s with options %s', name, options)
        AdminApp.update(name, options)


class View(AppAction):
    def __init__(self):
        AppAction.__init__(self)

    def __call__(self, name):
        options = self.getOptions()
        if len(options):
            logger.debug(
                'viewing application %s with options %s', name, options
            )
            return AdminApp.view(name, options)
        else:
            logger.debug('viewing application %s', name)
            return AdminApp.view(name)
