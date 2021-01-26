import sys
import matplotlib
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from matplotlib.pyplot import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from PyQt5 import QtCore
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import (QApplication, QMainWindow, QDockWidget, QVBoxLayout,
                             QHBoxLayout, QGridLayout, QWidget, QPushButton, QDialog,
                             QLabel, QLineEdit, QSizePolicy, QFileDialog, QSpinBox,
                             QCheckBox, QRadioButton, QTextBrowser, QMessageBox, QSpacerItem)


class GasSensorDataAnalysisSystem(QMainWindow):
    def __init__(self):
        """ CONSTRUCTOR: The constructor creates the main variables 
            for the analysis process and settings. It also calls the two
            functions that will build the menu and the main Layout."""

        QMainWindow.__init__(self)
        self.setWindowTitle('Gas Sensor Data Analysis System v0.9')
        self.setGeometry(50, 50, 1200, 600)

        matplotlib.style.use('seaborn')
        matplotlib.use('Qt5Agg')

        #---DATA FRAMES---#
        self.rawDF = pd.DataFrame()
        self.previewDF = pd.DataFrame()
        self.visualizationDF = pd.DataFrame()
        self.normalizationDF = pd.DataFrame()
        self.propertiesDF = pd.DataFrame()
        self.fitDF = pd.DataFrame()
        self.propertiesDF.index.name = 'Concentration'

        #---VARIABLES---#
        self.fileName = ''
        self.concentrationValues = []
        self.separatorList = ['\t', ',', ' ', ';']
        self.separator = ''
        self.responseLabel = u'\u0394R/R0 (%)'

        # used to visualization
        self.startVisualizationTime = ''
        self.endVisualizationTime = ''

        # used to calculate properties
        self.startExposureTime = ''
        self.endExposureTime = ''
        self.endRecoveryTime = ''

        # used in the fitting process
        self.x_fit_values = []
        self.coef1_list = []
        self.coef2_list = []
        self.fitListLabel = []
        self.numberOfFitPoints = 100

        # color settings are based on these lists
        self.colorsList1 = ['black', 'firebrick', 'orange',
                            'olive', 'yellowgreen', 'seagreen', 'skyblue', 'violet']
        self.colorsList2 = ['k', 'b', 'g',
                            'r', 'c', 'm', 'y', 'cyan']
        self.colorsList3 = ['black', 'lightcoral', 'chocolate',
                            'gold', 'limegreen', 'royalblue', 'indigo', 'crimson']

        #---DICTIONARIES---#
        self.responseType = {'dR/R0': True, 'Rgas/Rair': False}
        self.showingChannelsControl = {'ch1': False, 'ch2': False,
                                       'ch3': False, 'ch4': False,
                                       'ch5': False, 'ch6': False,
                                       'ch7': False, 'ch8': False}
        self.plottingControl = {'previewDF': False, 'visualizationDF': False,
                                'normalizationDF': False, 'propertiesDF': False,
                                'fittingDF': False}
        self.colorDic = {'Palette1': self.colorsList1,
                         'Palette2': self.colorsList2,
                         'Palette3': self.colorsList3}
        self.palette = self.colorDic['Palette1']

        self.startMenu()
        self.startMainLayout()

    def startMenu(self):
        """Creates the menu Bar of the QMainWindow"""

        self.mainMenu = self.menuBar()
        self.fileMenu = self.mainMenu.addMenu('File')

        self.settingsAction = self.mainMenu.addAction('Settings')
        self.settingsAction.triggered.connect(self.openSettingsDialog)

        self.aboutAction = self.mainMenu.addAction('About')
        self.aboutAction.triggered.connect(self.showAboutDialog)

        self.exitAction = self.mainMenu.addAction('Exit')
        self.exitAction.triggered.connect(self.close)

        self.openAct = self.fileMenu.addAction('Open')
        self.openAct.triggered.connect(self.openFileDialog)

        self.extAct = self.fileMenu.addAction('Exit')
        self.extAct.triggered.connect(self.close)

    def startMainLayout(self):
        """This function builds the main layout of the Interface:

            The main layout is a plot area that will get all the space
            of the central frame and a dock area that can float around
            but can't be closed.

            cw is the central widget that will hold the main pyplot Figure
            dw is dock widget that will contain the application buttoms"""

        # create centralWidget
        self.cw = QWidget()
        self.setCentralWidget(self.cw)

        # create objects inside the central Frame
        self.mainFigure = Figure(figsize=(5, 4), dpi=100)
        self.mainFigureCanvas = FigureCanvasQTAgg(self.mainFigure)
        self.mainFigureCanvas.setParent(self.cw)
        self.mainFigureCanvas.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.mainFigureToolBar = NavigationToolbar2QT(
            self.mainFigureCanvas,
            self.cw)

        # Create DW and define its features:
        self.dw = QDockWidget()
        self.dw.setFeatures(QDockWidget.DockWidgetFloatable |
                            QDockWidget.DockWidgetMovable)

        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.dw)

        # create the frame that contain the buttons inside
        self.dwWidget = QWidget()
        self.dw.setWidget(self.dwWidget)

        self.visualizationBtn = QPushButton(self.dwWidget)
        self.visualizationBtn.setText('Visualization')
        self.visualizationBtn.setDisabled(True)
        self.visualizationBtn.clicked.connect(self.openVisualizationDialog)

        self.normalizationBtn = QPushButton(self.dwWidget)
        self.normalizationBtn.setText('Normalization')
        self.normalizationBtn.setDisabled(True)
        self.normalizationBtn.clicked.connect(self.openNormalizationDialog)

        self.responseBtn = QPushButton(self.dwWidget)
        self.responseBtn.setText('Response')
        self.responseBtn.setDisabled(True)
        self.responseBtn.clicked.connect(self.openResponseDialog)

        self.fitBtn = QPushButton(self.dwWidget)
        self.fitBtn.setText('PowerLaw Fit')
        self.fitBtn.setDisabled(True)
        self.fitBtn.clicked.connect(self.fitRespData)

        self.exportBtn = QPushButton(self.dwWidget)
        self.exportBtn.setText('Export Data')
        self.exportBtn.setDisabled(True)
        self.exportBtn.clicked.connect(self.openExportDataDialog)

        # create DW layout and management
        self.dwLayout = QVBoxLayout(self.dwWidget)
        self.dwLayout.setSizeConstraint

        self.dwLayout.addWidget(self.visualizationBtn)
        self.dwLayout.addWidget(self.normalizationBtn)
        self.dwLayout.addWidget(self.responseBtn)
        self.dwLayout.addWidget(self.fitBtn)
        self.dwLayout.addWidget(self.exportBtn)
        self.dwLayout.addStretch()

        # create and define mainLayout as a VBox
        self.mainLayout = QVBoxLayout()
        self.cw.setLayout(self.mainLayout)
        self.mainLayout.addWidget(self.mainFigureCanvas)
        self.mainLayout.addWidget(self.mainFigureToolBar)

    def openFileDialog(self):
        """ This function will construct the dialog to open/import data.
            Here, the user has to browse for the file to open,
            define what is the separator used in the data table,
            define the number of channels, being 8 the maximum value.

            Also, there is the possibility of dividing the time or the channel
            columns by a factor, to convert the time/resistance
            to the desired unit"""

        self.importDlg = QDialog()
        self.importDlg.setWindowFlag(
            QtCore.Qt.WindowContextHelpButtonHint, on=False)
        self.importDlg.setWindowTitle('Import data')

        # open file button. This button is connected to the openFileRoutine
        self.openFileBtn = QPushButton(self.importDlg)
        self.openFileBtn.setText('Open CSV File')
        self.openFileBtn.clicked.connect(self.openFileRoutine)
        self.openFileBtn.setSizePolicy(
            QSizePolicy.Maximum, QSizePolicy.Maximum)

        # First line of Main layout
        self.separatorsFrame = QWidget(self.importDlg)
        self.separatorsFrame.setSizePolicy(
            QSizePolicy.Maximum, QSizePolicy.Maximum)

        self.columnSeparatorLbl = QLabel(self.separatorsFrame)
        self.columnSeparatorLbl.setText('Column separator:')

        self.tabSeparatorOpt = QRadioButton(self.separatorsFrame)
        self.tabSeparatorOpt.setText('Tab')
        self.tabSeparatorOpt.setChecked(True)

        self.commaSeparatorOpt = QRadioButton(self.separatorsFrame)
        self.commaSeparatorOpt.setText('Comma')

        self.spaceSeparatorOpt = QRadioButton(self.separatorsFrame)
        self.spaceSeparatorOpt.setText('Space')

        self.semicolonSeparatorOpt = QRadioButton(self.separatorsFrame)
        self.semicolonSeparatorOpt.setText('Semicolon')

        self.separatorsLayout = QGridLayout(self.separatorsFrame)
        self.separatorsLayout.addWidget(self.columnSeparatorLbl, 0, 0, 1, 3)
        self.separatorsLayout.addWidget(self.tabSeparatorOpt, 1, 0, 1, 1)
        self.separatorsLayout.addWidget(self.commaSeparatorOpt, 1, 1, 1, 1)
        self.separatorsLayout.addWidget(self.spaceSeparatorOpt, 1, 2, 1, 1)
        self.separatorsLayout.addWidget(self.semicolonSeparatorOpt, 1, 3, 1, 1)

        # Second line of Main layout
        self.channelFactorsFrame = QWidget(self.importDlg)
        self.channelFactorsFrame.setSizePolicy(
            QSizePolicy.Maximum, QSizePolicy.Maximum)

        self.numberOfChannelsLbl = QLabel(self.channelFactorsFrame)
        self.numberOfChannelsLbl.setText('Number of Channels')

        self.numberOfChannelsSpin = QSpinBox(self.channelFactorsFrame)
        self.numberOfChannelsSpin.setMinimum(1)
        self.numberOfChannelsSpin.setMaximum(8)

        self.divideTimeFactorLbl = QLabel(self.channelFactorsFrame)
        self.divideTimeFactorLbl.setText('Divide time column by:')

        self.timeFactorStr = QLineEdit(self.channelFactorsFrame)
        self.timeFactorStr.setFixedWidth(50)
        self.timeUnitStr = QLineEdit(self.channelFactorsFrame)
        self.timeUnitStr.setPlaceholderText('unit')
        self.timeUnitStr.setFixedWidth(50)

        self.divideChannelsFactorLbl = QLabel(self.channelFactorsFrame)
        self.divideChannelsFactorLbl.setText('Divide channels columns by:')

        self.channelsFactorStr = QLineEdit(self.channelFactorsFrame)
        self.channelsFactorStr.setFixedWidth(50)
        self.channelsUnitStr = QLineEdit(self.channelFactorsFrame)
        self.channelsUnitStr.setPlaceholderText('unit')
        self.channelsUnitStr.setFixedWidth(50)

        self.previewBtn = QPushButton(self.channelFactorsFrame)
        self.previewBtn.setText('Preview')
        self.previewBtn.clicked.connect(self.previewData)

        self.channelFactorsLayout = QGridLayout(self.channelFactorsFrame)
        self.channelFactorsLayout.addWidget(
            self.numberOfChannelsLbl, 0, 0, 1, 1)
        self.channelFactorsLayout.addWidget(
            self.numberOfChannelsSpin, 0, 1, 1, 2)
        self.channelFactorsLayout.addWidget(
            self.divideTimeFactorLbl, 1, 0, 1, 1)
        self.channelFactorsLayout.addWidget(self.timeFactorStr, 1, 1, 1, 1)
        self.channelFactorsLayout.addWidget(self.timeUnitStr, 1, 2, 1, 1)
        self.channelFactorsLayout.addWidget(
            self.divideChannelsFactorLbl, 3, 0, 1, 1)
        self.channelFactorsLayout.addWidget(self.channelsFactorStr, 3, 1, 1, 1)
        self.channelFactorsLayout.addWidget(self.channelsUnitStr, 3, 2, 1, 1)
        self.channelFactorsLayout.addWidget(self.previewBtn, 4, 0, 1, 3)

        # Third line of Main layout
        self.previewTextBox = QTextBrowser(self.importDlg)
        self.previewTextBox.setLineWrapMode(0)

        # fourth line of Main layout
        self.lowerBtnPanel = QWidget(self.importDlg)
        self.lowerBtnPanel.setSizePolicy(
            QSizePolicy.Maximum, QSizePolicy.Maximum)

        self.acceptBtnImportDlg = QPushButton(self.lowerBtnPanel)
        self.acceptBtnImportDlg.setText('Accept')
        self.acceptBtnImportDlg.setDisabled(True)
        self.acceptBtnImportDlg.clicked.connect(self.plotPreviewDF)

        self.closeBtnImportDlg = QPushButton(self.lowerBtnPanel)
        self.closeBtnImportDlg.setText('Close')
        self.closeBtnImportDlg.clicked.connect(self.importDlg.accept)

        self.cancelBtnImportDlg = QPushButton(self.lowerBtnPanel)
        self.cancelBtnImportDlg.setText('Cancel')
        self.cancelBtnImportDlg.clicked.connect(self.importDlg.reject)

        self.lowerBtnPanelImportLayout = QHBoxLayout(self.lowerBtnPanel)
        self.lowerBtnPanelImportLayout.addWidget(self.acceptBtnImportDlg)
        self.lowerBtnPanelImportLayout.addWidget(self.closeBtnImportDlg)
        self.lowerBtnPanelImportLayout.addWidget(self.cancelBtnImportDlg)

        # main layout is a VBox
        self.mainLayoutImportDlg = QVBoxLayout(self.importDlg)
        self.mainLayoutImportDlg.addWidget(self.openFileBtn)
        self.mainLayoutImportDlg.addWidget(self.separatorsFrame)
        self.mainLayoutImportDlg.addWidget(self.channelFactorsFrame)
        self.mainLayoutImportDlg.addWidget(self.previewTextBox)
        self.mainLayoutImportDlg.addWidget(self.lowerBtnPanel)

        self.importDlg.exec_()

    def openVisualizationDialog(self):
        """This is function builds the dialog in which
            the user defines the parameters for data visualization. 

            It may be of interest to analyze only a defined number 
            of channels, or just a region. Also, for convenience 
            there is an option to set initial time to zero"""

        self.visualizationDlg = QDialog()
        self.visualizationDlg.setWindowFlag(
            QtCore.Qt.WindowContextHelpButtonHint, on=False)
        self.visualizationDlg.setWindowTitle('Visualization')

        self.showingChannelsLbl = QLabel(self.visualizationDlg)
        self.showingChannelsLbl.setText('Showing Channels:')

        self.showCh1Check = QCheckBox('ch1', self.visualizationDlg)
        if not self.showingChannelsControl['ch1']:
            self.showCh1Check.setDisabled(True)
        else:
            self.showCh1Check.setChecked(True)

        self.showCh2Check = QCheckBox('ch2', self.visualizationDlg)
        if not self.showingChannelsControl['ch2']:
            self.showCh2Check.setDisabled(True)
        else:
            self.showCh2Check.setChecked(True)

        self.showCh3Check = QCheckBox('ch3', self.visualizationDlg)
        if not self.showingChannelsControl['ch3']:
            self.showCh3Check.setDisabled(True)
        else:
            self.showCh3Check.setChecked(True)

        self.showCh4Check = QCheckBox('ch4', self.visualizationDlg)
        if not self.showingChannelsControl['ch4']:
            self.showCh4Check.setDisabled(True)
        else:
            self.showCh4Check.setChecked(True)

        self.showCh5Check = QCheckBox('ch5', self.visualizationDlg)
        if not self.showingChannelsControl['ch5']:
            self.showCh5Check.setDisabled(True)
        else:
            self.showCh5Check.setChecked(True)

        self.showCh6Check = QCheckBox('ch6', self.visualizationDlg)
        if not self.showingChannelsControl['ch6']:
            self.showCh6Check.setDisabled(True)
        else:
            self.showCh6Check.setChecked(True)

        self.showCh7Check = QCheckBox('ch7', self.visualizationDlg)
        if not self.showingChannelsControl['ch7']:
            self.showCh7Check.setDisabled(True)
        else:
            self.showCh7Check.setChecked(True)

        self.showCh8Check = QCheckBox('ch8', self.visualizationDlg)
        if not self.showingChannelsControl['ch8']:
            self.showCh8Check.setDisabled(True)
        else:
            self.showCh8Check.setChecked(True)

        self.cutDataLbl = QLabel(self.visualizationDlg)
        self.cutDataLbl.setText('Time interval:')

        self.startPointInput = QLineEdit(self.visualizationDlg)
        self.startPointInput.setFixedWidth(75)
        self.startPointInput.setText(str(self.startVisualizationTime))
        self.startPointInput.setPlaceholderText('Begin')

        self.endPointInput = QLineEdit(self.visualizationDlg)
        self.endPointInput.setFixedWidth(75)
        self.endPointInput.setText(str(self.endVisualizationTime))
        self.endPointInput.setPlaceholderText('End')

        self.startZeroCheck = QCheckBox(
            'Set initial time to 0?', self.visualizationDlg)

        self.plotVisDataBtn = QPushButton(self.visualizationDlg)
        self.plotVisDataBtn.setText('Plot')
        self.plotVisDataBtn.clicked.connect(self.setVisualizationDF)

        self.closeDlgBtn = QPushButton(self.visualizationDlg)
        self.closeDlgBtn.setText('Close')
        self.closeDlgBtn.clicked.connect(self.visualizationDlg.accept)

        self.cancelDlgBtn = QPushButton(self.visualizationDlg)
        self.cancelDlgBtn.setText('Cancel')
        self.cancelDlgBtn.clicked.connect(self.visualizationDlg.reject)

        # Main layout is a Grid with four columns
        # Grid management is row, col, rowspan, colspan
        self.mainVisDlgLayout = QGridLayout(self.visualizationDlg)

        self.mainVisDlgLayout.addWidget(self.showingChannelsLbl, 0, 0, 1, 4)
        self.mainVisDlgLayout.addWidget(self.showCh1Check, 1, 0, 1, 1)
        self.mainVisDlgLayout.addWidget(self.showCh2Check, 1, 1, 1, 1)
        self.mainVisDlgLayout.addWidget(self.showCh3Check, 1, 2, 1, 1)
        self.mainVisDlgLayout.addWidget(self.showCh4Check, 1, 3, 1, 1)
        self.mainVisDlgLayout.addWidget(self.showCh5Check, 2, 0, 1, 1)
        self.mainVisDlgLayout.addWidget(self.showCh6Check, 2, 1, 1, 1)
        self.mainVisDlgLayout.addWidget(self.showCh7Check, 2, 2, 1, 1)
        self.mainVisDlgLayout.addWidget(self.showCh8Check, 2, 3, 1, 1)

        self.mainVisDlgLayout.addWidget(self.cutDataLbl, 3, 0, 1, 2)
        self.mainVisDlgLayout.addWidget(self.startPointInput, 3, 2, 1, 2)
        self.mainVisDlgLayout.addWidget(self.endPointInput, 4, 2, 1, 2)

        self.mainVisDlgLayout.addWidget(self.startZeroCheck, 5, 0, 1, 4)

        self.mainVisDlgLayout.addWidget(self.plotVisDataBtn, 6, 0, 1, 4)

        self.mainVisDlgLayout.addWidget(self.closeDlgBtn, 7, 0, 1, 2)
        self.mainVisDlgLayout.addWidget(self.cancelDlgBtn, 7, 2, 1, 2)

        self.visualizationDlg.exec_()

    def openNormalizationDialog(self):
        """This function opens the Normalization dialog.
            Normalization means that the system will divide each
            column by its own value at a given time. The resulting
            data table will be plotted together for comparison.

            In this box, the user can choose the normalization point,
            and it can go back to the visualization table. This option
            should be available only when there are more than 2 columns
            in the visualizationDF"""

        self.normalizationDlg = QDialog()
        self.normalizationDlg.setWindowFlag(
            QtCore.Qt.WindowContextHelpButtonHint, on=False)
        self.normalizationDlg.resize(200, 100)
        self.normalizationDlg.setWindowTitle('Define normalization point')

        # define two main Frames:
        self.topNormDialogWidget = QWidget(self.normalizationDlg)
        self.topNormDialogWidget.setSizePolicy(
            QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.BottomNormDialogWidget = QWidget(self.normalizationDlg)

        # main layout is two lines, with the two Frames:
        self.mainNormDialogLayout = QVBoxLayout(self.normalizationDlg)
        self.mainNormDialogLayout.addWidget(self.topNormDialogWidget)
        self.mainNormDialogLayout.addWidget(self.BottomNormDialogWidget)
        self.mainNormDialogLayout.setAlignment(
            self.topNormDialogWidget, QtCore.Qt.AlignHCenter)

        # objects in the top Layout
        self.normTimeLbl = QLabel(self.topNormDialogWidget)
        self.normTimeLbl.setText('Normalize with resistance at:')

        self.normTimeInput = QLineEdit(self.topNormDialogWidget)
        self.normTimeInput.setPlaceholderText('Time')
        self.normTimeInput.setFixedWidth(75)

        # top layout is a HBox:
        self.topNormDialogLayout = QHBoxLayout(self.topNormDialogWidget)
        self.topNormDialogLayout.addWidget(self.normTimeLbl)
        self.topNormDialogLayout.addWidget(self.normTimeInput)

        # objects in the bottom layout
        self.normSetBtn = QPushButton(self.BottomNormDialogWidget)
        self.normSetBtn.setText('Normalize')
        self.normSetBtn.clicked.connect(self.setNormalizationDF)

        self.normVisBtn = QPushButton(self.BottomNormDialogWidget)
        self.normVisBtn.setText('Visualize')
        self.normVisBtn.clicked.connect(self.plotVisualizationData)

        self.normCloseBtn = QPushButton(self.BottomNormDialogWidget)
        self.normCloseBtn.setText('Close')
        self.normCloseBtn.clicked.connect(self.normalizationDlg.accept)

        self.normCancelBtn = QPushButton(self.BottomNormDialogWidget)
        self.normCancelBtn.setText('Cancel')
        self.normCancelBtn.clicked.connect(self.normalizationDlg.reject)

        # bottom layout is a HBox:
        self.bottomNormDialogLayout = QHBoxLayout(self.BottomNormDialogWidget)
        self.bottomNormDialogLayout.addWidget(self.normSetBtn)
        self.bottomNormDialogLayout.addWidget(self.normVisBtn)
        self.bottomNormDialogLayout.addWidget(self.normCloseBtn)
        self.bottomNormDialogLayout.addWidget(self.normCancelBtn)

        self.normalizationDlg.exec_()

    def openResponseDialog(self):
        """This is the box to calculate the response, response time, 
            and recovery time of each exposure. The user has to input
            the concentration of a given exposure cycle, the start of
            exposure time, the end of the exposure time, and the time 
            of the end of recovery. 

            Based on these three values, the system will calculate the
            response in dR/R0 in percentage or Rgas/Rair according to 
            the user’s choice. It will also calculate the response time 
            and recovery time will be given in time units."""

        self.responseDlg = QDialog()
        self.responseDlg.setWindowFlag(
            QtCore.Qt.WindowContextHelpButtonHint, on=False)

        self.responseDlg.setWindowTitle('Response/Recovery calculation')

        self.leftPanel = QWidget(self.responseDlg)

        self.sensorPropertiesTablePreview = QTextBrowser(self.responseDlg)
        self.sensorPropertiesTablePreview.setText(
            self.propertiesDF.to_string())
        self.sensorPropertiesTablePreview.setMinimumSize(400, 300)
        self.sensorPropertiesTablePreview.setLineWrapMode(0)

        self.mainRespDialogLayout = QHBoxLayout(self.responseDlg)
        self.mainRespDialogLayout.addWidget(self.leftPanel)
        self.mainRespDialogLayout.addWidget(self.sensorPropertiesTablePreview)

        # left panel objects
        self.concentrationLbl = QLabel(self.leftPanel)
        self.concentrationLbl.setText('Concentration:')

        self.concentrationInput = QLineEdit(self.leftPanel)
        self.concentrationInput.setPlaceholderText('conc. value')

        self.initialExpTimeLbl = QLabel(self.leftPanel)
        self.initialExpTimeLbl.setText('Start of exposure: ')

        self.initialExpTimeInput = QLineEdit(self.leftPanel)
        self.initialExpTimeInput.setPlaceholderText('time')

        self.finalExpTimeLbl = QLabel(self.leftPanel)
        self.finalExpTimeLbl.setText('End of exposure: ')

        self.finalExpTimeInput = QLineEdit(self.leftPanel)
        self.finalExpTimeInput.setPlaceholderText('time')

        self.finalRecTimeLbl = QLabel(self.leftPanel)
        self.finalRecTimeLbl.setText('End of recovery: ')

        self.finalRecTimeInput = QLineEdit(self.leftPanel)
        self.finalRecTimeInput.setPlaceholderText('time')

        self.ch1previewLbl = QLabel(self.leftPanel)
        self.ch1previewLbl.setText('ch1 preview:')

        self.calcSensitivityLbl = QLabel(self.leftPanel)
        self.calcSensitivityLbl.setText(self.responseLabel)

        self.calcSensitivityResult = QLabel(self.leftPanel)
        self.calcSensitivityResult.setText('...')

        self.calcRespTimeLbl = QLabel(self.leftPanel)
        self.calcRespTimeLbl.setText('t-resp-90 = ')

        self.calcRespTimeResult = QLabel(self.leftPanel)
        self.calcRespTimeResult.setText('...')

        self.calcRecoveryTimeLbl = QLabel(self.leftPanel)
        self.calcRecoveryTimeLbl.setText('t-rec-90 = ')

        self.calcRecoveryTimeResult = QLabel(self.leftPanel)
        self.calcRecoveryTimeResult.setText('...')

        self.calcRespBtn = QPushButton(self.leftPanel)
        self.calcRespBtn.setText('Calculate')
        self.calcRespBtn.clicked.connect(self.calcResponse)

        self.appendRespBtn = QPushButton(self.leftPanel)
        self.appendRespBtn.setText('Append')
        self.appendRespBtn.setDisabled(True)
        self.appendRespBtn.clicked.connect(self.appendResponseToDF)

        self.clearRespBtn = QPushButton(self.leftPanel)
        self.clearRespBtn.setText('Clear')
        self.clearRespBtn.clicked.connect(self.clearResponseDF)

        self.plotRespBtn = QPushButton(self.leftPanel)
        self.plotRespBtn.setText('Plot')
        self.plotRespBtn.clicked.connect(self.plotResponseData)

        self.closeRespBtn = QPushButton(self.leftPanel)
        self.closeRespBtn.setText('Close')
        self.closeRespBtn.clicked.connect(self.responseDlg.accept)

        self.cancelRespBtn = QPushButton(self.leftPanel)
        self.cancelRespBtn.setText('Cancel')
        self.cancelRespBtn.clicked.connect(self.responseDlg.reject)

        # left panel layout:
        self.leftPanelRespDialogLayout = QGridLayout(self.leftPanel)

        self.leftPanelRespDialogLayout.addWidget(
            self.concentrationLbl, 0, 0, 1, 1)
        self.leftPanelRespDialogLayout.addWidget(
            self.concentrationInput, 0, 1, 1, 1)
        self.leftPanelRespDialogLayout.addItem(QSpacerItem(1, 10), 1, 0, 1, 2)
        self.leftPanelRespDialogLayout.addWidget(
            self.initialExpTimeLbl, 2, 0, 1, 1)
        self.leftPanelRespDialogLayout.addWidget(
            self.initialExpTimeInput, 2, 1, 1, 1)
        self.leftPanelRespDialogLayout.addWidget(
            self.finalExpTimeLbl, 3, 0, 1, 1)
        self.leftPanelRespDialogLayout.addWidget(
            self.finalExpTimeInput, 3, 1, 1, 1)
        self.leftPanelRespDialogLayout.addWidget(
            self.finalRecTimeLbl, 4, 0, 1, 1)
        self.leftPanelRespDialogLayout.addWidget(
            self.finalRecTimeInput, 4, 1, 1, 1)
        self.leftPanelRespDialogLayout.addItem(QSpacerItem(1, 10), 5, 0, 1, 2)
        self.leftPanelRespDialogLayout.addWidget(
            self.ch1previewLbl, 6, 0, 1, 2)
        self.leftPanelRespDialogLayout.addWidget(
            self.calcSensitivityLbl, 7, 0, 1, 1)
        self.leftPanelRespDialogLayout.addWidget(
            self.calcSensitivityResult, 7, 1, 1, 1)
        self.leftPanelRespDialogLayout.addWidget(
            self.calcRespTimeLbl, 8, 0, 1, 1)
        self.leftPanelRespDialogLayout.addWidget(
            self.calcRespTimeResult, 8, 1, 1, 1)
        self.leftPanelRespDialogLayout.addWidget(
            self.calcRecoveryTimeLbl,  9, 0, 1, 1)
        self.leftPanelRespDialogLayout.addWidget(
            self.calcRecoveryTimeResult,  9, 1, 1, 1)
        self.leftPanelRespDialogLayout.addItem(QSpacerItem(1, 10), 10, 0, 1, 2)
        self.leftPanelRespDialogLayout.addWidget(
            self.calcRespBtn,  11, 0, 1, 1)
        self.leftPanelRespDialogLayout.addWidget(
            self.appendRespBtn,  11, 1, 1, 1)
        self.leftPanelRespDialogLayout.addWidget(
            self.clearRespBtn, 12, 0, 1, 1)
        self.leftPanelRespDialogLayout.addWidget(self.plotRespBtn, 12, 1, 1, 1)
        self.leftPanelRespDialogLayout.addWidget(
            self.closeRespBtn, 13, 0, 1, 1)
        self.leftPanelRespDialogLayout.addWidget(
            self.cancelRespBtn, 13, 1, 1, 1)

        self.leftPanelRespDialogLayout.setColumnStretch(0, 1)
        self.leftPanelRespDialogLayout.setColumnStretch(1, 1)

        self.responseDlg.exec_()

    def openExportDataDialog(self):
        """This function opens the export Data dialog.

            The user can choose to export to CSV files 
            the data from each one of the DataFrames as
            long as they are holding data. The options
            are visualizationDF, normalizationDF, 
            propertiesDF, fit Info"""

        self.exportDlg = QDialog()
        self.exportDlg.setWindowFlag(
            QtCore.Qt.WindowContextHelpButtonHint, on=False)
        self.exportDlg.setWindowTitle('Export Data')

        self.selectFolderBtn = QPushButton(self.exportDlg)
        self.selectFolderBtn.setText('Select Folder')
        self.selectFolderBtn.clicked.connect(self.getExportFileDirectory)

        self.exportFileNameLbl = QLabel(self.exportDlg)
        self.exportFileNameLbl.setText('Type the export file name:')

        self.exportFileNameInput = QLineEdit(self.exportDlg)

        self.exportChoiceLbl = QLabel(self.exportDlg)
        self.exportChoiceLbl.setText('Choose data to export:')

        self.exportVisDataCheck = QCheckBox(
            'Visualization DataFrame', self.exportDlg)
        self.exportVisDataCheck.setDisabled(True)

        self.exportNormDataCheck = QCheckBox(
            'Normalization DataFrame', self.exportDlg)
        self.exportNormDataCheck.setDisabled(True)

        self.exportPropDataCheck = QCheckBox(
            'Properties DataFrame', self.exportDlg)
        self.exportPropDataCheck.setDisabled(True)

        self.exportFitInfoCheck = QCheckBox('Fit Info', self.exportDlg)
        self.exportFitInfoCheck.setDisabled(True)

        self.exportDlgBtn = QPushButton(self.exportDlg)
        self.exportDlgBtn.setText('Export')
        self.exportDlgBtn.setDisabled(True)
        self.exportDlgBtn.clicked.connect(self.exportData)

        self.exportCloseBtn = QPushButton(self.exportDlg)
        self.exportCloseBtn.setText('Close')
        self.exportCloseBtn.clicked.connect(self.exportDlg.accept)

        # Main layout is a Grid
        # Grid management is row, col, rowspan, colspan
        self.exportDlgLayout = QGridLayout(self.exportDlg)
        self.exportDlgLayout.addWidget(self.selectFolderBtn, 0, 0, 1, 1)
        self.exportDlgLayout.addWidget(self.exportFileNameLbl, 1, 0, 1, 2)
        self.exportDlgLayout.addWidget(self.exportFileNameInput, 2, 0, 1, 2)
        self.exportDlgLayout.addWidget(self.exportChoiceLbl, 3, 0, 1, 2)
        self.exportDlgLayout.addWidget(self.exportVisDataCheck, 4, 0, 1, 1)
        self.exportDlgLayout.addWidget(self.exportNormDataCheck, 4, 1, 1, 1)
        self.exportDlgLayout.addWidget(self.exportPropDataCheck, 5, 0, 1, 1)
        self.exportDlgLayout.addWidget(self.exportFitInfoCheck, 5, 1, 1, 1)
        self.exportDlgLayout.addWidget(self.exportDlgBtn, 6, 0, 1, 1)
        self.exportDlgLayout.addWidget(self.exportCloseBtn, 6, 1, 1, 1)
        self.exportDlgLayout.setColumnStretch(0, 1)
        self.exportDlgLayout.setColumnStretch(1, 1)

        # option to export should be disabled if there is no data
        # Here, it checks the length of the index column for each DF,
        # If it is zero, then the user can not export it.

        if len(self.visualizationDF.index) != 0:
            self.exportVisDataCheck.setDisabled(False)

        if len(self.normalizationDF.index) != 0:
            self.exportNormDataCheck.setDisabled(False)

        if len(self.propertiesDF.index) != 0:
            self.exportPropDataCheck.setDisabled(False)

        if len(self.fitDF.index) != 0:
            self.exportFitInfoCheck.setDisabled(False)

        self.exportDlg.exec_()

    def openSettingsDialog(self):
        """ This box allows the user to choose the response type, 
            number of fitting points the plotting style and color 
            palette.

            The most important settings here are the response type
            and number of fitting points. The number of fitting 
            points will be the parameter that will generate the fitted
            function If the number is to big, it can make the
            fitting process slow."""

        self.settingsDlg = QDialog()
        self.settingsDlg.setWindowFlag(
            QtCore.Qt.WindowContextHelpButtonHint, on=False)
        self.settingsDlg.setWindowTitle('Settings')

        # Line 1
        self.settingsDlgWidget1 = QWidget(self.settingsDlg)
        self.settingsDlgWidget1.setSizePolicy(
            QSizePolicy.Maximum, QSizePolicy.Maximum)

        self.settingsRespTypeLbl = QLabel(self.settingsDlgWidget1)
        self.settingsRespTypeLbl.setText('Response type:')

        self.responseOpt1 = QRadioButton(self.settingsDlgWidget1)
        self.responseOpt1.setText(u'\u0394R/R0 (%) ')
        if self.responseType['dR/R0']:
            self.responseOpt1.setChecked(True)

        self.responseOpt2 = QRadioButton(self.settingsDlgWidget1)
        self.responseOpt2.setText('R(gas)/R(air) (a.u.)')
        if self.responseType['Rgas/Rair']:
            self.responseOpt2.setChecked(True)

        self.numberOfFitPointsLbl = QLabel('Number of fit points:')

        self.numberOfFitPointsInput = QLineEdit(self.settingsDlgWidget1)
        self.numberOfFitPointsInput.setPlaceholderText(
            f'{self.numberOfFitPoints}')
        self.numberOfFitPointsInput.setFixedWidth(50)

        self.settingsDlgWidget1Layout = QGridLayout(self.settingsDlgWidget1)
        self.settingsDlgWidget1Layout.addWidget(
            self.settingsRespTypeLbl, 0, 0, 1, 1)
        self.settingsDlgWidget1Layout.addWidget(self.responseOpt1, 1, 0, 1, 1)
        self.settingsDlgWidget1Layout.addWidget(self.responseOpt2, 2, 0, 1, 1)
        self.settingsDlgWidget1Layout.addItem(QSpacerItem(50, 1), 1, 1, 1, 1)
        self.settingsDlgWidget1Layout.addWidget(
            self.numberOfFitPointsLbl, 0, 2, 1, 1)
        self.settingsDlgWidget1Layout.addWidget(
            self.numberOfFitPointsInput, 0, 3, 1, 1)

        # Line 2
        self.settingsDlgWidget2 = QWidget(self.settingsDlg)

        self.matplotlibStyleLbl = QLabel(self.settingsDlgWidget2)
        self.matplotlibStyleLbl.setText('matplotlib Style: ')

        self.matplotlibStyleOpt1 = QRadioButton(self.settingsDlgWidget2)
        self.matplotlibStyleOpt1.setText('seaborn')
        self.matplotlibStyleOpt1.setChecked(True)

        self.matplotlibStyleOpt2 = QRadioButton(self.settingsDlgWidget2)
        self.matplotlibStyleOpt2.setText('seaborn white')

        self.matplotlibStyleOpt3 = QRadioButton(self.settingsDlgWidget2)
        self.matplotlibStyleOpt3.setText('bmh')

        self.matplotlibStyleOpt4 = QRadioButton(self.settingsDlgWidget2)
        self.matplotlibStyleOpt4.setText('greyScale')

        self.matplotlibStyleOpt5 = QRadioButton(self.settingsDlgWidget2)
        self.matplotlibStyleOpt5.setText('default')

        self.settingsDlgWidget2Layout = QGridLayout(self.settingsDlgWidget2)
        self.settingsDlgWidget2Layout.addWidget(
            self.matplotlibStyleLbl, 0, 0, 1, 5)
        self.settingsDlgWidget2Layout.addWidget(
            self.matplotlibStyleOpt1, 1, 0, 1, 1)
        self.settingsDlgWidget2Layout.addWidget(
            self.matplotlibStyleOpt2, 1, 1, 1, 1)
        self.settingsDlgWidget2Layout.addWidget(
            self.matplotlibStyleOpt3, 1, 2, 1, 1)
        self.settingsDlgWidget2Layout.addWidget(
            self.matplotlibStyleOpt4, 1, 3, 1, 1)
        self.settingsDlgWidget2Layout.addWidget(
            self.matplotlibStyleOpt5, 1, 4, 1, 1)

        # Line 3
        self.settingsDlgWidget3 = QWidget(self.settingsDlg)

        self.colorPaletteLbl = QLabel(self.settingsDlgWidget3)
        self.colorPaletteLbl.setText('Color Palette:')

        self.colorPaletteOpt1 = QRadioButton(self.settingsDlgWidget3)
        self.colorPaletteOpt1.setText('Option 1:')
        self.colorPaletteOpt1.setChecked(True)

        self.colorPalette1 = QLabel(self.settingsDlgWidget3)
        self.colorPalette1.setPixmap(QPixmap('palette1.png'))

        self.colorPaletteOpt2 = QRadioButton(self.settingsDlgWidget3)
        self.colorPaletteOpt2.setText('Option 2:')

        self.colorPalette2 = QLabel(self.settingsDlgWidget3)
        self.colorPalette2.setPixmap(QPixmap('palette2.png'))

        self.colorPaletteOpt3 = QRadioButton(self.settingsDlgWidget3)
        self.colorPaletteOpt3.setText('Option 3:')

        self.colorPalette3 = QLabel(self.settingsDlgWidget3)
        self.colorPalette3.setPixmap(QPixmap('palette3.png'))

        self.settingsDlgWidget3Layout = QGridLayout(self.settingsDlgWidget3)

        self.settingsDlgWidget3Layout.addWidget(
            self.colorPaletteLbl, 0, 0, 1, 3)
        self.settingsDlgWidget3Layout.addWidget(
            self.colorPaletteOpt1, 1, 0, 1, 1)
        self.settingsDlgWidget3Layout.addWidget(
            self.colorPalette1, 2, 0, 1, 1)
        self.settingsDlgWidget3Layout.addWidget(
            self.colorPaletteOpt2, 1, 1, 1, 1)
        self.settingsDlgWidget3Layout.addWidget(
            self.colorPalette2, 2, 1, 1, 1)
        self.settingsDlgWidget3Layout.addWidget(
            self.colorPaletteOpt3, 1, 2, 1, 1)
        self.settingsDlgWidget3Layout.addWidget(
            self.colorPalette3, 2, 2, 1, 1)

        # Line 4
        self.settingsDlgWidget4 = QWidget(self.settingsDlg)
        self.acceptSettingsBtn = QPushButton(self.settingsDlgWidget4)
        self.acceptSettingsBtn.setText('Accept')
        self.acceptSettingsBtn.clicked.connect(self.setSettings)

        self.closeSettingsBtn = QPushButton(self.settingsDlgWidget4)
        self.closeSettingsBtn.setText('Close')
        self.closeSettingsBtn.clicked.connect(self.settingsDlg.accept)

        self.settingsDlgWidget4Layout = QHBoxLayout(self.settingsDlgWidget4)
        self.settingsDlgWidget4Layout.addWidget(self.acceptSettingsBtn)
        self.settingsDlgWidget4Layout.addWidget(self.closeSettingsBtn)

        self.settingsDlgMainLayout = QGridLayout(self.settingsDlg)
        self.settingsDlgMainLayout.addWidget(
            self.settingsDlgWidget1, 0, 0, 1, 4)
        self.settingsDlgMainLayout.addItem(QSpacerItem(1, 10), 1, 0, 1, 4)
        self.settingsDlgMainLayout.addWidget(
            self.settingsDlgWidget2, 2, 0, 1, 4)
        self.settingsDlgMainLayout .addItem(QSpacerItem(1, 10), 3, 0, 1, 4)
        self.settingsDlgMainLayout.addWidget(
            self.settingsDlgWidget3, 4, 0, 1, 4)
        self.settingsDlgMainLayout.addWidget(
            self.settingsDlgWidget4, 5, 2, 1, 2)

        self.settingsDlg.exec_()

    def openFileRoutine(self):
        """This function will get the file path using the QFileDialog
            and set the fileName that will be used to insert the data
            into the rawDF"""

        self.fileDirectory = QFileDialog.getOpenFileName()
        self.fileName = f'{self.fileDirectory[0]}'

    def previewData(self):
        """This function is activated when the preview button
            in the open file dialog box is clicked. 
            This function will run the following steps:

            #1.	Check if there is a filePath in the variable fileName. 
                If there is, it goes forward, else it does nothing;

            #2.	The algorithm then empty the  rawDF and previewDF.
                This is designed to make this function able to work 
                multiple times after the software is running;

            #3.	It checks what is the separator chosen and uses the
                separatorList to assign it to the separator variable;

            #4.	Creates the rawDF using the read_csv from pandas;

            #5.	If it does not have at least 2 columns, the separator is wrong;

            #6.	Builds the previewDF by putting the name of 
                ch1, ch2, ch3… up to the length of the 
                number of columns in the rawDF.

                Also calculates and the new time values 
                and chanel values based on the users input. 

                If these inputs are not floatable, 
                it will return an error. 

            #7.	By the end of the routine it will put the 
                data in the previewTextBox and enable the 
                acceptButton and the visualization
                button in the dock widget;

            #8.	The name of each column here is ch1, ch2… 
                For each of these columns, it will make each
                variable stored in the dictionary 
                showingChannelsControl True;"""

        try:
            # 1
            if self.fileName:
                # 2
                self.rawDF = pd.DataFrame()
                self.previewDF = pd.DataFrame()
                for key in self.showingChannelsControl:
                    self.showingChannelsControl[key] = False

                # 3
                if self.tabSeparatorOpt.isChecked():
                    self.separator = self.separatorList[0]

                elif self.commaSeparatorOpt.isChecked():
                    self.separator = self.separatorList[1]

                elif self.spaceSeparatorOpt.isChecked():
                    self.separator = self.separatorList[2]

                elif self.semicolonSeparatorOpt.isChecked():
                    self.separator = self.separatorList[3]

                # 4
                self.rawDF = pd.read_csv(
                    self.fileName, sep=self.separator, header=None)

                # 5
                if len(self.rawDF.columns) == 1:
                    self.invalidParametersWarning(
                        'Invalid column separator!')

                # 6
                else:
                    """for referencing in the code, there is a colX list
                        to get the lists of the rawDF"""
                    self.rawDFColNames = []

                    for i in range(len(self.rawDF.columns)):
                        self.rawDFColNames.append(f'col{i}')

                    self.rawDF.columns = self.rawDFColNames

                    self.previewDF.insert(
                        0, 'Time', value=self.rawDF[self.rawDFColNames[0]])

                    if len(self.rawDF.columns) > self.numberOfChannelsSpin.value():
                        for i in range(1, self.numberOfChannelsSpin.value()+1):
                            self.previewDF.insert(
                                i, f'ch{i}', value=self.rawDF[self.rawDFColNames[i]])

                    else:
                        for i in range(1, len(self.rawDF.columns)):
                            self.previewDF.insert(
                                i, f'ch{i}', value=self.rawDF[self.rawDFColNames[i]])

                        self.invalidParametersWarning(
                            f'For this dataset the max \n number of Channels is {len(self.rawDF.columns)-1}')

                        self.numberOfChannelsSpin.setValue(
                            len(self.rawDF.columns)-1)

                    self.previewDF.set_index('Time', inplace=True)

                    if self.timeFactorStr.text():
                        try:
                            timeFactor = float(self.timeFactorStr.text())
                            self.previewDF.index = self.previewDF.index/timeFactor

                        except ValueError:
                            self.invalidParametersWarning(
                                'invalid time factor !')

                    if self.channelsFactorStr.text():
                        try:
                            channelFactor = float(
                                self.channelsFactorStr.text())

                            for i in range(len(self.previewDF.columns)):
                                colName = self.previewDF.columns[i]
                                self.previewDF[colName] = self.previewDF[colName] / \
                                    channelFactor

                        except ValueError:
                            self.invalidParametersWarning(
                                'invalid channel factor !')
                    # 7
                    self.previewTextBox.setText(
                        self.previewDF.to_string(max_rows=10))

                    self.acceptBtnImportDlg.setDisabled(False)
                    self.visualizationBtn.setDisabled(False)

                    # 8
                    for i in self.previewDF.columns:
                        self.showingChannelsControl[i] = True

            else:
                pass

        except:
            self.invalidParametersWarning('Error :(')

    def setVisualizationDF(self):
        """This function is called by the plot button (plotVisDataBtn) 
            in the visualization dialog box. 
            It will run the following steps:

            #1.	Empty the visualizationDF;

            #2.	Check if the user has entered values 
                to start and end time. If so, it will
                assign the variable startVisualizationTime
                and endVisualizationTime to the closest value
                that the user has entered. If there is none, 
                it will get the first and/or last values from 
                the previewDF;

            #3.	Then, it makes the visualizationDF equals
                the interval between startVisualizationTime
                and endVisualizationTime of the previewDF;

            #4.	It checks if the user wants to set the time to zero.
                If so, it will subtract the startVisualizationTime
                of the time data in the visualizationDF;

            #5.	Creates and populate a list (showingChannelsList) with
                the channels selected. Each of the checkbox was already
                made enabled or disabled after values present in the 
                showingChannelsControl that ware set in the 
                step #8 of previewData function.

            #6.	If the users do not select at least one channel, 
                it returns an error, else, it makes the visualizationDF
                equals itself but with only these columns, make the
                buttons response, and export available and plot
                the visualization data.

            #7.	Finally, it creates the propertiesTableColNames.
                This is based on what columns are inside the visualizationDF."""

        try:
            # 1
            self.visualizationDF = pd.DataFrame()

            # 2
            if self.startPointInput.text():
                self.startVisualizationTime = min(self.previewDF.index, key=lambda x: abs(
                    float(self.startPointInput.text())-x))
            else:
                self.startVisualizationTime = self.previewDF.first_valid_index()

            if self.endPointInput.text():
                self.endVisualizationTime = min(self.previewDF.index, key=lambda x: abs(
                    float(self.endPointInput.text())-x))
            else:
                self.endVisualizationTime = self.previewDF.last_valid_index()

            # 3
            self.visualizationDF = self.previewDF[self.startVisualizationTime:self.endVisualizationTime]

            # 4
            if self.startZeroCheck.isChecked():
                self.visualizationDF.index = self.visualizationDF.index - self.startVisualizationTime

            # 5
            self.showingChannelsList = []

            if self.showCh1Check.isEnabled():
                if self.showCh1Check.isChecked():
                    self.showingChannelsList.append('ch1')

            if self.showCh2Check.isEnabled():
                if self.showCh2Check.isChecked():
                    self.showingChannelsList.append('ch2')

            if self.showCh3Check.isEnabled():
                if self.showCh3Check.isChecked():
                    self.showingChannelsList.append('ch3')

            if self.showCh4Check.isEnabled():
                if self.showCh4Check.isChecked():
                    self.showingChannelsList.append('ch4')

            if self.showCh5Check.isEnabled():
                if self.showCh5Check.isChecked():
                    self.showingChannelsList.append('ch5')

            if self.showCh6Check.isEnabled():
                if self.showCh6Check.isChecked():
                    self.showingChannelsList.append('ch6')

            if self.showCh7Check.isEnabled():
                if self.showCh7Check.isChecked():
                    self.showingChannelsList.append('ch7')

            if self.showCh8Check.isEnabled():
                if self.showCh8Check.isChecked():
                    self.showingChannelsList.append('ch8')

            # 6
            if len(self.showingChannelsList) == 0:
                self.invalidParametersWarning('No data Select')
                self.plotPreviewDF()
                self.responseBtn.setDisabled(True)
                self.exportBtn.setDisabled(True)
            else:
                self.visualizationDF = self.visualizationDF[self.showingChannelsList]

                if len(self.visualizationDF.columns) > 1:
                    self.normalizationBtn.setDisabled(False)

                self.responseBtn.setDisabled(False)
                self.exportBtn.setDisabled(False)
                self.plotVisualizationData()

                # 7
                self.propertiesTableColNames = []

                for i in range(len(self.visualizationDF.columns)):
                    self.propertiesTableColNames.append(
                        f'{self.visualizationDF.columns[i]} resp')
                    self.propertiesTableColNames.append(
                        f'{self.visualizationDF.columns[i]} respTime')
                    self.propertiesTableColNames.append(
                        f'{self.visualizationDF.columns[i]} recTime')

        except ValueError:
            self.invalidParametersWarning('Invalid Parameters!')

    def setNormalizationDF(self):
        """This function will normalize the data inside the visualizationDF
            as long as it has at least two columns by dividing each column
            by its own value at the chosentime. It runs the following steps:

            #1.	Empty the normalizationDF;

            #2.	If there is text in the normTimeInput, 
                it makes the normalizationPoint as the
                closest value from the user’s input.

            #3.	It makes the normalizationDF indexes the 
                same as the visualizationDF;

            #4.	Then it inserts the visualization data
                divided by the normalizationPoint;

            #5.	Calls plotNormalizationData;"""

        try:
            # 1
            self.normalizationDF = pd.DataFrame()

            # 2
            if self.normTimeInput.text():

                self.normalizationPoint = min(self.visualizationDF.index,
                                              key=lambda x: abs(float(self.normTimeInput.text())-x))

                self.normalizationDF.insert(0, f'{self.visualizationDF.index.name}',
                                            value=self.visualizationDF.index)

                # 3
                self.normalizationDF.set_index(
                    f'{self.visualizationDF.index.name}', inplace=True)

                # 4
                for position, colName in enumerate(self.visualizationDF.columns):
                    self.normalizationDF.insert(position, f'ch{position+1} norm',
                                                value=self.visualizationDF[colName].div(self.visualizationDF[colName][self.normalizationPoint]))
                # 5
                self.plotNormalizationData()

        except ValueError:
            self.invalidParametersWarning('Error :(')

    def calcResponse(self):
        """ This function calculates the response, the response Time
            and the recovery time of a given exposure-recovery cycle
            for all channels present in the visualizationDF. 

            This function is called by pressing the calcRespBtn 
            on the responseDlg. The system does that by running 
            the following steps:

            #1.	After entering the concentration, start of exposure time,
                end of exposure time, and end of recovery time, it will 
                look into the visualizationDF for the closest values present
                in the data table. It will assign the variables startExposureTime,
                endExposureTime, endRecoveryTime with these values;

            #2.	Creates a list called properties list. For each column in the 
                visualizationDF it will find the initial resistance r0, final exposure
                resistance rf, and final recovery resistance rf2. These values correspond
                to the resistance values of startExposureTime, endExposureTime, 
                endRecoveryTime, respectively.

            #3.	Calculates the absolute variations in the adsorption and desorption cycles;

            #4.	It calculates the response according to the user’s settings 
                (in the settings dialog). The default is dR/R0 in %.

            #5.	Calculate the values corresponding to 90% respose and 
                recovery variation, and finds the corresponding values
                in the visualizationDF. The routine is different if the
                resistance variation is positive or negative. 

                The variation depends on the nature of the semiconductor 
                material/gas interaction;

            #6.	Find the time in the time table corresponding to these values,
                and subtracts the startExposureTime, endExposureTime to 
                calculate the response time and recovery time, respectively;

            #7.	Append the values of response, response time 
                and recovery time to the properties list,
                set the append button enabled, 

            #8.	Update the channel 1 preview panel and if 
                the propertiesDF has at least three rows, 
                it opens the enables the button in the 
                dock widget for the powerLaw fit.
            """

        try:
            # A list is created to hold the calculated values after the calculation is done

            # 1
            self.startExposureTime = min(self.visualizationDF.index, key=lambda x: abs(
                float(self.initialExpTimeInput.text())-x))

            self.endExposureTime = min(self.visualizationDF.index, key=lambda x: abs(
                float(self.finalExpTimeInput.text())-x))

            self.endRecoveryTime = min(self.visualizationDF.index, key=lambda x: abs(
                float(self.finalRecTimeInput.text())-x))

            # 2
            self.propertiesList = []

            for colName in self.visualizationDF.columns:

                self.r0 = self.visualizationDF[colName][self.startExposureTime]
                self.rf = self.visualizationDF[colName][self.endExposureTime]
                self.rf2 = self.visualizationDF[colName][self.endRecoveryTime]

                # 3
                self.deltaR1 = abs(self.rf-self.r0)
                self.deltaR2 = abs(self.rf2-self.rf)

                # 4
                if self.responseType['dR/R0']:
                    self.responseLabel = u'\u0394R/R0 (%)'
                    self.response = (self.deltaR1*100)/self.r0

                elif self.responseType['Rgas/Rair']:
                    self.responseLabel = 'Rg/Rair (a.u.)'
                    self.response = self.rf/self.r0

                # 5
                if self.rf > self.r0:
                    self.resp90Resistance = min(
                        self.visualizationDF[colName][self.startExposureTime:self.endExposureTime],
                        key=lambda x: abs(((self.r0+(0.9*self.deltaR1))-x)))

                    self.rec90Resistance = min(
                        self.visualizationDF[colName][self.endExposureTime:self.endRecoveryTime],
                        key=lambda x: abs(((self.rf-(0.9*self.deltaR2))-x)))
                else:
                    self.resp90Resistance = min(
                        self.visualizationDF[colName][self.startExposureTime:self.endExposureTime],
                        key=lambda x: abs(((self.r0-(0.9*self.deltaR1))-x)))

                    self.rec90Resistance = min(
                        self.visualizationDF[colName][self.endExposureTime:self.endRecoveryTime],
                        key=lambda x: abs(((self.rf+(0.9*self.deltaR2))-x)))

                # 6
                self.responseTime = self.visualizationDF[self.visualizationDF[colName]
                                                         == self.resp90Resistance].index.tolist()[0]-self.startExposureTime

                self.recoveryTime = self.visualizationDF[self.visualizationDF[colName]
                                                         == self.rec90Resistance].index.tolist()[0]-self.endExposureTime

                # 7
                self.propertiesList.append(self.response)
                self.propertiesList.append(self.responseTime)
                self.propertiesList.append(self.recoveryTime)

            # 8
            self.calcSensitivityResult.setText(f'{self.propertiesList[0]:.3f}')
            self.calcRespTimeResult.setText(f'{self.propertiesList[1]:.3f}')
            self.calcRecoveryTimeResult.setText(
                f'{self.propertiesList[2]:.3f}')

            self.appendRespBtn.setDisabled(False)

            if len(self.propertiesDF.index) > 1:
                self.fitBtn.setDisabled(False)

        except ValueError:
            self.invalidParametersWarning('Invalid values!')

    def appendResponseToDF(self):
        """This function gets the propertiesList and added to the propertiesDF. 
            It does that by 

            #1 converting this list into a pandas’ series with the 
                propertiesTableColNames and the name being the concentration value;

            #2 This series becomes the row is then appended to the propertiesDF;

            #3 it updates the text shown in the sensorPropertiesTablePreview;
            """

        # 1
        self.newResponseRow = pd.Series(self.propertiesList,
                                        index=self.propertiesTableColNames,
                                        name=float(self.concentrationInput.text()))

        # 2
        self.propertiesDF = self.propertiesDF.append(self.newResponseRow)

        # 3
        self.sensorPropertiesTablePreview.setText(
            self.propertiesDF.to_string())

    def clearResponseDF(self):
        """The user can clear the last line of the
            properties DF to start over"""

        if len(self.propertiesDF.index) == 0:
            self.invalidParametersWarning('The DF is empty!')

        else:
            self.propertiesDF.drop(
                axis=0, index=self.propertiesDF.last_valid_index(), inplace=True)
            self.sensorPropertiesTablePreview.setText(
                self.propertiesDF.to_string())

    def powerLawFunc(self, x, a, b):
        return a*(x**b)

    def fitRespData(self):
        """This function will fit the response data to the 
            powerLawFunc described previously. It does it by
            using the curve_fit from the scipy.optmize. 
            The algorithm run as follows:

            #1.	Empty the fitDF;

            #2.	Calculate the fitting step by dividing the last
                data point from the propertiesDF concentration
                column by the numberOfFitPoints that can be entered
                in the settings menu. If the last concentration is 5,
                and the number of points is 100, each step
                will be of 0.05;

            #3.	Enter the values in the x_fit_values that represent the 
                concentration values according to the step value,
                and starting at zero;

            #4.	Insert these values in the fitDF;

            #5.	For each column in the propertiesDF it will fit the curve
                using the function curve_fit and it uses the 
                visualizationDF.columns to get the proper names of each column.
                This is important because the user can choose any sort of 
                combination of channels to fit;

            #6.	The curve_fit function returns the coefficient that 
                are added to the coef1_list and coef2_list. Each of these
                lists will hold a number of values equivalent to the
                number of columns analyzed.

            #7.	Creates a str with this information that will be
                used in the legend when plotting. These strings are
                stored in the variable fitListLabel

            #8.	It calculates the y_fit_values and add to the fitDF;

            #9.	Call the function plotFittedData that plots both
                the fitDF and the response data from propertiesDF;
        """
        # 1
        self.fitDF = pd.DataFrame()
        self.x_fit_values = []

        # 2
        step = self.propertiesDF.last_valid_index()/self.numberOfFitPoints

        # 3
        for i in range(self.numberOfFitPoints):
            if len(self.x_fit_values) == 0:

                self.x_fit_values.append(0)
            else:

                self.x_fit_values.append(self.x_fit_values[-1]+step)

        # 4
        self.fitDF.insert(0, 'x_fit_values', self.x_fit_values)

        # 5
        for i in range(len(self.visualizationDF.columns)):
            name = f'y_fit_{i+1}'

            popt = curve_fit(self.powerLawFunc, self.propertiesDF.index,
                             self.propertiesDF[f'{self.visualizationDF.columns[i]} resp'])

            # 6
            self.coef1_list.append(popt[0][0])
            self.coef2_list.append(popt[0][1])

            # 7
            self.fitListLabel.append(
                f'fit {self.visualizationDF.columns[i]}: a={popt[0][0]:.2f}, b={popt[0][1]:.2f}')

            # 8
            y_fit_values = self.powerLawFunc(
                self.x_fit_values, popt[0][0], popt[0][1])

            # 9
            self.fitDF.insert(i+1, name, y_fit_values)

        self.fitDF.set_index('x_fit_values', inplace=True)
        self.plotFittedData()

    def getExportFileDirectory(self):
        """This function creates the string to the path
            to export the data"""

        self.exportDirectory = QFileDialog.getExistingDirectory(self.exportDlg)

        if self.exportDirectory:
            self.exportDlgBtn.setDisabled(False)

    def setSettings(self):
        """This function will set the values chosen in the 
            settings dialog box.

            #1 sets type of response type by assigning the to responseType dic
            #2 sets the fitting number points
            #3 sets the matplotlib style
            #4 sets color pallet
            #5 plot with new settings
        """
        try:
            # 1
            if self.responseOpt1.isChecked():
                self.responseType['dR/R0'] = True
                self.responseType['Rgas/Rair'] = False

            elif self.responseOpt2.isChecked():
                self.responseType['dR/R0'] = False
                self.responseType['Rgas/Rair'] = True

            # 2
            if self.numberOfFitPointsInput.text():
                self.numberOfFitPoints = int(
                    self.numberOfFitPointsInput.text())
            else:
                pass

            # 3
            if self.matplotlibStyleOpt1.isChecked():
                matplotlib.style.use('seaborn')

            elif self.matplotlibStyleOpt2.isChecked():
                matplotlib.style.use('seaborn-whitegrid')

            elif self.matplotlibStyleOpt3.isChecked():
                matplotlib.style.use('bmh')

            elif self.matplotlibStyleOpt4.isChecked():
                matplotlib.style.use('grayscale')

            elif self.matplotlibStyleOpt5.isChecked():
                matplotlib.style.use('default')

            # 4
            if self.colorPaletteOpt1.isChecked():
                self.palette = self.colorDic['Palette1']

            elif self.colorPaletteOpt2.isChecked():
                self.palette = self.colorDic['Palette2']

            elif self.colorPaletteOpt3.isChecked():
                self.palette = self.colorDic['Palette3']

            # 5
            if self.plottingControl['previewDF']:
                self.plotPreviewDF()
            elif self.plottingControl['visualizationDF']:
                self.plotVisualizationData()
            elif self.plottingControl['normalizationDF']:
                self.plotNormalizationData()
            elif self.plottingControl['propertiesDF']:
                self.plotResponseData()
            elif self.plottingControl['fittingDF']:
                self.plotFittedData()
            else:
                pass

        except ValueError:
            self.invalidParametersWarning('Invalid parameters!')

    def plotDataFrame(self, dataFrame, x_unit, y_axis_name, y_unit):
        """ This is a generic plot function that was designed to plot a dataframe. 
            It also asks for the units of the axis and it puts the name of the axis
            as necessary. It creates up to eight plots separated."""

        self.plottingDataFrame = dataFrame

        self.x_text = self.plottingDataFrame.index.name + f' ({x_unit})'
        self.y_text = y_axis_name+f' ({y_unit})'

        self.numberOfAxis = len(self.plottingDataFrame.columns)

        self.mainFigure.clf()

        self.mainFigure.text(0.5, 0.01,
                             self.x_text,
                             fontsize=12)

        self.mainFigure.text(0.005, 0.45,
                             self.y_text,
                             rotation=90,
                             fontsize=12)

        if self.numberOfAxis == 1:
            self.ax1 = self.mainFigure.add_subplot(111)

            self.ax1.plot(self.plottingDataFrame.iloc[:, 0],
                          color=self.palette[0],
                          label=self.plottingDataFrame.columns[0])

            self.ax1.legend(loc='upper right', shadow=True)

        elif self.numberOfAxis == 2:
            self.ax1 = self.mainFigure.add_subplot(211)
            self.ax2 = self.mainFigure.add_subplot(212)

            self.ax1.plot(self.plottingDataFrame.iloc[:, 0],
                          color=self.palette[0],
                          label=self.plottingDataFrame.columns[0])

            self.ax2.plot(self.plottingDataFrame.iloc[:, 1],
                          color=self.palette[1],
                          label=self.plottingDataFrame.columns[1])

            self.ax1.legend(loc='upper right', shadow=True)
            self.ax2.legend(loc='upper right', shadow=True)

        elif self.numberOfAxis == 3:
            self.ax1 = self.mainFigure.add_subplot(221)
            self.ax2 = self.mainFigure.add_subplot(222)
            self.ax3 = self.mainFigure.add_subplot(223)

            self.ax1.plot(self.plottingDataFrame.iloc[:, 0],
                          color=self.palette[0],
                          label=self.plottingDataFrame.columns[0])

            self.ax2.plot(self.plottingDataFrame.iloc[:, 1],
                          color=self.palette[1],
                          label=self.plottingDataFrame.columns[1])

            self.ax3.plot(self.plottingDataFrame.iloc[:, 2],
                          color=self.palette[2],
                          label=self.plottingDataFrame.columns[2])

            self.ax1.legend(loc='upper right', shadow=True)
            self.ax2.legend(loc='upper right', shadow=True)
            self.ax3.legend(loc='upper right', shadow=True)

        elif self.numberOfAxis == 4:
            self.ax1 = self.mainFigure.add_subplot(221)
            self.ax2 = self.mainFigure.add_subplot(222)
            self.ax3 = self.mainFigure.add_subplot(223)
            self.ax4 = self.mainFigure.add_subplot(224)

            self.ax1.plot(self.plottingDataFrame.iloc[:, 0],
                          color=self.palette[0],
                          label=self.plottingDataFrame.columns[0])

            self.ax2.plot(self.plottingDataFrame.iloc[:, 1],
                          color=self.palette[1],
                          label=self.plottingDataFrame.columns[1])

            self.ax3.plot(self.plottingDataFrame.iloc[:, 2],
                          color=self.palette[2],
                          label=self.plottingDataFrame.columns[2])

            self.ax4.plot(self.plottingDataFrame.iloc[:, 3],
                          color=self.palette[3],
                          label=self.plottingDataFrame.columns[3])

            self.ax1.legend(loc='upper right', shadow=True)
            self.ax2.legend(loc='upper right', shadow=True)
            self.ax3.legend(loc='upper right', shadow=True)
            self.ax4.legend(loc='upper right', shadow=True)

        elif self.numberOfAxis == 5:
            self.ax1 = self.mainFigure.add_subplot(231)
            self.ax2 = self.mainFigure.add_subplot(232)
            self.ax3 = self.mainFigure.add_subplot(233)
            self.ax4 = self.mainFigure.add_subplot(234)
            self.ax5 = self.mainFigure.add_subplot(235)

            self.ax1.plot(self.plottingDataFrame.iloc[:, 0],
                          color=self.palette[0],
                          label=self.plottingDataFrame.columns[0])

            self.ax2.plot(self.plottingDataFrame.iloc[:, 1],
                          color=self.palette[1],
                          label=self.plottingDataFrame.columns[1])

            self.ax3.plot(self.plottingDataFrame.iloc[:, 2],
                          color=self.palette[2],
                          label=self.plottingDataFrame.columns[2])

            self.ax4.plot(self.plottingDataFrame.iloc[:, 3],
                          color=self.palette[3],
                          label=self.plottingDataFrame.columns[3])

            self.ax5.plot(self.plottingDataFrame.iloc[:, 4],
                          color=self.palette[4],
                          label=self.plottingDataFrame.columns[4])

            self.ax1.legend(loc='upper right', shadow=True)
            self.ax2.legend(loc='upper right', shadow=True)
            self.ax3.legend(loc='upper right', shadow=True)
            self.ax4.legend(loc='upper right', shadow=True)
            self.ax5.legend(loc='upper right', shadow=True)

        elif self.numberOfAxis == 6:
            self.ax1 = self.mainFigure.add_subplot(231)
            self.ax2 = self.mainFigure.add_subplot(232)
            self.ax3 = self.mainFigure.add_subplot(233)
            self.ax4 = self.mainFigure.add_subplot(234)
            self.ax5 = self.mainFigure.add_subplot(235)
            self.ax6 = self.mainFigure.add_subplot(236)

            self.ax1.plot(self.plottingDataFrame.iloc[:, 0],
                          color=self.palette[0],
                          label=self.plottingDataFrame.columns[0])

            self.ax2.plot(self.plottingDataFrame.iloc[:, 1],
                          color=self.palette[1],
                          label=self.plottingDataFrame.columns[1])

            self.ax3.plot(self.plottingDataFrame.iloc[:, 2],
                          color=self.palette[2],
                          label=self.plottingDataFrame.columns[2])

            self.ax4.plot(self.plottingDataFrame.iloc[:, 3],
                          color=self.palette[3],
                          label=self.plottingDataFrame.columns[3])

            self.ax5.plot(self.plottingDataFrame.iloc[:, 4],
                          color=self.palette[4],
                          label=self.plottingDataFrame.columns[4])

            self.ax6.plot(self.plottingDataFrame.iloc[:, 5],
                          color=self.palette[5],
                          label=self.plottingDataFrame.columns[5])

            self.ax1.legend(loc='upper right', shadow=True)
            self.ax2.legend(loc='upper right', shadow=True)
            self.ax3.legend(loc='upper right', shadow=True)
            self.ax4.legend(loc='upper right', shadow=True)
            self.ax5.legend(loc='upper right', shadow=True)
            self.ax6.legend(loc='upper right', shadow=True)

        elif self.numberOfAxis == 7:
            self.ax1 = self.mainFigure.add_subplot(241)
            self.ax2 = self.mainFigure.add_subplot(242)
            self.ax3 = self.mainFigure.add_subplot(243)
            self.ax4 = self.mainFigure.add_subplot(244)
            self.ax5 = self.mainFigure.add_subplot(245)
            self.ax6 = self.mainFigure.add_subplot(246)
            self.ax7 = self.mainFigure.add_subplot(247)

            self.ax1.plot(self.plottingDataFrame.iloc[:, 0],
                          color=self.palette[0],
                          label=self.plottingDataFrame.columns[0])

            self.ax2.plot(self.plottingDataFrame.iloc[:, 1],
                          color=self.palette[1],
                          label=self.plottingDataFrame.columns[1])

            self.ax3.plot(self.plottingDataFrame.iloc[:, 2],
                          color=self.palette[2],
                          label=self.plottingDataFrame.columns[2])

            self.ax4.plot(self.plottingDataFrame.iloc[:, 3],
                          color=self.palette[3],
                          label=self.plottingDataFrame.columns[3])

            self.ax5.plot(self.plottingDataFrame.iloc[:, 4],
                          color=self.palette[4],
                          label=self.plottingDataFrame.columns[4])

            self.ax6.plot(self.plottingDataFrame.iloc[:, 5],
                          color=self.palette[5],
                          label=self.plottingDataFrame.columns[5])

            self.ax7.plot(self.plottingDataFrame.iloc[:, 6],
                          color=self.palette[6],
                          label=self.plottingDataFrame.columns[6])

            self.ax1.legend(loc='upper right', shadow=True)
            self.ax2.legend(loc='upper right', shadow=True)
            self.ax3.legend(loc='upper right', shadow=True)
            self.ax4.legend(loc='upper right', shadow=True)
            self.ax5.legend(loc='upper right', shadow=True)
            self.ax6.legend(loc='upper right', shadow=True)
            self.ax7.legend(loc='upper right', shadow=True)

        else:
            self.ax1 = self.mainFigure.add_subplot(241)
            self.ax2 = self.mainFigure.add_subplot(242)
            self.ax3 = self.mainFigure.add_subplot(243)
            self.ax4 = self.mainFigure.add_subplot(244)
            self.ax5 = self.mainFigure.add_subplot(245)
            self.ax6 = self.mainFigure.add_subplot(246)
            self.ax7 = self.mainFigure.add_subplot(247)
            self.ax8 = self.mainFigure.add_subplot(248)

            self.ax1.plot(self.plottingDataFrame.iloc[:, 0],
                          color=self.palette[0],
                          label=self.plottingDataFrame.columns[0])

            self.ax2.plot(self.plottingDataFrame.iloc[:, 1],
                          color=self.palette[1],
                          label=self.plottingDataFrame.columns[1])

            self.ax3.plot(self.plottingDataFrame.iloc[:, 2],
                          color=self.palette[2],
                          label=self.plottingDataFrame.columns[2])

            self.ax4.plot(self.plottingDataFrame.iloc[:, 3],
                          color=self.palette[3],
                          label=self.plottingDataFrame.columns[3])

            self.ax5.plot(self.plottingDataFrame.iloc[:, 4],
                          color=self.palette[4],
                          label=self.plottingDataFrame.columns[4])

            self.ax6.plot(self.plottingDataFrame.iloc[:, 5],
                          color=self.palette[5],
                          label=self.plottingDataFrame.columns[5])

            self.ax7.plot(self.plottingDataFrame.iloc[:, 6],
                          color=self.palette[6],
                          label=self.visualizationDF.columns[6])

            self.ax8.plot(self.plottingDataFrame.iloc[:, 7],
                          color=self.palette[7],
                          label=self.plottingDataFrame.columns[7])

            self.ax1.legend(loc='upper right', shadow=True)
            self.ax2.legend(loc='upper right', shadow=True)
            self.ax3.legend(loc='upper right', shadow=True)
            self.ax4.legend(loc='upper right', shadow=True)
            self.ax5.legend(loc='upper right', shadow=True)
            self.ax6.legend(loc='upper right', shadow=True)
            self.ax7.legend(loc='upper right', shadow=True)
            self.ax8.legend(loc='upper right', shadow=True)

        self.mainFigure.subplots_adjust(top=0.980,
                                        bottom=0.1,
                                        left=0.075,
                                        right=0.98,
                                        hspace=0.18,
                                        wspace=0.18)

        self.mainFigureCanvas.draw()

    def plotPreviewDF(self):
        """This function first adjusts the plotting control to 
            the previewDW and then it plots it using the 
            plotDataFrame function
        """

        self.plottingControl['previewDF'] = True
        self.plottingControl['visualizationDF'] = False
        self.plottingControl['normalizationDF'] = False
        self.plottingControl['propertiesDF'] = False
        self.plottingControl['fittingDF'] = False

        if len(self.previewDF.index) == 0:
            self.invalidParametersWarning('Empty Data Frame!')
        else:
            self.plotDataFrame(self.previewDF, self.timeUnitStr.text(
            ), 'Sensor data', self.channelsUnitStr.text())

    def plotVisualizationData(self):
        """This function first adjusts the plotting control to 
            the previewDW and then it plots it using the 
            plotDataFrame function
        """
        self.plottingControl['previewDF'] = False
        self.plottingControl['visualizationDF'] = True
        self.plottingControl['normalizationDF'] = False
        self.plottingControl['propertiesDF'] = False
        self.plottingControl['fittingDF'] = False

        if len(self.visualizationDF.index) == 0:
            self.invalidParametersWarning('Empty Data Frame!')

        else:
            self.plotDataFrame(self.visualizationDF, self.timeUnitStr.text(
            ), 'Sensor data', self.channelsUnitStr.text())

    def plotNormalizationData(self):
        """This function plots the normalizedDF in one axis"""

        self.plottingControl['previewDF'] = False
        self.plottingControl['visualizationDF'] = False
        self.plottingControl['normalizationDF'] = True
        self.plottingControl['propertiesDF'] = False
        self.plottingControl['fittingDF'] = False

        self.mainFigure.clf()

        self.mainFigure.text(0.50, 0.01,
                             self.normalizationDF.index.name,
                             fontsize=12)

        self.mainFigure.text(0.005, 0.32,
                             'Normalized Resistance, arb. unit.',
                             rotation=90,
                             fontsize=12)

        self.ax1 = self.mainFigure.add_subplot(111)

        for i in range(len(self.normalizationDF.columns)):
            self.ax1.plot(self.normalizationDF.iloc[:, i],
                          color=self.palette[i],
                          label=f'ch{i+1}')

        self.ax1.legend(loc='upper right', shadow=True)

        self.mainFigureCanvas.draw()

    def plotResponseData(self):
        """This function will plot the response,
            response time and recoveryTime in three plots separated"""

        self.plottingControl['previewDF'] = False
        self.plottingControl['visualizationDF'] = False
        self.plottingControl['normalizationDF'] = False
        self.plottingControl['propertiesDF'] = True
        self.plottingControl['fittingDF'] = False

        if len(self.propertiesDF.index) == 0:
            self.invalidParametersWarning('The properties DF is empty!')

        else:
            self.mainFigure.clf()

            self.mainFigure.text(0.48, 0.01,
                                 'Concentration',
                                 fontsize=12)

            self.ax1 = self.mainFigure.add_subplot(131)
            self.ax1.title.set_text(self.responseLabel)

            self.ax2 = self.mainFigure.add_subplot(132)
            self.ax2.title.set_text('Response time')

            self.ax3 = self.mainFigure.add_subplot(133)
            self.ax3.title.set_text('Recovery time')

            for i in range(len(self.visualizationDF.columns)):

                self.ax1.scatter(self.propertiesDF.index, self.propertiesDF[f'{self.visualizationDF.columns[i]} resp'],
                                 color=self.palette[i],
                                 marker='o',
                                 linestyle='None',
                                 label=self.visualizationDF.columns[i])

                self.ax2.scatter(self.propertiesDF.index, self.propertiesDF[f'{self.visualizationDF.columns[i]} respTime'],
                                 color=self.palette[i],
                                 marker='o',
                                 linestyle='None',
                                 label=self.visualizationDF.columns[i])

                self.ax3.scatter(self.propertiesDF.index, self.propertiesDF[f'{self.visualizationDF.columns[i]} recTime'],
                                 color=self.palette[i],
                                 marker='o',
                                 linestyle='None',
                                 label=self.visualizationDF.columns[i])

            self.mainFigure.subplots_adjust(top=0.950,
                                            bottom=0.1,
                                            left=0.075,
                                            right=0.98,
                                            hspace=0.15,
                                            wspace=0.15)

            self.ax3.legend(loc='best', shadow=True)
            self.mainFigureCanvas.draw()

    def plotFittedData(self):
        """This function will plot the response and the fitted data in one plot"""

        self.plottingControl['previewDF'] = False
        self.plottingControl['visualizationDF'] = False
        self.plottingControl['normalizationDF'] = False
        self.plottingControl['propertiesDF'] = False
        self.plottingControl['fittingDF'] = True

        self.mainFigure.clf()

        self.mainFigure.text(0.005, 0.45,
                             self.responseLabel,
                             rotation=90,
                             fontsize=12)

        self.mainFigure.text(0.48, 0.01, 'Concentration', fontsize=12)

        self.ax1 = self.mainFigure.add_subplot(111)

        for i in range(len(self.visualizationDF.columns)):

            self.ax1.plot(self.propertiesDF[f'{self.visualizationDF.columns[i]} resp'],
                          color=self.palette[i],
                          marker='o',
                          linestyle='None',
                          label=f'{self.visualizationDF.columns[i]}')

            self.ax1.plot(self.fitDF.iloc[:, i],
                          linestyle='dashed',
                          linewidth=0.5,
                          color=self.palette[i], label=self.fitListLabel[i])

        self.ax1.legend(loc='best', shadow=True)
        self.mainFigureCanvas.draw()

    def exportData(self):
        """This function will export the data frames into CSV files
            according to the folder that the user has chosen

            #1 Gets the export file names from the input box

            #2 Create paths according to the exportDirectory
                from the getExportFileDirectory function

            #3 Export the data that is checked. The check boxes are disabled 
                if there is no data in the respective dataFrame. The fitDF
                generates two tables, one with the data, another with the 
                fit info"""

        # 1
        self.exportFileName = self.exportFileNameInput.text()

        # 2
        self.path1 = self.exportDirectory+'/'+self.exportFileName+' VIS_DATA.dat'
        self.path2 = self.exportDirectory+'/'+self.exportFileName+' NORM_DATA.dat'
        self.path3 = self.exportDirectory+'/'+self.exportFileName+' RESPONSE_DATA.dat'
        self.path4 = self.exportDirectory+'/'+self.exportFileName+' FIT_INFO.dat'
        self.path5 = self.exportDirectory+'/'+self.exportFileName+' FIT_DATA.dat'

        # 3
        if self.exportVisDataCheck.isChecked():
            self.visualizationDF.to_csv(
                self.path1, sep=self.separator, index=True)

        if self.exportNormDataCheck.isChecked():
            self.normalizationDF.to_csv(
                self.path2, sep=self.separator, index=True)

        if self.exportPropDataCheck.isChecked():
            self.propertiesDF.to_csv(
                self.path3, sep=self.separator, index=True)

        if self.exportFitInfoCheck.isChecked():
            self.fitDataFile = open(self.path4, 'w')
            self.fitDataFile.write('Power Law Fit function:\n')
            self.fitDataFile.write('Response = a*(Conc.)^b:\n')

            for i in range(len(self.fitListLabel)):
                self.fitDataFile.write(f'{self.fitListLabel[i]}\n')

            self.fitDataFile.close()

            self.fitDF.to_csv(self.path5, sep=self.separator, index=True)

    def showAboutDialog(self):
        """Opens up an About Dialog"""

        self.aboutDlg = QDialog()
        self.aboutDlg.setFixedSize(300, 400)
        self.aboutDlg.setWindowTitle('About')

        self.aboutLbl1 = QLabel(self.aboutDlg)
        self.aboutLbl1.setText('Gas Sensor Data Analysis system')
        self.aboutLbl1.setAlignment(QtCore.Qt.AlignLeft)
        self.aboutLbl1.setSizePolicy(
            QSizePolicy.Maximum, QSizePolicy.Maximum)

        self.aboutLbl2 = QLabel(self.aboutDlg)
        self.aboutLbl2.setText('Beta Version 0.9')
        self.aboutLbl2.setAlignment(QtCore.Qt.AlignLeft)
        self.aboutLbl2.setSizePolicy(
            QSizePolicy.Maximum, QSizePolicy.Maximum)

        self.aboutLbl3 = QLabel(self.aboutDlg)
        self.aboutLbl3.setPixmap(QPixmap('logo.png'))
        self.aboutLbl3.setAlignment(QtCore.Qt.AlignCenter)

        self.aboutLbl4 = QLabel(self.aboutDlg)
        self.aboutLbl4.setText('This software was developed and tested by')
        self.aboutLbl4.setAlignment(QtCore.Qt.AlignLeft)
        self.aboutLbl4.setSizePolicy(
            QSizePolicy.Maximum, QSizePolicy.Maximum)

        self.aboutLbl5 = QLabel(self.aboutDlg)
        self.aboutLbl5.setText(
            'Bruno S. de Lima, Weverton A. S. Silva, Amadou L. Ndiaye, Valmor R. Mastelaro, and Jerome Brunet')
        self.aboutLbl5.setWordWrap(True)
        self.aboutLbl5.setAlignment(QtCore.Qt.AlignLeft)
        self.aboutLbl5.setSizePolicy(
            QSizePolicy.Maximum, QSizePolicy.Maximum)

        self.aboutBtn = QPushButton(self.aboutDlg)
        self.aboutBtn.setText('Ok')
        self.aboutBtn.setFixedWidth(100)
        self.aboutBtn.clicked.connect(self.aboutDlg.accept)

        self.aboutDlgLayout = QGridLayout(self.aboutDlg)
        self.aboutDlgLayout.addWidget(self.aboutLbl1, 0, 0, 1, 3)
        self.aboutDlgLayout.addWidget(self.aboutLbl2, 1, 0, 1, 3)
        self.aboutDlgLayout.addWidget(self.aboutLbl3, 2, 0, 1, 3)
        self.aboutDlgLayout.addWidget(self.aboutLbl4, 3, 0, 1, 3)
        self.aboutDlgLayout.addWidget(self.aboutLbl5, 4, 0, 1, 3)
        self.aboutDlgLayout.addWidget(self.aboutBtn, 5, 2, 1, 1)

        self.aboutDlg.exec_()

    def invalidParametersWarning(self, message):
        """Warning box for error handling"""

        self.message = message

        self.warningBox = QMessageBox()
        self.warningBox.setIcon(QMessageBox.Warning)
        self.warningBox.setWindowTitle('Error :(')
        self.warningBox.setText(self.message)
        self.warningBox.exec_()

    def closeEvent(self, event):
        """Close event with a message to confirm"""
        self.warningBox_2 = QMessageBox.question(self,
                                                 'Close window',
                                                 'Would you like to quit?',
                                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if self.warningBox_2 == QMessageBox.Yes:
            event.accept()

        else:
            event.ignore()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GasSensorDataAnalysisSystem()
    window.show()
    sys.exit(app.exec_())