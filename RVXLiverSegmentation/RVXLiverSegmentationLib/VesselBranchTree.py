import qt
import slicer
import vtk

from RVXLiverSegmentationLib import Signal, PlaceStatus, VesselBranchWizard, removeNodeFromMRMLScene, InteractionStatus, \
  VesselTreeColumnRole, VesselHelpWidget
from .RVXLiverSegmentationUtils import Icons, getMarkupIdPositionDictionary, createMultipleMarkupFiducial, createButton


class VesselBranchTreeItem(qt.QTreeWidgetItem):
  """Helper class holding nodeId and nodeName in the VesselBranchTree
  """

  def __init__(self, nodeId, status=PlaceStatus.NOT_PLACED):
    qt.QTreeWidgetItem.__init__(self)
    self.nodeId = nodeId
    self.setIcon(VesselTreeColumnRole.DELETE, Icons.delete)
    self._status = status
    self.setFlags(self.flags() | qt.Qt.ItemIsEditable)
    self.updateText()

  @property
  def status(self):
    return self._status

  @status.setter
  def status(self, status):
    self._status = status
    self.updateText()

  def updateText(self):
    suffixMap = {PlaceStatus.NOT_PLACED: "<click here to start placing node>", PlaceStatus.PLACING: "*placing*"}

    suffix = suffixMap.get(self._status, None)
    self.setText(0, "{} {}".format(self.nodeId, suffix) if suffix is not None else self.nodeId)

