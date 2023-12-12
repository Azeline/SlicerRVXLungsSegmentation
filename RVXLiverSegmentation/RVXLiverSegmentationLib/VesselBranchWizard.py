import qt

from RVXLiverSegmentationLib import Signal, jumpSlicesToNthMarkupPosition


class VeinId(object):
    PulmonaryTrunkRoot = "Pulmonary Trunk Root"
    PulmonaryTrunk = "Pulmonary Trunk"
    RightPulmonaryArtery = "Right Pulmonary Artery"
    SuperiorLobarArteryRUL = "Superior Lobar Artery RUL"
    ApicalRUL = "Apical RUL"
    AnteriorRUL = "Anterior RUL"
    PosteriorRUL = "Posterior RUL"
    MiddleLobarArteryRML = "Middle Lobar Artery RML"
    MedialRML = "Medial RML"
    LateralRML = "Lateral RML"
    InferiorLobarArteryRLL = "Inferior Lobar Artery RLL"
    SuperiorRLL = "Superior RLL"
    AnteriorRLL = "Anterior RLL"
    LateralRLL = "Lateral RLL"
    MedialRLL = "Medial RLL"
    PosteriorRLL = "Posterior RLL"
    LeftPulmonaryArtery = "Left Pulmonary Artery"
    SuperiorLobarArteryLUL = "Superior Lobar Artery LUL"
    ApicalLUL = "Apical LUL"
    AnteriorLUL = "Anterior LUL"
    PosteriorLUL = "Posterior LUL"
    LingularArteryLML = "Lingular Artery LML"
    InferiorLingulaLML = "Inferior Lingula LML"
    SuperiorLingulaLML = "Superior Lingula LML"
    InferiorLobarArteryLLL = "Inferior Lobar Artery LLL"
    SuperiorLLL = "Superior LLL"
    AnteriorLLL = "Anterior LLL"
    LateralLLL = "Lateral LLL"
    MedialLLL = "Medial LLL"
    PosteriorLLL = "Posterior LLL"

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
    branches = [(VeinId.PulmonaryTrunkRoot, None),
                (VeinId.PulmonaryTrunk, VeinId.PulmonaryTrunkRoot),
                # Right lung
                (VeinId.RightPulmonaryArtery, VeinId.PulmonaryTrunk),

                (VeinId.SuperiorLobarArteryRUL, VeinId.RightPulmonaryArtery),
                (VeinId.ApicalRUL, VeinId.SuperiorLobarArteryRUL),
                (VeinId.AnteriorRUL, VeinId.SuperiorLobarArteryRUL),
                (VeinId.PosteriorRUL, VeinId.SuperiorLobarArteryRUL),

                (VeinId.MiddleLobarArteryRML, VeinId.RightPulmonaryArtery),
                (VeinId.MedialRML, VeinId.MiddleLobarArteryRML),
                (VeinId.LateralRML, VeinId.MiddleLobarArteryRML),

                (VeinId.InferiorLobarArteryRLL, VeinId.MiddleLobarArteryRML),
                (VeinId.SuperiorRLL, VeinId.InferiorLobarArteryRLL),
                (VeinId.AnteriorRLL, VeinId.InferiorLobarArteryRLL),
                (VeinId.LateralRLL, VeinId.InferiorLobarArteryRLL),
                (VeinId.MedialRLL, VeinId.InferiorLobarArteryRLL),
                (VeinId.PosteriorRLL, VeinId.InferiorLobarArteryRLL),
                # Left lung
                (VeinId.LeftPulmonaryArtery, VeinId.PulmonaryTrunk),

                (VeinId.SuperiorLobarArteryLUL, VeinId.LeftPulmonaryArtery),
                (VeinId.ApicalLUL, VeinId.SuperiorLobarArteryLUL),
                (VeinId.AnteriorLUL, VeinId.SuperiorLobarArteryLUL),
                (VeinId.PosteriorLUL, VeinId.SuperiorLobarArteryLUL),

                (VeinId.LingularArteryLML, VeinId.LeftPulmonaryArtery),
                (VeinId.InferiorLingulaLML, VeinId.LingularArteryLML),
                (VeinId.SuperiorLingulaLML, VeinId.LingularArteryLML),

                (VeinId.InferiorLobarArteryLLL, VeinId.LeftPulmonaryArtery),
                (VeinId.SuperiorLLL, VeinId.InferiorLobarArteryLLL),
                (VeinId.AnteriorLLL, VeinId.InferiorLobarArteryLLL),
                (VeinId.LateralLLL, VeinId.InferiorLobarArteryLLL),
                (VeinId.MedialLLL, VeinId.InferiorLobarArteryLLL),
                (VeinId.PosteriorLLL, VeinId.InferiorLobarArteryLLL),
                ]

    for child, parent in branches:
        tree.insertAfterNode(nodeId=child, parentNodeId=parent)


