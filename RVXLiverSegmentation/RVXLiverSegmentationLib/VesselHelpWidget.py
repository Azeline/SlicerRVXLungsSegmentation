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
        return f"<img src='{self.getHelpImagePath(veinType)}' width='750' height='600'>"

    def getHelpImagePath(self, veinType):
        return self._helpDict.get(veinType, self._default)

    def _helpPath(self):
        return resourcesPath().joinpath("RVXVesselsHelp")

    def _portalHelpPathDict(self):
        return {VesselHelpType.Portal: self._helpPath().joinpath("schema_full.png"),
            VeinId.PulmonaryTrunkRoot: self._helpPath().joinpath("schema_pulmonary_trunk_root.png"),
            VeinId.PulmonaryTrunk: self._helpPath().joinpath("schema_pulmonary_trunk.png"),
            VeinId.RightPulmonaryArtery: self._helpPath().joinpath("schema_right_pulmonary_artery.png"),
            VeinId.SuperiorLobarArteryRUL: self._helpPath().joinpath("schema_superior_lobar_artery_rul.png"),
            VeinId.ApicalRUL: self._helpPath().joinpath("schema_apical_rul.png"),
            VeinId.AnteriorRUL: self._helpPath().joinpath("schema_anterior_rul.png"),
            VeinId.PosteriorRUL: self._helpPath().joinpath("schema_posterior_rul.png"),
            VeinId.MiddleLobarArteryRML: self._helpPath().joinpath("schema_middle_lobar_artery_rml.png"),
            VeinId.MedialRML: self._helpPath().joinpath("schema_medial_rml.png"),
            VeinId.LateralRML: self._helpPath().joinpath("schema_lateral_rml.png"),
            VeinId.InferiorLobarArteryRLL: self._helpPath().joinpath("schema_inferior_lobar_artery_rll.png"),
            VeinId.SuperiorRLL: self._helpPath().joinpath("schema_superior_rll.png"),
            VeinId.AnteriorRLL: self._helpPath().joinpath("schema_anterior_rll.png"),
            VeinId.LateralRLL: self._helpPath().joinpath("schema_lateral_rll.png"),
            VeinId.MedialRLL: self._helpPath().joinpath("schema_medial_rll.png"),
            VeinId.PosteriorRLL: self._helpPath().joinpath("schema_posterior_rll.png"),
            VeinId.LeftPulmonaryArtery: self._helpPath().joinpath("schema_left_pulmonary_artery.png"),
            VeinId.SuperiorLobarArteryLUL: self._helpPath().joinpath("schema_superior_lobar_artery_lul.png"),
            VeinId.ApicalLUL: self._helpPath().joinpath("schema_apical_lul.png"),
            VeinId.AnteriorLUL: self._helpPath().joinpath("schema_anterior_lul.png"),
            VeinId.PosteriorLUL: self._helpPath().joinpath("schema_posterior_lul.png"),
            VeinId.LingularArteryLML: self._helpPath().joinpath("schema_lingular_artery_lml.png"),
            VeinId.InferiorLingulaLML: self._helpPath().joinpath("schema_inferior_lingula_lml.png"),
            VeinId.SuperiorLingulaLML: self._helpPath().joinpath("schema_superior_lingula_lml.png"),
            VeinId.InferiorLobarArteryLLL: self._helpPath().joinpath("schema_inferior_lobar_artery_lll.png"),
            VeinId.SuperiorLLL: self._helpPath().joinpath("schema_superior_lll.png"),
            VeinId.AnteriorLLL: self._helpPath().joinpath("schema_anterior_lll.png"),
            VeinId.LateralLLL: self._helpPath().joinpath("schema_lateral_lll.png"),
            VeinId.MedialLLL: self._helpPath().joinpath("schema_medial_lll.png"),
            VeinId.PosteriorLLL: self._helpPath().joinpath("schema_posterior_lll.png")}

    def _ivcHelpPathDict(self):
        dico = {id: self._helpPath().joinpath("vessels_schema_portal_veins.png") for id in VeinId.sortedIds(VeinId)}
        dico[VesselHelpType.IVC] = self._helpPath().joinpath("vessels_schema_portal_veins.png")
        return dico