class VesselBranchTree(qt.QTreeWidget):
  """Tree representation of vessel branch nodes.

  Class enables inserting new vessel node branches after or before existing nodes.
  Class signals when modified or user interacts with the UI.
  """

  def __init__(self, vesselHelpWidget, parent=None):
    qt.QTreeWidget.__init__(self, parent)

    self.keyPressed = Signal("VesselBranchTreeItem, qt.Qt.Key")
    self.setContextMenuPolicy(qt.Qt.CustomContextMenu)
    self.customContextMenuRequested.connect(self.onContextMenu)
    self.editing_node = False
    self.itemChanged.connect(self.onItemChange)
    self.itemRenamed = Signal(str, str)
    self.itemDropped = Signal()
    self.itemDeleted = Signal("VesselBranchTreeItem")

    self._branchDict = {}
    self._vesselHelpWidget = vesselHelpWidget

    # Configure tree widget
    self.setColumnCount(2)
    self.setHeaderLabels(["Branch Node Name", "", ""])

    # Configure tree to have first section stretched and last sections to be at right of the layout
    # other columns will always be at minimum size fitting the icons
    self.header().setSectionResizeMode(0, qt.QHeaderView.Stretch)
    self.header().setStretchLastSection(False)
    self.header().setSectionResizeMode(1, qt.QHeaderView.ResizeToContents)
    self.header().setSectionResizeMode(2, qt.QHeaderView.ResizeToContents)
    self.headerItem().setIcon(VesselTreeColumnRole.DELETE, Icons.delete)

    # Enable reordering by drag and drop
    self.setDragEnabled(True)
    self.setDropIndicatorShown(True)
    self.setDragDropMode(qt.QAbstractItemView.InternalMove)

  def mouseDoubleClickEvent(self, event):
    # Prevent the default double-click editing behavior
    event.ignore()

  def clear(self):
    self._branchDict = {}
    qt.QTreeWidget.clear(self)

  def clickItem(self, item):
    item = self.getTreeWidgetItem(item) if isinstance(item, str) else item
    self.setItemSelected(item)
    if item is not None:
      self.itemClicked.emit(item, 0)

  def setItemSelected(self, item):
    if item is not None:
      self.selectionModel().clearSelection()
      item.setSelected(True)

  def getNextUnplacedItem(self, nodeId):
    """
    Returns
    -------
    VesselBranchTreeItem or None
      Next vessel branch tree which has not been placed yet in the scene
    """
    item = self.getTreeWidgetItem(nodeId)
    if item is None:
      return None

    if item.status == PlaceStatus.NOT_PLACED:
      return item

    nextItem = self._getNextItem(nodeId)
    return self.getNextUnplacedItem(nextItem.nodeId) if nextItem is not None else None

  def isInTree(self, nodeId):
    """
    Parameters
    ----------
    nodeId: str
      Id of the node which may ne in the tree.

    Returns
    -------
    bool
      True if nodeId is part of the tree, False otherwise.
    """
    return nodeId in self._branchDict.keys()

  def isRoot(self, nodeId):
    """
    :return: True if node doesn't have any parents
    """
    return self.getParentNodeId(nodeId) is None

  def dropEvent(self, event):
    """On drop event, enforce structure of the tree is not broken.
    """
    qt.QTreeWidget.dropEvent(self, event)
    self.enforceOneRoot()
    self.itemDropped.emit()

  def keyPressEvent(self, event):
    """Overridden from qt.QTreeWidget to notify listeners of key event

    Parameters
    ----------
    event: qt.QKeyEvent
    """
    if self.currentItem():
      self.keyPressed.emit(self.currentItem(), event.key())

    qt.QTreeWidget.keyPressEvent(self, event)

  def onContextMenu(self, position):
    # Cannot display context menu while editing
    if PlaceStatus.PLACING in [node.status for node in self._branchDict.values()]:
      return

    displayAction = qt.QAction("Display Selection")
    displayAction.triggered.connect(self.displaySelection)

    renameAction = qt.QAction("Rename")
    renameAction.triggered.connect(self.renameItem)

    deleteAction = qt.QAction("Delete")
    deleteAction.triggered.connect(lambda :self.itemDeleted.emit(self.currentItem()))

    addChildAction = qt.QAction("Add child")
    addChildAction.triggered.connect(lambda: self._addNode(parent_node=self.currentItem().nodeId))

    menu = qt.QMenu(self)
    menu.addAction(displayAction)
    menu.addAction(renameAction)
    menu.addAction(deleteAction)
    menu.addAction(addChildAction)

    menu.exec_(self.mapToGlobal(position))

  def onItemChange(self, item, column):
    if self.editing_node:
      self.editing_node = False
      previous = item.nodeId
      new = item.text(0)

      # Forbid renaming with existing name
      if self.isInTree(new):
        item.updateText()
        return

      self._branchDict[item.text(0)] = self._branchDict.pop(item.nodeId)
      item.nodeId = item.text(0)
      item.updateText()
      self.itemRenamed.emit(previous, new)

  def displaySelection(self):
    column = self.currentColumn()
    text = self.currentItem().text(0)
    print(f"right-clicked item is {text}")
    print(f"type : {type(self.currentItem())}")

  def renameItem(self):
    item: VesselBranchTreeItem = self.currentItem()
    self.editing_node = True
    self.editItem(item, 0)

  def _takeItem(self, nodeId):
    """Remove item with given item id from the tree. Removes it from its parent if necessary
    """
    if nodeId is None:
      return None
    elif nodeId in self._branchDict:
      nodeItem = self._branchDict[nodeId]
      self._removeFromParent(nodeItem)
      return nodeItem
    else:
      return VesselBranchTreeItem(nodeId)

  def _addNode(self, parent_node=False):
    new_node_idx = len(self._branchDict)
    new_node = f"n{new_node_idx}"
    while self.isInTree(new_node):
      new_node_idx += 1
      new_node = f"n{new_node_idx}"
    if parent_node is False:
      if len(self._branchDict) == 1:
        parent_node = list(self.getNodeList())[0]
      elif len(self._branchDict) > 1:
        parent_node = self.getTreeParentList()[-1][0]
    self._insertNode(new_node, parent_node, PlaceStatus.NOT_PLACED)

  def _removeFromParent(self, nodeItem):
    """Remove input node item from its parent if it is attached to an item or from the TreeWidget if at the root
    """
    parent = nodeItem.parent()
    if parent is not None:
      parent.removeChild(nodeItem)
    else:
      self.takeTopLevelItem(self.indexOfTopLevelItem(nodeItem))

  def _insertNode(self, nodeId, parentId, status):
    """Insert the nodeId with input node name as child of the item whose name is parentId. If parentId is None, the item
    will be added as a root of the tree

    Parameters
    ----------
    nodeId: str
      Unique id of the node to add to the tree
    parentId: str or None
      Unique id of the parent node. If None or "" will add node as root
    """
    nodeItem = self._takeItem(nodeId)
    nodeItem.status = status
    if not parentId:
      hasRoot = self.topLevelItemCount > 0
      self.addTopLevelItem(nodeItem)
      if hasRoot:
        rootItem = self.takeTopLevelItem(0)
        nodeItem.addChild(rootItem)
    else:
      self._branchDict[parentId].addChild(nodeItem)

    self._branchDict[nodeId] = nodeItem
    return nodeItem

  def insertAfterNode(self, nodeId, parentNodeId, status=PlaceStatus.NOT_PLACED):
    """Insert given node after the input parent Id. Inserts new node as root if parentNodeId is None.
    If root is already present in the tree and insert after None is used, new node will become the parent of existing
    root node.

    Parameters
    ----------
    nodeId: str
      Unique ID of the node to insert in the tree
    parentNodeId: str or None
      Unique ID of the parent node. If None, new node will be inserted as root.
    status: PlaceStatus

    Raises
    ------
      ValueError
        If parentNodeId is not None and doesn't exist in the tree
    """
    node = self._insertNode(nodeId, parentNodeId, status)
    node.setToolTip(0, self._vesselHelpWidget.tooltipImageUrl(nodeId))
    self.expandAll()

  def removeNode(self, nodeId):
    """Remove given node from tree.

    If node is root, only remove if it has exactly one direct child and replace root by child. Else does nothing.
    If intermediate item, move each child of node to node parent.

    Parameters
    ----------
    nodeId: str
      Id of the node to remove from tree

    Returns
    -------
    bool - True if node was removed, False otherwise
    """
    nodeItem = self._branchDict[nodeId]
    if nodeItem.parent() is None:
      return False
    else:
      self._removeIntermediateItem(nodeItem, nodeId)
      return True

  def _removeIntermediateItem(self, nodeItem, nodeId):
    """Move each child of node to node parent and remove item.
    """
    parentItem = nodeItem.parent()
    parentItem.takeChild(parentItem.indexOfChild(nodeItem))
    for child in nodeItem.takeChildren():
      parentItem.addChild(child)
    del self._branchDict[nodeId]

  def getParentNodeId(self, childNodeId):
    """

    Parameters
    ----------
    childNodeId: str
      Node for which we want the parent id

    Returns
    -------
    str or None
      Id of the parent item or None if node has no parent
    """
    parentItem = self._branchDict[childNodeId].parent()
    return parentItem.nodeId if parentItem is not None else None

  def getChildrenNodeId(self, parentNodeId):
    """
    Returns
    -------
    List[str]
      List of nodeIds of every children associated with parentNodeId
    """
    parent = self._branchDict[parentNodeId]
    return [parent.child(i).nodeId for i in range(parent.childCount())]

  def _getSiblingId(self, nodeId, nextIncrement):
    """
    Returns
    -------
    str or None
      nodeId sibling at iNode + nextIncrement index. None if new index is out of bounds
    """
    nodeItem = self._branchDict[nodeId]
    parent = nodeItem.parent()
    if parent is None:
      return None
    else:
      iSibling = parent.indexOfChild(nodeItem) + nextIncrement
      return parent.child(iSibling).nodeId if (0 <= iSibling < parent.childCount()) else None

  def _getNextItem(self, nodeId, lookInChildren=True):
    """
    Parameters
    ----------
      nodeId: str
        Id of start element
      lookInChildren: bool
        if True, will look for next in the node's children if any, else will look for next in siblings or parents

    Returns
    -------
    Optional[VesselBranchTreeItem] next node item
    """
    nodeItem = self.getTreeWidgetItem(nodeId)
    if nodeItem is None:
      return None

    if lookInChildren and nodeItem.childCount() > 0:
      return nodeItem.child(0)

    nextSiblingId = self._getSiblingId(nodeId, 1)
    if nextSiblingId is not None:
      return self.getTreeWidgetItem(nextSiblingId)

    parent = nodeItem.parent()
    return self._getNextItem(parent.nodeId, lookInChildren=False) if parent is not None else None

  def getNextSiblingNodeId(self, nodeId):
    """
    Returns
    -------
    str or None
      nodeId sibling at iNode + 1 index. None if new index is out of bounds
    """
    return self._getSiblingId(nodeId, nextIncrement=1)

  def getPreviousSiblingNodeId(self, nodeId):
    """
    Returns
    -------
    str or None
      nodeId sibling at iNode - 1 index. None if new index is out of bounds
    """
    return self._getSiblingId(nodeId, nextIncrement=-1)

  def getRootNodeId(self):
    """
    Returns
    -------
    str or None
      nodeId of the first root of the tree. None if tree has no root item
    """
    return self.topLevelItem(0).nodeId if self.topLevelItemCount > 0 else None

  def getTreeParentList(self):
    """Returns tree as adjacent list in the format [[parentId, childId_1], [parentId, childId_2], ...].
    Root adjacent list is listed as [None, RootId]. List is constructed in breadth first manner from root to leaf.

    Returns
    -------
    List[List[str]] Representing adjacent list of the tree. List is empty if tree is emtpy.
    """
    roots = [self.topLevelItem(i) for i in range(self.topLevelItemCount)]
    treeParentList = [[None, root.nodeId] for root in roots]
    for root in roots:
      treeParentList += self._getChildrenAdjacentLists(root)

    return treeParentList

  def getPlacedNodeList(self):
    """
    Returns
    -------
    List[str]
      List of nodeIds which have been placed in the mrmlScene
    """
    return [nodeId for nodeId in self.getNodeList() if self._isPlaced(nodeId)]

  def areAllNodesPlaced(self):
    return all([self._isPlaced(nodeId) for nodeId in self.getNodeList()])

  def _isPlaced(self, nodeId):
    return self.getTreeWidgetItem(nodeId).status == PlaceStatus.PLACED

  def getNodeList(self):
    """
    Returns
    -------
    List[str]
      List of every nodeIds referenced in the tree
    """
    return self._branchDict.keys()

  def getTreeWidgetItem(self, nodeId):
    return self._branchDict[nodeId] if nodeId in self._branchDict else None

  def getText(self, nodeId):
    item = self.getTreeWidgetItem(nodeId)
    return item.text(0) if item is not None else ""

  def isLeaf(self, nodeId):
    """
    Returns
    -------
    bool
      True if nodeId has no children item, False otherwise
    """
    return len(self.getChildrenNodeId(nodeId)) == 0

  def _getChildrenAdjacentLists(self, nodeItem):
    """
    Returns
    -------
    List[List[str]]
      List of every [parentId, childId] pair starting from nodeItem in the tree.
    """
    children = [nodeItem.child(i) for i in range(nodeItem.childCount())]
    nodeList = [[nodeItem.nodeId, child.nodeId] for child in children]
    for child in children:
      nodeList += self._getChildrenAdjacentLists(child)
    return nodeList

  def enforceOneRoot(self):
    """Reorders tree to have only one root item. If elements are defined after root, they will be inserted before
    current root. Methods is called during drop events.
    """
    # Early return if tree has at most one root
    if self.topLevelItemCount <= 1:
      return

    # Set current root as second item child
    newRoot = self.takeTopLevelItem(1)
    currentRoot = self.takeTopLevelItem(0)
    newRoot.addChild(currentRoot)

    # Add the new root to the tree
    self.insertTopLevelItem(0, newRoot)

    # Expand both items
    newRoot.setExpanded(True)
    currentRoot.setExpanded(True)

    # Call recursively until the whole tree has only one root
    self.enforceOneRoot()


