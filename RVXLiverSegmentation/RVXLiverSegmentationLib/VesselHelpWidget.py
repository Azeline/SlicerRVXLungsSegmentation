from enum import Enum, auto, unique

from RVXLiverSegmentationLib import resourcesPath, VeinId
from qt import QToolTip, QCursor


@unique
class VesselHelpType(Enum):
    Portal = auto()
    IVC = auto()


class VesselHelpWidget:
    def __init__(self, helpType):
        self._lastVeinType = None
        self._helpDict = self._portalHelpPathDict() if helpType == VesselHelpType.Portal else self._ivcHelpPathDict()
        self._default = self._helpDict[helpType]
        self._helpImagePath = self.getHelpImagePath(None)

    def updateHelp(self, veinType):
        self._lastVeinType = veinType

    def showHelp(self):
        QToolTip.showText(QCursor.pos(), self.tooltipImageUrl(self._lastVeinType))

    def tooltipImageUrl(self, veinType):
        return f"<img src='{self.getHelpImagePath(veinType)}' width='600' height='600'>"

    def getHelpImagePath(self, veinType):
        return self._helpDict.get(veinType, self._default)

    def _helpPath(self):
        return resourcesPath().joinpath("RVXVesselsHelp")

    def _portalHelpPathDict(self):
        dico = {id: self._helpPath().joinpath("vessels_schema_portal_veins.png") for id in VeinId.sortedIds(VeinId)}
        dico[VesselHelpType.Portal] = self._helpPath().joinpath("vessels_schema_portal_veins.png")
        return dico

    def _ivcHelpPathDict(self):
        dico = {id: self._helpPath().joinpath("vessels_schema_portal_veins.png") for id in VeinId.sortedIds(VeinId)}
        dico[VesselHelpType.IVC] = self._helpPath().joinpath("vessels_schema_portal_veins.png")
        return dico
