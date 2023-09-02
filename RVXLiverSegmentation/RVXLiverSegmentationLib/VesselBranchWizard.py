import qt

from RVXLiverSegmentationLib import Signal, jumpSlicesToNthMarkupPosition


class VeinId(object):
    BaseTroncPulmonaire = "Base Tronc Pulmonaire"
    TroncPulmonaire = "Tronc Pulmonaire"
    ArterePulmonaireDroite = "Artère Pulmonaire Droite"
    ArtereLobaireSuperieurePD = "Artère Lobaire Supérieure PD"
    ArtereSegmentereApicaleA1PD = "Artère Segmentère Apicale A1 PD"
    ArtereSegmentaireAnterieureA2PD = "Artère Segmentaire Antérieure A2 PD"
    ArtereSegmentairePosterieureA3PD = "Artère Segmentaire Postérieure A3 PD"
    ArtereLobaireMoyennePD = "Artère Lobaire Moyenne PD"
    ArteresegmentairemedialeA4PD = "Artère segmentaire médiale A4 PD"
    ArtereSegmentaireLateraleA5PD = "Artère Segmentaire Latérale A5 PD"
    ArtereLobaireInferieurePD = "Artère Lobaire Inférieure PD"
    ArtereSegmentaireSuperieureA6PD = "Artère Segmentaire Supérieure A6 PD"
    ArtereSegmentairebasaleAnterieureA7PD = "Artère Segmentaire basale Antérieure A7 PD"
    ArtereSegmentairebasaleLateraleA8PD = "Artère Segmentaire basale Latérale A8 PD"
    ArtereSegmentairebasaleMedialeA9PD = "Artère Segmentaire basale Médiale A9 PD"
    ArtereSegmentairebasalePosterieureA10PD = "Artère Segmentaire basale Postérieure A10 PD"
    ArterePulmonaireGauche = "Artère Pulmonaire Gauche"
    ArtereLobaireSuperieurePG = "Artère Lobaire Supérieure PG"
    ArtereSegmentaireApicaleA1PG = "Artère Segmentaire Apicale A1 PG"
    ArtereSegmentaireAnterieureA2PG = "Artère Segmentaire Antérieure A2 PG"
    ArtereSegmentairePosterieureA3PG = "Artère Segmentaire Postérieure A3 PG"
    ArtereLingulairePG = "Artère Lingulaire PG"
    ArtereLingulaireInferieureA4PG = "Artère Lingulaire Inférieure A4 PG"
    ArtereLingulaireSuperieureA5PG = "Artère Lingulaire Supérieure A5 PG"
    ArtereLobaireInferieurePG = "Artère Lobaire Inférieure PG"
    ArtereSegmentaireSuperieureA6PG = "Artère Segmentaire Supérieure A6 PG"
    ArtereSegmentairebasaleAnterieureA7PG = "Artère Segmentaire basale Antérieure A7 PG"
    ArtereSegmentairebasaleLateraleA8PG = "Artère Segmentaire basale Latérale A8 PG"
    ArtereSegmentairebasaleMedialeA9PG = "Artère Segmentaire basale Médiale A9 PG"
    ArtereSegmentairebasalePosterieureA10PG = "Artère Segmentaire basale Postérieure A10 PG"

    def sortedIds(self):
        return [v for k, v in VeinId.__dict__.items() if not k.startswith("__")]


class NodeBranches(object):
    """
  Container class for branch names and start and end point coordinates.
  Used for extraction
  """

    def __init__(self):
        self._branchNames = []
        self._startPoints = []
        self._endPoints = []

    def addBranch(self, branchName):
        self._branchNames.append(branchName)

    def addEndPoint(self, endPoint):
        self._endPoints.append(endPoint)

    def addStartPoint(self, startPoint):
        self._startPoints.append(startPoint)

    def names(self):
        return self._branchNames

    def startPoints(self):
        return self._startPoints

    def endPoints(self):
        return self._endPoints


class InteractionStatus(object):
    STOPPED = "Stopped"
    INSERT_BEFORE = "Insert Before Node"
    EDIT = "Edit"
    PLACING = "Placing"