class TreeDrawer(object):
  """
  Class responsible for drawing lines between the different vessel nodes
  """

  def __init__(self, vesselTree, markupFiducial):
    """
    Parameters
    ----------
    vesselTree: VesselBranchTree
    markupFiducial: vtkMRMLMarkupsFiducialNode
    """
    self._tree = vesselTree
    self._markupFiducial = markupFiducial
    self._lineWidth = 4
    self._lineOpacity = 1
    self._setupLineModel()

  def _setupLineModel(self):
    self._polyLine = vtk.vtkPolyLineSource()
    self._polyLine.SetClosed(False)
    self._lineModel = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode")
    self._lineModel.SetAndObservePolyData(self._polyLine.GetOutput())
    self._lineModel.CreateDefaultDisplayNodes()
    self._lineModel.SetName("VesselBranchNodeTree")
    self._updateNodeCoordDict()

    self.setColor(qt.QColor("red"))
    self.setLineWidth(self._lineWidth)
    self.setOpacity(self._lineOpacity)

  def _updateNodeCoordDict(self):
    """Update node coordinates associated with node ID for the current tree

    Returns
    -------
    Dict[str, List[float]]
      Dictionary containing the node ids contained in the markup node and its associated positions
    """
    self._nodeCoordDict = getMarkupIdPositionDictionary(self._markupFiducial)

  def updateTreeLines(self):
    """Updates the lines between the different nodes of the tree. Uses the last set line width and color
    """
    # Update nodes coordinates
    self._updateNodeCoordDict()

    # Force modification by resetting number of points to 0 (other wise update will not be visible if only points
    # position has changed)
    self._polyLine.SetNumberOfPoints(0)
    coordList = self._extractTreeLinePointSequence()
    self._polyLine.SetNumberOfPoints(len(coordList))
    for i, coord in enumerate(coordList):
      self._polyLine.SetPoint(i, *coord)

    # Trigger poly line update
    self._polyLine.Update()

  def _extractTreeLinePointSequence(self, parentId=None):
    """Constructs a coordinate sequence starting from parentId node recursively.

    example :
    parent
      |_ child
            |_ sub child
      |_ child2

    Previous tree will generate coordinates : [parent, child, sub child, child, parent, child2, parent]
    This coordinate construction enables using only one poly line instead of multiple lines at the expense of
    constructed lines number

    Parameters
    ----------
    parentId: str or None
      Starting point of the recursion. If none, will start from tree root

    Returns
    -------
    List[List[float]]
      Coordinate sequence for polyLine construction
    """
    if parentId is None:
      parentId = self._tree.getRootNodeId()

    # Early return if tree is empty
    if not parentId:
      return []

    parentCoord = self._nodeCoordinate(parentId)
    pointSeq = [parentCoord]
    for childId in self._tree.getChildrenNodeId(parentId):
      pointSeq += self._extractTreeLinePointSequence(childId)
      pointSeq.append(parentCoord)
    return [point for point in pointSeq if point is not None]

  def _nodeCoordinate(self, nodeId):
    return self._nodeCoordDict[nodeId] if nodeId in self._nodeCoordDict else None

  def setColor(self, lineColor):
    """
    Parameters
    ----------
    lineColor: qt.QColor
      New color for line. Call updateTreeLines to apply to tree.
    """
    self._lineDisplayNode().SetColor(lineColor.red(), lineColor.green(), lineColor.blue())

  def setLineWidth(self, lineWidth):
    """
    Parameters
    ----------
    lineWidth: float
      New line width for lines of the tree.  Call updateTreeLines to apply to tree.
    """
    self._lineDisplayNode().SetLineWidth(lineWidth)
    self._lineWidth = lineWidth

  def getLineWidth(self):
    """
    :return: Current line width
    """
    return self._lineDisplayNode().GetLineWidth()

  def setOpacity(self, opacity):
    """
    :param opacity: float - Opacity of the lines
    """
    self._lineDisplayNode().SetOpacity(opacity)
    self._lineOpacity = opacity

  def getOpacity(self):
    """
    :return: Current opacity of the lines
    """
    return self._lineDisplayNode().GetOpacity()

  def setVisible(self, isVisible):
    """
    Parameters
    ----------
    isVisible: bool
      If true, will show tree in mrmlScene. Else will hide tree model
    """
    self._lineModel.SetDisplayVisibility(isVisible)

  def _lineDisplayNode(self):
    return self._lineModel.GetDisplayNode()

  def clear(self):
    removeNodeFromMRMLScene(self._lineModel)
    self._setupLineModel()


