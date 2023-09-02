import os
import unittest

import qt
import slicer
from slicer.ScriptedLoadableModule import *

from RVXLiverSegmentationLib import RVXLiverSegmentationLogic, Settings, DataWidget, addInCollapsibleLayout, \
  SegmentWidget, ArteriesWidget, IVCVesselWidget, ArteriesEditWidget, IVCVesselEditWidget, createButton, \
  resourcesPath
from RVXLiverSegmentationTest import RVXLiverSegmentationTestCase, VesselBranchTreeTestCase, \
  ExtractVesselStrategyTestCase, VesselBranchWizardTestCase, VesselSegmentEditWidgetTestCase


class RVXLiverSegmentation(ScriptedLoadableModule):
  def __init__(self, parent=None):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "RVX Liver Segmentation"
    self.parent.categories = ["Segmentation"]
    self.parent.dependencies = []
    self.parent.contributors = [
      "Lucie Macron - Kitware SAS",
      "Thibault Pelletier - Kitware SAS",
      "Camille Huet - Kitware SAS",
      "Leo Sanchez - Kitware SAS"
    ]
    self.parent.helpText = "Liver and hepatic vessels segmentation plugin.<br><br>This plugin aims at easing the " \
                           "segmentation of liver, liver vessels and liver tumor from DICOM data for annotation " \
                           "purposes. The exported segmentations will then be used in research.<br><br>" \
                           "To test the plugin, please use the 3D_IRCAD_B_5_Liver in the SampleData module."

    self.parent.acknowledgementText = "This plugin was initially developed during the RVesselX research project. " \
                                      "For mor details, please visit : https://anr.fr/Projet-ANR-18-CE45-0018<br><br>" \
                                      "The sample data is extracted from the 3D-IRCADb (3D Image Reconstruction for " \
                                      "Comparison of Algorithm Database) database.<br>" \
                                      "The content of 3D-IRCADb is subject to a CC Attribution-Non commercial-No " \
                                      "Derivative Works 3.0 licence.<br><br>For more information on the IRCAD " \
                                      "dataset, please visit : https://www.ircad.fr/research/3dircadb/"

    # Register sample data when the plugin has Slicer has finished loading
    slicer.app.connect("startupCompleted()", registerSampleData)


def registerSampleData():
    """
    Add 3D IRCAD data to the sample to test the LiverSegmentation module.
    """
    import SampleData
    iconsPath = resourcesPath().joinpath('Icons')

    SampleData.SampleDataLogic.registerCustomSampleDataSource(
        category="Chest",
        sampleName='3D_IRCAD_B_5_Liver',
        uris='https://github.com/R-Vessel-X/SlicerRVXLiverSegmentation/releases/download/SampleData/3Dircadb1.5.nii.gz',
        fileNames='3Dircadb1.5.nii.gz',
        nodeNames='3D_IRCAD_B_5_Liver',
        thumbnailFileName=os.path.join(iconsPath, '3D_IRCAD_B_5_Liver.png'),
        loadFileType='VolumeFile',
        checksums='SHA256:e88c68a7280368aa93969de4d49efc2bc7b2537c0a962b05164a3ffbe6ffdebc')