def setup_portal_vein_default_branch(tree):
    branches = [(VeinId.BaseTroncPulmonaire, None),
                (VeinId.TroncPulmonaire, VeinId.BaseTroncPulmonaire),
                # Right lung
                (VeinId.ArterePulmonaireDroite, VeinId.TroncPulmonaire),

                (VeinId.ArtereLobaireSuperieurePD, VeinId.ArterePulmonaireDroite),
                (VeinId.ArtereSegmentereApicaleA1PD, VeinId.ArtereLobaireSuperieurePD),
                (VeinId.ArtereSegmentaireAnterieureA2PD, VeinId.ArtereLobaireSuperieurePD),
                (VeinId.ArtereSegmentairePosterieureA3PD, VeinId.ArtereLobaireSuperieurePD),

                (VeinId.ArtereLobaireMoyennePD, VeinId.ArtereLobaireSuperieurePD),
                (VeinId.ArteresegmentairemedialeA4PD, VeinId.ArtereLobaireMoyennePD),
                (VeinId.ArtereSegmentaireLateraleA5PD, VeinId.ArtereLobaireMoyennePD),

                (VeinId.ArtereLobaireInferieurePD, VeinId.ArtereLobaireMoyennePD),
                (VeinId.ArtereSegmentaireSuperieureA6PD, VeinId.ArtereLobaireInferieurePD),
                (VeinId.ArtereSegmentairebasaleAnterieureA7PD, VeinId.ArtereLobaireInferieurePD),
                (VeinId.ArtereSegmentairebasaleLateraleA8PD, VeinId.ArtereLobaireInferieurePD),
                (VeinId.ArtereSegmentairebasaleMedialeA9PD, VeinId.ArtereLobaireInferieurePD),
                (VeinId.ArtereSegmentairebasalePosterieureA10PD, VeinId.ArtereLobaireInferieurePD),
                # Left lung
                (VeinId.ArterePulmonaireGauche, VeinId.TroncPulmonaire),

                (VeinId.ArtereLobaireSuperieurePG, VeinId.ArterePulmonaireGauche),
                (VeinId.ArtereSegmentaireApicaleA1PG, VeinId.ArtereLobaireSuperieurePG),
                (VeinId.ArtereSegmentaireAnterieureA2PG, VeinId.ArtereLobaireSuperieurePG),
                (VeinId.ArtereSegmentairePosterieureA3PG, VeinId.ArtereLobaireSuperieurePG),

                (VeinId.ArtereLingulairePG, VeinId.ArtereLobaireSuperieurePG),
                (VeinId.ArtereLingulaireInferieureA4PG, VeinId.ArtereLingulairePG),
                (VeinId.ArtereLingulaireSuperieureA5PG, VeinId.ArtereLingulairePG),

                (VeinId.ArtereLobaireInferieurePG, VeinId.ArtereLingulairePG),
                (VeinId.ArtereSegmentaireSuperieureA6PG, VeinId.ArtereLobaireInferieurePG),
                (VeinId.ArtereSegmentairebasaleAnterieureA7PG, VeinId.ArtereLobaireInferieurePG),
                (VeinId.ArtereSegmentairebasaleLateraleA8PG, VeinId.ArtereLobaireInferieurePG),
                (VeinId.ArtereSegmentairebasaleMedialeA9PG, VeinId.ArtereLobaireInferieurePG),
                (VeinId.ArtereSegmentairebasalePosterieureA10PG, VeinId.ArtereLobaireInferieurePG),
                ]

    for child, parent in branches:
        tree.insertAfterNode(nodeId=child, parentNodeId=parent)