class MarkupNode(object):
  """
  Wrapper around slicer markup Node to define a single interface for signals slots and access to the fiducial points.
  """

  def __init__(self, slicerNode):
    """
    Parameters
    ----------
    slicerNode: slicer.vtkMRMLMarkupsFiducialNode
    """
    # Instance signals
    self.pointAdded = Signal()
    self.pointClicked = Signal("int pointId")
    self.pointInteractionEnded = Signal("int pointId")
    self.pointModified = Signal("int pointId")

    self._node = slicerNode

    # Handle API change between Slicer 4.10 and 4.11
    if hasattr(slicer.vtkMRMLMarkupsNode, 'MarkupAddedEvent'):
      pointAddedEvent = slicer.vtkMRMLMarkupsNode.MarkupAddedEvent
      pointClickedEvent = slicer.vtkMRMLMarkupsNode.PointClickedEvent
    else:
      pointAddedEvent = slicer.vtkMRMLMarkupsNode.PointPositionDefinedEvent
      pointClickedEvent = slicer.vtkMRMLMarkupsNode.PointEndInteractionEvent

    # Connect markup events as signals
    self._nodeObsId = []
    self._connectNodeSignal(pointAddedEvent, self._emitPointAdded)
    self._connectNodeSignal(pointClickedEvent, self._emitPointClicked)
    self._connectNodeSignal(slicer.vtkMRMLMarkupsNode.PointEndInteractionEvent, self._emitPointInteractionEnded)
    self._connectNodeSignal(slicer.vtkMRMLMarkupsNode.PointModifiedEvent, self._emitPointModified)

    # Forward slicer markup functions
    self.GetNumberOfControlPoints = self._node.GetNumberOfControlPoints
    self.AddControlPoint = self._node.AddControlPoint
    self.GetNthControlPointLabel = self._node.GetNthControlPointLabel
    self.GetNthControlPointPosition = self._node.GetNthControlPointPosition
    self.GetNthFiducialVisibility = self._node.GetNthFiducialVisibility
    self.SetNthControlPointVisibility = self._node.SetNthControlPointVisibility
    self.SetNthControlPointLabel = self._node.SetNthControlPointLabel
    self.SetName = self._node.SetName
    self.SetLocked = self._node.SetLocked
    self.GetLocked = self._node.GetLocked
    self.GetDisplayNode = self._node.GetDisplayNode
    self.RemoveAllControlPoints = self._node.RemoveAllControlPoints
    self.RemoveNthControlPoint = self._node.RemoveNthControlPoint

  def GetSlicerNode(self):
    return self._node

  def GetLastFiducialId(self):
    return max(0, self.GetNumberOfControlPoints() - 1)

  def GetNodeLabelList(self):
    return [self.GetNthControlPointLabel(i) for i in range(self.GetNumberOfControlPoints())]

  def __del__(self):
    for obsId in self._nodeObsId:
      self._node.RemoveObserver(obsId)

  def _connectNodeSignal(self, signal, slot):
    self._nodeObsId.append(self._node.AddObserver(signal, slot))

  def _emitPointAdded(self, *args):
    self.pointAdded.emit()

  def _emitPointClicked(self, caller, callData):
    self.pointClicked.emit(callData)

  def _emitPointInteractionEnded(self, caller, callData):
    self.pointInteractionEnded.emit(callData)

  def _emitPointModified(self, caller, callData):
    self.pointModified.emit(callData)



