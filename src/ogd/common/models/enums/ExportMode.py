# import standard libraries
from enum import IntEnum

class ExportMode(IntEnum):
    """An enum representing the various modes that can be part of an OGD export.

    These are just the kinds of data that OGD outputs:
    Game Events, Generated (Detector) Events, Features, Models.

    :param IntEnum: _description_
    :type IntEnum: _type_
    :return: _description_
    :rtype: _type_
    """
    EVENTS     = 1
    DETECTORS  = 2
    FEATURES   = 3

    def __str__(self):
        return self.name
