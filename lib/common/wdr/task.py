import logging
import re
import wdr


(
    AdminApp, AdminConfig, AdminControl, AdminTask, Help
) = wdr.WsadminObjects().getObjects()

logger = logging.getLogger('wdr.task')

_listPattern = re.compile(r'\[(.*)\]')
_itemPattern = re.compile(
    r'(?<=\[)'
    r'(?P<key>\S+)'
    r'\s+'
    r'(?:'
    + (
        r''
        + r'\[(?P<valueQuoted>[^\]]+)\]'
        + r'|'
        + r'(?P<valueNotQuoted>[^ \[\]]+)'
    ) +
    r')'
)


def adminTaskAsDict(adminTaskList):
    result = {}
    for (key, valueQuoted, valueNotQuoted) in _itemPattern.findall(
        adminTaskList
    ):
        result[key] = valueQuoted or valueNotQuoted
    return result


def adminTaskAsDictList(adminTaskListOfLists):
    result = []
    for l in adminTaskListOfLists.splitlines():
        listMatcher = _listPattern.match(l)
        if listMatcher:
            result.append(adminTaskAsDict(listMatcher.group(1)))
    return result


def adminTaskAsListOfLists(adminTaskList):
    result = []
    for (key, valueQuoted, valueNotQuoted) in _itemPattern.findall(
        adminTaskList
    ):
        result.append([key, valueQuoted or valueNotQuoted])
    return result


def adminTaskAsListOfListsList(adminTaskListOfLists):
    result = []
    for l in adminTaskListOfLists.splitlines():
        listMatcher = _listPattern.match(l)
        if listMatcher:
            result.append(adminTaskAsListOfLists(listMatcher.group(1)))
    return result