class INodePlaceWidget(object):
  """
  Interface class for used place widget functionality. Defines a signal enabling notifying when the place mode is
  changed and simplifies the interface for the place widget
  """

  def __init__(self):
    self.placeModeChanged = Signal()

  def setPlaceModeEnabled(self, isEnabled):
    pass

  @property
  def placeModeEnabled(self):
    return False


class SlicerNodePlaceWidget(INodePlaceWidget):
  """
  Node place widget wrapping place mode widget of a markup node selector.
  Adds observer on interaction modifications to notify when place mode is cancelled.
  Notifies when place mode is changed through this interface
  """

  def __init__(self, placeWidget):
    super(SlicerNodePlaceWidget, self).__init__()
    self._placeWidget = placeWidget
    self._previousPlaceMode = self.placeModeEnabled

    interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
    if interactionNode is not None:
      interactionNode.AddObserver(vtk.vtkCommand.ModifiedEvent, lambda *x: self._notifyIfPlaceModeChanged())

  def _notifyIfPlaceModeChanged(self):
    if self.placeModeEnabled != self._previousPlaceMode:
      self._previousPlaceMode = self.placeModeEnabled
      self.placeModeChanged.emit()

  def setPlaceModeEnabled(self, isEnabled):
    self._placeWidget.setPlaceModeEnabled(isEnabled)
    self._notifyIfPlaceModeChanged()

  @property
  def placeModeEnabled(self):
    return self._placeWidget.placeModeEnabled