class RVXLiverSegmentationWidget(ScriptedLoadableModuleWidget):
  """Class responsible for the UI of the RVesselX project.

  For more information on the R-Vessel-X project, please visit :
  https://anr.fr/Projet-ANR-18-CE45-0018

  Module is composed of 4 tabs :
    Data Tab : Responsible for loading DICOM data in Slicer
    Liver Tab : Responsible for Liver segmentation
    Vessel Tab : Responsible for vessel segmentation
    Tumor Tab : Responsible for tumor segmentation
  """
  enableReloadOnSceneClear = True

  def __init__(self, parent=None):
    ScriptedLoadableModuleWidget.__init__(self, parent)

    self.logic = None
    self._tabWidget = None
    self._dataTab = None
    self._arteriesTab = None
    self._arteriesEditTab = None

    self._tabList = []
    self._obs = slicer.mrmlScene.AddObserver(slicer.mrmlScene.EndCloseEvent, lambda *x: self.reloadModule())

  def setTestingMode(self, isTesting):
    for tab in self._tabList:
      tab.setTestingMode(isTesting)

  def cleanup(self):
    """Cleanup called before reloading module. Removes mrmlScene observer to avoid multiple setup of the module
    """
    slicer.mrmlScene.RemoveObserver(self._obs)
    ScriptedLoadableModuleWidget.cleanup(self)

  def reloadModule(self):
    """Reload module only if reloading is enabled (ie : not when testing module).

    Implementation closely resembles super class onReload method but without verbosity and with enabling handled.
    """
    if RVXLiverSegmentationWidget.enableReloadOnSceneClear:
      slicer.util.reloadScriptedModule(self.moduleName)

  def _configureLayout(self):
    # Define layout #
    layoutDescription = """
             <layout type=\"horizontal\" split=\"true\" >
               <item splitSize=\"500\">
                 <view class=\"vtkMRMLSliceNode\" singletontag=\"Red\">
                 <property name=\"orientation\" action=\"default\">Axial</property>
                 <property name=\"viewlabel\" action=\"default\">R</property>
                 <property name=\"viewcolor\" action=\"default\">#F34A33</property>
                 </view>
               </item>
               <item splitSize=\"500\">
                 <view class=\"vtkMRMLViewNode\" singletontag=\"1\">
                 <property name=\"viewlabel\" action=\"default\">1</property>
                 </view>
               </item>
             </layout>
           """

    layoutNode = slicer.util.getNode('*LayoutNode*')
    if layoutNode.IsLayoutDescription(layoutNode.SlicerLayoutUserView):
      layoutNode.SetLayoutDescription(layoutNode.SlicerLayoutUserView, layoutDescription)
    else:
      layoutNode.AddLayoutDescription(layoutNode.SlicerLayoutUserView, layoutDescription)
    layoutNode.SetViewArrangement(layoutNode.SlicerLayoutUserView)

    # Add button to layout selector toolbar for this custom layout
    viewToolBar = slicer.util.mainWindow().findChild('QToolBar', 'ViewToolBar')
    layoutMenu = viewToolBar.widgetForAction(viewToolBar.actions()[0]).menu()

    # Add layout button to menu
    rVesselXActionText = "RVesselX 2 Panel View"
    hasRVesselXButton = rVesselXActionText in [action.text for action in layoutMenu.actions()]
    if not hasRVesselXButton:
      layoutSwitchAction = layoutMenu.addAction(rVesselXActionText)
      layoutSwitchAction.setData(layoutNode.SlicerLayoutUserView)
      layoutSwitchAction.setIcon(qt.QIcon(':Icons/LayoutSideBySideView.png'))
      layoutSwitchAction.setToolTip(rVesselXActionText)
      layoutSwitchAction.connect('triggered()',
                                 lambda: slicer.app.layoutManager().setLayout(layoutNode.SlicerLayoutUserView))
      layoutMenu.setActiveAction(layoutSwitchAction)

  @staticmethod
  def areDependenciesSatisfied():
    from RVXLiverSegmentationEffect import PythonDependencyChecker
    # Find extra segment editor effects
    try:
      import SegmentEditorLocalThresholdLib
    except ImportError:
      return False

    return PythonDependencyChecker.areDependenciesSatisfied() and RVXLiverSegmentationLogic.isVmtkFound()

  @staticmethod
  def downloadDependenciesAndRestart():
    from RVXLiverSegmentationEffect import PythonDependencyChecker
    progressDialog = slicer.util.createProgressDialog(maximum=0)
    extensionManager = slicer.app.extensionsManagerModel()

    def downloadWithMetaData(extName):
      # Method for downloading extensions prior to Slicer 5.0.3
      meta_data = extensionManager.retrieveExtensionMetadataByName(extName)
      if meta_data:
        return extensionManager.downloadAndInstallExtension(meta_data["extension_id"])

    def downloadWithName(extName):
      # Direct extension download since Slicer 5.0.3
      return extensionManager.downloadAndInstallExtensionByName(extName)

    # Install Slicer extensions
    downloadF = downloadWithName if hasattr(extensionManager,
                                            "downloadAndInstallExtensionByName") else downloadWithMetaData

    slicerExtensions = ["SlicerVMTK", "MarkupsToModel", "SegmentEditorExtraEffects", "PyTorch"]
    for slicerExt in slicerExtensions:
      progressDialog.labelText = f"Installing the {slicerExt}\nSlicer extension"
      downloadF(slicerExt)

    # Install PIP dependencies
    PythonDependencyChecker.installDependenciesIfNeeded(progressDialog)
    progressDialog.close()

    # Restart if no extension failed to download. Otherwise warn the user about the failure.
    failedDownload = [slicerExt for slicerExt in slicerExtensions if
                      not extensionManager.isExtensionInstalled(slicerExt)]

    if failedDownload:
      failed_ext_list = "\n".join(failedDownload)
      warning_msg = f"The download process failed install the following extensions : {failed_ext_list}" \
                    f"\n\nPlease try to manually install them using Slicer's extension manager"
      qt.QMessageBox.warning(None, "Failed to download extensions", warning_msg)
    else:
      slicer.app.restart()

  def setup(self):
    """Setups widget in Slicer UI.
    """
    ScriptedLoadableModuleWidget.setup(self)

    # Verify Slicer version compatibility
    if not (slicer.app.majorVersion, slicer.app.minorVersion, float(slicer.app.revision)) >= (4, 11, 29738):
      error_msg = "The RVesselX plugin is only compatible from Slicer 4.11 2021.02.26 onwards.\n" \
                  "Please download the latest Slicer version to use this plugin."
      self.layout.addWidget(qt.QLabel(error_msg))
      self.layout.addStretch()
      slicer.util.errorDisplay(error_msg)
      return

    if not self.areDependenciesSatisfied():
      error_msg = "Slicer VMTK, MarkupsToModel, SegmentEditorExtraEffects and MONAI are required by this plugin.\n" \
                  "Please click on the Download button to download and install these dependencies."
      self.layout.addWidget(qt.QLabel(error_msg))
      downloadDependenciesButton = createButton("Download dependencies and restart",
                                                self.downloadDependenciesAndRestart)
      self.layout.addWidget(downloadDependenciesButton)
      self.layout.addStretch()
      return

    # Reset tab list
    self._tabList = []

    # Configure layout and 3D view
    self._configureLayout()
    self._configure3DViewWithMaximumIntensityProjection()

    # Initialize Variables
    self.logic = RVXLiverSegmentationLogic()
    self._dataTab = DataWidget()
    self._arteriesTab = ArteriesWidget(self.logic)

    self._arteriesEditTab = ArteriesEditWidget(self.logic, self._arteriesTab.getVesselWizard())

    # Connect vessels tab to vessels edit tab
    self._arteriesTab.vesselSegmentationChanged.connect(self._arteriesEditTab.onVesselSegmentationChanged)

    # Create tab widget and add it to layout in collapsible layout
    self._tabWidget = qt.QTabWidget()
    self._tabWidget.connect("currentChanged(int)", self._adjustTabSizeToContent)
    self.layout.addWidget(self._tabWidget)

    # Add widgets to tab widget and connect data tab input change to the liver and vessels tab set input methods
    self._addTab(self._dataTab, "Data")
    self._addTab(self._arteriesTab, "Arteries")
    self._addTab(self._arteriesEditTab, "Arteries Edit")
    self._dataTab.addInputNodeChangedCallback(lambda *x: self._clearTabs())
    self._dataTab.addInputNodeChangedCallback(self._arteriesTab.setInputNode)
    self._dataTab.addInputNodeChangedCallback(self._arteriesEditTab.setInputNode)

  def _clearTabs(self):
    """
    Clears all tabs from previous computations
    """
    for tab in self._tabList:
      tab.clear()

  def _configure3DViewWithMaximumIntensityProjection(self):
    """Configures 3D View to render volumes with ray casting maximum intensity projection configuration.
    Background is set to black color.

    This rendering allows to see the vessels and associated segmented areas making it possible to see if parts of the
    volumes have been missed during segmentation.
    """
    # Get 3D view Node
    view = slicer.mrmlScene.GetNodeByID('vtkMRMLViewNode1')

    # Set background color to black
    view.SetBackgroundColor2([0, 0, 0])
    view.SetBackgroundColor([0, 0, 0])

    # Set ray cast technique as maximum intensity projection
    # see https://github.com/Slicer/Slicer/blob/master/Libs/MRML/Core/vtkMRMLViewNode.h
    view.SetRaycastTechnique(2)

  def _addTab(self, tab, tabName):
    """Add input tab to the tab widget and to the tab list.

    Parameters
    ----------
    tab: qt.QWidget
    tabName: str
      Display label of the tab
    """
    self._tabWidget.addTab(tab, tabName)
    self._tabList.append(tab)

  def _adjustTabSizeToContent(self, index):
    """Update current tab size to adjust to its content.

    Parameters
    ----------
    index: int
      Index of new widget to which the tab size will be adjusted
    """
    for i in range(self._tabWidget.count):
      self._tabWidget.widget(i).setSizePolicy(qt.QSizePolicy.Ignored, qt.QSizePolicy.Ignored)

    self._tabWidget.widget(index).setSizePolicy(qt.QSizePolicy.Preferred, qt.QSizePolicy.Preferred)
    self._tabWidget.widget(index).resize(self._tabWidget.widget(index).minimumSizeHint)
    self._tabWidget.widget(index).adjustSize()

  def _setCurrentTab(self, tab_widget):
    # Change tab to new widget
    self._tabWidget.setCurrentWidget(tab_widget)

  def _exportVolumes(self):
    """Export every volume of RVesselX to specified user directory.
    Does nothing if no user directory is selected.
    """
    # Query output directory from user and early return in case of cancel
    selectedDir = qt.QFileDialog.getExistingDirectory(None, "Select export directory", Settings.exportDirectory())

    if not selectedDir:
      return

    # Save user directory in settings
    Settings.setExportDirectory(selectedDir)

    # Export each volume to export to export directory
    for vol in self._volumesToExport():
      vol.exportToDirectory(selectedDir)

    # Save scene as MRB
    slicer.util.saveScene(os.path.join(selectedDir, "Scene.mrb"))
    qt.QMessageBox.information(None, "Export Done", "Exported all results to {}".format(selectedDir))

  def _volumesToExport(self):
    """Creates list of GeometryExporter associated with every element to export (ie Vessels, liver and tumors)

    Returns
    -------
      List[GeometryExporter]
    """
    # Aggregate every volume to export
    volumesToExport = []
    for tab in self._tabList:
      exporters = tab.getGeometryExporters()
      if exporters:
        volumesToExport.extend(exporters)

    # return only not None elements
    return [vol for vol in volumesToExport if vol is not None]

class RVXLiverSegmentationTest(ScriptedLoadableModuleTest):
  def runTest(self):
    # Disable module reloading between tests
    RVXLiverSegmentationWidget.enableReloadOnSceneClear = False
    slicer.modules.RVXLiverSegmentationWidget.setTestingMode(True)

    # Gather tests for the plugin and run them in a test suite
    testCases = [RVXLiverSegmentationTestCase, VesselBranchTreeTestCase, VesselBranchWizardTestCase,
                 ExtractVesselStrategyTestCase, VesselSegmentEditWidgetTestCase]

    suite = unittest.TestSuite([unittest.TestLoader().loadTestsFromTestCase(case) for case in testCases])
    unittest.TextTestRunner(verbosity=3).run(suite)

    # Reactivate module reloading and cleanup slicer scene
    RVXLiverSegmentationWidget.enableReloadOnSceneClear = True
    slicer.modules.RVXLiverSegmentationWidget.setTestingMode(False)
    slicer.mrmlScene.Clear()