def setup_inferior_cava_vein_default_branch(tree):
    branches = [(VeinId.PulmonaryTrunk, None),
                (VeinId.RightPulmonaryArtery, VeinId.PulmonaryTrunk),

                (VeinId.SuperiorLobarArteryRUL, VeinId.RightPulmonaryArtery),
                (VeinId.ApicalRUL, VeinId.SuperiorLobarArteryRUL),
                (VeinId.AnteriorRUL, VeinId.SuperiorLobarArteryRUL),
                (VeinId.PosteriorRUL, VeinId.SuperiorLobarArteryRUL),

                (VeinId.MiddleLobarArteryRML, VeinId.SuperiorLobarArteryRUL),
                (VeinId.MedialRML, VeinId.MiddleLobarArteryRML),
                (VeinId.LateralRML, VeinId.MiddleLobarArteryRML),

                (VeinId.InferiorLobarArteryRLL, VeinId.MiddleLobarArteryRML),
                (VeinId.SuperiorRLL, VeinId.InferiorLobarArteryRLL),
                (VeinId.AnteriorRLL, VeinId.InferiorLobarArteryRLL),
                (VeinId.LateralRLL, VeinId.InferiorLobarArteryRLL),
                (VeinId.MedialRLL, VeinId.InferiorLobarArteryRLL),
                (VeinId.PosteriorRLL, VeinId.InferiorLobarArteryRLL),
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
        self._tree.itemRenamed.connect(self.onItemRenamed)
        self._tree.itemDeleted.connect(self._onDeleteItem)
        self._tree.sceneItemDeleted.connect(self._onDeleteSceneItem)
        self._tree.itemReplaced.connect(self._onReplaceItem)
        self._tree.itemRedraw.connect(self._onRedraw)
        self._tree.keyPressed.connect(self.onKeyPressed)
        self._tree.itemDropped.connect(lambda: self._treeDrawer.updateTreeLines())
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
        self._tree.lastaction = "place"
        self._tree.removedNode = treeItem
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

    def onItemRenamed(self, previous, new):
        nodeList = self._node.GetNodeLabelList()
        try:
            idx = nodeList.index(previous)
            self._node.SetNthControlPointLabel(idx, new)
            self._treeDrawer.updateTreeLines()
        except ValueError:
            pass

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

    def _onDeleteSceneItem(self, treeItem):
        """
    Remove the item from the scene only and set the node to unplaced
    """
        self.onStopInteraction()
        nodeList = self._node.GetNodeLabelList()
        nodeId = treeItem.nodeId

        # Delete node in the scene if it has been place
        if nodeId in nodeList:
            self._node.RemoveNthControlPoint(nodeList.index(nodeId))
            self.updateNodeVisibility()

        treeItem.status = PlaceStatus.NOT_PLACED
        self._placeWidget.setPlaceModeEnabled(False)
        self._updateCurrentInteraction(InteractionStatus.NOT_PLACED)

    def _onDeleteItem(self, treeItem):
        """
    Remove the item from the tree and hide the associated markup
    """
        self.onStopInteraction()
        nodeList = self._node.GetNodeLabelList()
        nodeId = treeItem.nodeId
        remove_worked = self._tree.removeNode(nodeId)

        # Delete node in the scene if it has been place
        if remove_worked and nodeId in nodeList:
            self.lastnode = nodeList.index(nodeId)
            self._node.RemoveNthControlPoint(nodeList.index(nodeId))
            self.updateNodeVisibility()

        if self._currentTreeItem == treeItem:
            self._currentTreeItem = None
        self._updatePlacingFinished()


    def _onRedraw(self, treeItem):
        self._treeDrawer.updateTreeLines()

    def _onReplaceItem(self, treeItem, column):
        """
    Replace the deleted item back in the scene
    """


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