class VesselBranchWidget(qt.QWidget):
  """Class holding the widgets for vessel branch node edition.

  Creates the node edition buttons, branch node tree and starts and connects the branch markup node.
  """

  def __init__(self, setupBranchF, vesselHelpWidget, parent=None):
    """
    Parameters
    ----------
    setupBranchF: Callable[]
    parent: Optional[qt.QWidget]
    """
    qt.QWidget.__init__(self, parent)

    # Create Markups node
    self._createVesselsBranchMarkupNode()

    # Create branch tree
    self._branchTree = VesselBranchTree(vesselHelpWidget)

    # Create tree drawer
    self._treeDrawer = TreeDrawer(self._branchTree, self._markupNode)

    # Create interaction wizard
    self._wizard = VesselBranchWizard(self._branchTree, self._markupNode, self._markupPlaceWidget, self._treeDrawer,
                                      setupBranchF)
    self._wizard.interactionChanged.connect(self._updateButtonCheckedStatus)

    # Create layout for the widget
    widgetLayout = qt.QVBoxLayout()
    widgetLayout.addLayout(self._createButtonLayout())
    widgetLayout.addWidget(self._branchTree)
    self.setLayout(widgetLayout)

    # Create interaction action
    self._stopInteractionAction = self._createStopInteractionAction()

    # Emitted when validity changes
    self.treeValidityChanged = Signal()
    self._wizard.placingFinished.connect(self.treeValidityChanged.emit)

    # Emitted when node id is changed in wizard
    self.currentNodeIdChanged = Signal()
    self._wizard.currentNodeIdChanged.connect(self.currentNodeIdChanged.emit)

  def enableShortcuts(self, isEnabled):
    """Enables/Disables the shortcuts for the widget. If enabled, add node and edit node can be disabled by pressing
    escape key.
    """
    if isEnabled:
      slicer.util.mainWindow().addAction(self._stopInteractionAction)
    else:
      slicer.util.mainWindow().removeAction(self._stopInteractionAction)

  def _createStopInteractionAction(self):
    """
    Returns
    -------
    QAction
      When triggered, action will stop add node and edit node interactions
    """
    action = qt.QAction("Stop branch interaction", self)
    action.connect("triggered()", self._wizard.onStopInteraction)
    action.setShortcut(qt.QKeySequence("esc"))
    return action

  def _createVesselsBranchMarkupNode(self):
    """Creates markup node and node selector and connect the interaction node modified event to node status update.
    """
    self._markupNode = MarkupNode(slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode"))
    self._markupNode.SetName("node")

    # Markup node selector will not be shown sor tooltip and markup names are unnecessary
    self._markupNodeSelector = createMultipleMarkupFiducial(toolTip="", markupName="")
    self._markupPlaceWidget = SlicerNodePlaceWidget(self._markupNodeSelector.markupsPlaceWidget())

  def _createButtonLayout(self):
    """Create layout with Extract vessels, Add Node button and an Edit Node button

    Returns
    -------
    QLayout
    """

    # Create add and edit layout
    addEditButtonLayout = qt.QHBoxLayout()
    self._unlockNodePositionsButton = createButton("Unlock Node Positions", self._wizard.onEditNode, isCheckable=True)
    addEditButtonLayout.addWidget(self._unlockNodePositionsButton)

    # Create vertical layout and add Add and edit buttons on top of extract button
    buttonLayout = qt.QVBoxLayout()
    buttonLayout.addLayout(addEditButtonLayout)
    self._clearTreeButton = createButton("Clear Tree", lambda : (self._branchTree.clear(), self._treeDrawer.clear(), self._markupNode.RemoveAllControlPoints()))
    buttonLayout.addWidget(self._clearTreeButton)
    self._addNodeButton = createButton("Add Node", self._branchTree._addNode)
    buttonLayout.addWidget(self._addNodeButton)
    self.extractVesselsButton = createButton("Extract Vessels from node tree")
    buttonLayout.addWidget(self.extractVesselsButton)
    return buttonLayout

  def _updateButtonCheckedStatus(self):
    interaction = self._wizard.getInteractionStatus()
    self._unlockNodePositionsButton.setChecked(interaction == InteractionStatus.EDIT)

  def getBranchTree(self):
    return self._branchTree

  def getBranchNames(self):
    """
    :return: Standardized branch names present in the tree. If some branches have been removed from the tree, they are
      not present in the returned list.
    """
    return self._wizard.getVesselBranches()

  def getBranchMarkupNode(self):
    return self._markupNode.GetSlicerNode()

  def setVisibleInScene(self, isVisible):
    """
    If isVisible, markups and tree will be shown in scene, else they will be hidden.
    This method will disable placement mode for the widget
    """

    self._wizard.setVisibleInScene(isVisible)
    if isVisible:
      self._markupNodeSelector.markupsSelectorComboBox().setCurrentNode(self._markupNode.GetSlicerNode())

    self._markupPlaceWidget.setPlaceModeEnabled(False)

  def stopInteraction(self):
    self._wizard.onStopInteraction()

  def isVesselTreeValid(self):
    return self._wizard.isPlacingFinished()

  def getVesselWizard(self):
    return self._wizard

  def getMarkupDisplayNode(self):
    return self._markupNode.GetDisplayNode()

  def getTreeDrawer(self):
    return self._treeDrawer

  def clear(self):
    self._wizard.clear()