def setup_inferior_cava_vein_default_branch(tree):
    branches = [(VeinId.TroncPulmonaire, None),
                (VeinId.ArterePulmonaireDroite, VeinId.TroncPulmonaire),

                (VeinId.ArtereLobaireSuperieurePD, VeinId.ArterePulmonaireDroite),
                (VeinId.ArtereSegmentereApicaleA1PD, VeinId.ArtereLobaireSuperieurePD),
                (VeinId.ArtereSegmentaireAnterieureA2PD, VeinId.ArtereLobaireSuperieurePD),
                (VeinId.ArtereSegmentairePosterieureA3PD, VeinId.ArtereLobaireSuperieurePD),

                (VeinId.ArtereLobaireMoyennePD, VeinId.ArtereLobaireSuperieurePD),
                (VeinId.ArteresegmentairemedialeA4PD, VeinId.ArtereLobaireMoyennePD),
                (VeinId.ArtereSegmentaireLateraleA5PD, VeinId.ArtereLobaireMoyennePD),

                (VeinId.ArtereLobaireInferieurePD, VeinId.ArtereLobaireMoyennePD),
                (VeinId.ArtereSegmentaireSuperieureA6PD, VeinId.ArtereLobaireInferieurePD),
                (VeinId.ArtereSegmentairebasaleAnterieureA7PD, VeinId.ArtereLobaireInferieurePD),
                (VeinId.ArtereSegmentairebasaleLateraleA8PD, VeinId.ArtereLobaireInferieurePD),
                (VeinId.ArtereSegmentairebasaleMedialeA9PD, VeinId.ArtereLobaireInferieurePD),
                (VeinId.ArtereSegmentairebasalePosterieureA10PD, VeinId.ArtereLobaireInferieurePD),
                ]

    for child, parent in branches:
        tree.insertAfterNode(nodeId=child, parentNodeId=parent)


class VesselBranchWizard(object):
    """
  Object responsible for handling interaction with the branch tree and the markup in the 3D and 2D views.
  Triggers slicer move to markup and selects the current parent node when markups are clicked with or without key
  modifiers
  """

    def __init__(self, tree, markupNode, nodePlaceWidget, treeDrawer, setupDefaultBranchF):
        """
    Parameters
    ----------
    tree: VesselBranchTree.VesselBranchTree
    markupNode: MarkupNode
    nodePlaceWidget: INodePlaceWidget
    treeDrawer: TreeDrawer
    setupDefaultBranchF: Callable[]
    """
        self._tree = tree
        self._node = markupNode
        self._node.SetLocked(True)
        self._setupDefaultBranchF = setupDefaultBranchF
        self._setupDefaultBranchNodes()
        self._placeWidget = nodePlaceWidget
        self._currentTreeItem = None
        self._treeDrawer = treeDrawer

        self._tree.connect("itemClicked(QTreeWidgetItem *, int)", self.onItemClicked)
        self._tree.connect("currentItemChanged(QTreeWidgetItem *), QTreeWidgetItem *)",
                           lambda current, previous: self.onItemClicked(current, 0))
        self._tree.keyPressed.connect(self.onKeyPressed)
        self._node.pointAdded.connect(self.onMarkupPointAdded)
        self._node.pointModified.connect(lambda *x: self._treeDrawer.updateTreeLines())
        self._node.pointInteractionEnded.connect(lambda *x: self._treeDrawer.updateTreeLines())
        self._placeWidget.placeModeChanged.connect(self._onNodePlaceModeChanged)

        # Emitted when interaction mode changes
        self._interactionStatus = InteractionStatus.STOPPED
        self.interactionChanged = Signal()

        # Emitted when all nodes have been placed in the wizard
        self._placingFinished = False
        self.placingFinished = Signal()

        # Emitted when current selected node is changed
        self.currentNodeIdChanged = Signal("str")

    def _currentItemPlaceStatus(self):
        """
    :return: Current item place status if it's valid, else PlaceStatus.NONE
    """
        return self._currentTreeItem.status if self._currentTreeItem is not None else PlaceStatus.NONE

    def _onNodePlaceModeChanged(self):
        """
    Disables current wizard placing when markup place widget is disabled from the UI
    """
        if not self._placeWidget.placeModeEnabled:
            self.onStopInteraction()

    def _setupDefaultBranchNodes(self):
        """
    Prepares tree with the different hepatic vessel node names
    """
        self._setupDefaultBranchF(self._tree)
        self._placingFinished = False

    def getInteractionStatus(self):
        return self._interactionStatus

    def onInsertBeforeNode(self):
        """
    If current node and parent node are placed, enables node placing and set node as insert before
    """
        self.onStopInteraction()
        insertEnabled = self._isCurrentNodePlaced() and self._isParentNodePlaced()
        if insertEnabled and self._isCurrentNodePlaced() and self._isParentNodePlaced():
            self._placeWidget.setPlaceModeEnabled(True)
            self._currentTreeItem.status = PlaceStatus.INSERT_BEFORE
            self._updateCurrentInteraction(InteractionStatus.INSERT_BEFORE)
            self._tree.setItemSelected(self._currentTreeItem)

    def _isCurrentNodePlaced(self):
        return self._currentItemPlaceStatus() == PlaceStatus.PLACED

    @staticmethod
    def _isNodeItemPlaced(nodeItem):
        return nodeItem.status == PlaceStatus.PLACED if nodeItem is not None else False

    def _isParentNodePlaced(self):
        parentId = self._tree.getParentNodeId(self._currentTreeItem.nodeId)
        return self._isNodeItemPlaced(self._tree.getTreeWidgetItem(parentId)) if parentId is not None else False

    def onEditNode(self, editEnabled):
        self.onStopInteraction()

        if editEnabled:
            self._node.SetLocked(False)
            self._updateCurrentInteraction(InteractionStatus.EDIT)

    def onStartPlacing(self):
        if self._currentItemPlaceStatus() == PlaceStatus.NOT_PLACED:
            self.onStopInteraction()
            self._currentTreeItem.status = PlaceStatus.PLACING
            self._placeWidget.setPlaceModeEnabled(True)
            self._updateCurrentInteraction(InteractionStatus.PLACING)

    def onStopInteraction(self):
        self._deactivatePreviousItem()
        self._placeWidget.setPlaceModeEnabled(False)
        self._node.SetLocked(True)
        self._updateCurrentInteraction(InteractionStatus.STOPPED)

    def _deactivatePreviousItem(self):
        if self._currentItemPlaceStatus() == PlaceStatus.PLACING:
            self._currentTreeItem.status = PlaceStatus.NOT_PLACED
        elif self._currentItemPlaceStatus() == PlaceStatus.INSERT_BEFORE:
            self._currentTreeItem.status = PlaceStatus.PLACED

    def onItemClicked(self, treeItem, column):
        """
    On item clicked, start placing item if necessary.
    Delete item if delete column was selected
    """
        self._deactivatePreviousItem()

        self._currentTreeItem = treeItem
        if column == VesselTreeColumnRole.DELETE:
            self._onDeleteItem(treeItem)
        elif column == VesselTreeColumnRole.INSERT_BEFORE:
            self.onInsertBeforeNode()
        elif treeItem.status == PlaceStatus.NOT_PLACED:
            self.onStartPlacing()
        elif self._interactionStatus == InteractionStatus.PLACING and treeItem.status == PlaceStatus.PLACED:
            self.onStopInteraction()

        self._jumpSlicesToCurrentNode()
        self._treeDrawer.updateTreeLines()

    def _jumpSlicesToCurrentNode(self):
        """
    Center all slices to input node position
    """
        if self._isCurrentNodePlaced():
            jumpSlicesToNthMarkupPosition(self._node, self._nodeIndex(self._currentTreeItem.nodeId))

    def _nodeIndex(self, nodeId):
        """
    Parameters
    ----------
    nodeId: str
      Id of the node for which we want the index in the vessel branch node

    Returns
    -------
    int or None
      Markup index associated with id if found else None
    """
        for i in range(self._node.GetNumberOfControlPoints()):
            if self._node.GetNthControlPointLabel(i) == nodeId:
                return i
        return None

    def _updateCurrentInteraction(self, interaction):
        if self._interactionStatus != interaction:
            self._interactionStatus = interaction
            self.interactionChanged.emit()
            self._emitNewNodeId()

    def onKeyPressed(self, treeItem, key):
        """
    On delete key pressed, delete the current item if any selected
    """
        if key == qt.Qt.Key_Delete:
            self._onDeleteItem(treeItem)

    def _onDeleteItem(self, treeItem):
        """
    Remove the item from the tree and hide the associated markup
    """
        self.onStopInteraction()
        self._tree.removeNode(treeItem.nodeId)
        self.updateNodeVisibility()
        if self._currentTreeItem == treeItem:
            self._currentTreeItem = None
        self._updatePlacingFinished()

    def updateNodeVisibility(self):
        """
    Hides markup nodes which may have been deleted
    """
        for i in range(self._node.GetNumberOfControlPoints()):
            self._node.SetNthControlPointVisibility(i, self._tree.isInTree(self._node.GetNthControlPointLabel(i)))

        self._treeDrawer.updateTreeLines()

    def onMarkupPointAdded(self):
        """
    On markup added, modify its status to placed and select the next unplaced node in the tree
    """
        if self._currentTreeItem is not None:
            self._currentTreeItem.status = PlaceStatus.PLACED

            if self._interactionStatus == InteractionStatus.PLACING:
                self._placeCurrentNodeAndActivateNext()
            elif self._interactionStatus == InteractionStatus.INSERT_BEFORE:
                self._insertPlacedNodeBeforeCurrent()

        self._treeDrawer.updateTreeLines()
        self._updatePlacingFinished()

    def _placeCurrentNodeAndActivateNext(self):
        self._renamePlacedNode(self._currentTreeItem.nodeId)
        self._currentTreeItem = self._tree.getNextUnplacedItem(self._currentTreeItem.nodeId)
        if self._currentTreeItem is not None:
            self._tree.clickItem(self._currentTreeItem)
        else:
            self._placeWidget.setPlaceModeEnabled(False)
        self._emitNewNodeId()

    def _emitNewNodeId(self):
        self.currentNodeIdChanged.emit(self._currentTreeItem.nodeId if self._currentTreeItem else None)

    def _renamePlacedNode(self, name):
        self._node.SetNthControlPointLabel(self._node.GetLastFiducialId(), name)

    def _insertPlacedNodeBeforeCurrent(self):
        insertedId = self._nextInsertedNodeId(self._currentTreeItem.nodeId)
        self._renamePlacedNode(insertedId)
        self._tree.insertBeforeNode(nodeId=insertedId, beforeNodeId=self._currentTreeItem.nodeId,
                                    status=PlaceStatus.PLACED)
        self._currentTreeItem = self._tree.getTreeWidgetItem(insertedId)
        self.onInsertBeforeNode()

    @staticmethod
    def _nextInsertedNodeId(nodeId):
        """
    :type nodeId: str
    :return: new node ID with base inputNodeId followed by _nodeIndex
    """
        if nodeId in VeinId().sortedIds():
            return "{}_0".format(nodeId)

        nameParts = nodeId.split("_")
        i_node = int(nameParts[-1]) + 1 if len(nameParts) > 1 else 0
        return "{}_{}".format("_".join(nameParts[:-1]), i_node)

    def setVisibleInScene(self, isVisible):
        """
    Show or hide the tree and the nodes in the scene
    """
        self._treeDrawer.setVisible(isVisible)

        for i in range(self._node.GetNumberOfControlPoints()):
            isNodeVisible = isVisible and self._tree.isInTree(self._node.GetNthControlPointLabel(i))
            self._node.SetNthControlPointVisibility(i, isNodeVisible)

    def _updatePlacingFinished(self):
        """
    Emit placing finished when placing is done the first time.
    """
        if not self._placingFinished:
            self._placingFinished = self._tree.areAllNodesPlaced()
            if self._placingFinished:
                self.placingFinished.emit()

    def isPlacingFinished(self):
        return self._placingFinished

    def getVesselBranches(self):
        """
    :return: List of all the default branches present in the tree as well as their start and end positions
    """
        treeBranches = NodeBranches()

        for nodeId in VeinId().sortedIds():
            if nodeId in self._tree.getNodeList():
                nodePosition = self._getNodePosition(nodeId)
                treeBranches.addBranch(nodeId)
                if self._tree.isRoot(nodeId):
                    treeBranches.addStartPoint(nodePosition)
                elif self._tree.isLeaf(nodeId):
                    treeBranches.addEndPoint(nodePosition)

        return treeBranches

    def _getNodePosition(self, nodeId):
        for i in range(self._node.GetNumberOfControlPoints()):
            if self._node.GetNthControlPointLabel(i) == nodeId:
                position = [0] * 3
                self._node.GetNthControlPointPosition(i, position)
                return position

        return None

    def clear(self):
        self._tree.clear()
        self._treeDrawer.clear()
        self._node.RemoveAllControlPoints()
        self._setupDefaultBranchNodes()


class PlaceStatus(object):
    NOT_PLACED = 0
    PLACING = 1
    PLACED = 2
    INSERT_BEFORE = 3
    NONE = 4


class VesselTreeColumnRole(object):
    NODE_ID = 0
    INSERT_BEFORE = 1
    DELETE = 2
