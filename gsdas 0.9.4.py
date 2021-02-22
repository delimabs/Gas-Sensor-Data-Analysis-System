import sys
import matplotlib
import pandas as pd
from datetime import datetime
from scipy import stats, optimize
from matplotlib.pyplot import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from PyQt5 import QtCore
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import (QApplication, QMainWindow, QDockWidget, QVBoxLayout,
                             QHBoxLayout, QGridLayout, QWidget, QPushButton, QDialog,
                             QLabel, QLineEdit, QSizePolicy, QFileDialog, QSpinBox,
                             QCheckBox, QRadioButton, QTextEdit, QMessageBox, QSpacerItem)


class GasSensorDataAnalysisSystem(QMainWindow):
    def __init__(self):
        """ 
            ##########################################################

            CONSTRUCTOR: The constructor creates the main variables for
            the analysis process and settings. It also calls the two
            functions that will build the menu and the main Layout.

            ##########################################################
        """

        QMainWindow.__init__(self)
        self.setWindowTitle('Gas Sensor Data Analysis System v0.9.4')
        self.setGeometry(50, 50, 1350, 900)

        matplotlib.style.use('bmh')
        matplotlib.use('Qt5Agg')

        #---DATA FRAMES---#
        self.rawDF = pd.DataFrame()
        self.previewDF = pd.DataFrame()
        self.visualizationDF = pd.DataFrame()
        self.normalizationDF = pd.DataFrame()
        self.propertiesDF = pd.DataFrame()
        self.fitDF = pd.DataFrame()

        #---VARIABLES---#
        self.fileName = ''
        self.concentrationValues = []
        self.separatorList = ['\t', ',', ' ', ';']
        self.separator = ''
        self.responseLabel = u'\u0394S/S0 (%)'

        # used to visualize the data
        self.startVisualizationTime = ''
        self.endVisualizationTime = ''

        # used to calculate properties
        self.startExposureTime = ''
        self.endExposureTime = ''
        self.endRecoveryTime = ''
        self.timeFactor = 1
        self.channelFactor = 1
        self.numberOfChannels = 1
        self.timeUnitStr = 'unit'
        self.channelsUnitStr = 'unit'
        self.concentrationUnitStr = 'ppm'

        # used in the fitting process
        self.x_fit_values = []
        self.coef1_list = []
        self.coef2_list = []
        self.fitListLabel = []
        self.numberOfFitPoints = 100

        self.sensitivityList = []
        self.sensitivityRValues = []
        self.sensitivityResultsList = []

        # color options are based on these lists
        self.colorsList1 = ['black', 'firebrick', 'orange',
                            'yellowgreen', 'royalblue', 'seagreen', 'skyblue', 'violet']

        self.colorsList2 = ['k', 'b', 'g',
                            'r', 'c', 'm', 'y', 'cyan']

        self.colorsList3 = ['black', 'lightcoral', 'chocolate',
                            'gold', 'limegreen', 'royalblue', 'indigo', 'crimson']

        #---DICTIONARIES---#
        self.responseType = {'dR/R0': True,
                             'dR': False,
                             'Rgas/Rair': False,
                             'sigconc': False,
                             'sensitivity': False}

        self.showingChannelsControl = {'ch1': False, 'ch2': False,
                                       'ch3': False, 'ch4': False,
                                       'ch5': False, 'ch6': False,
                                       'ch7': False, 'ch8': False}

        self.plottingControl = {'previewDF': False,
                                'visualizationDF': False,
                                'normalizationDF': False,
                                'Response': False,
                                'Fit': False,
                                'RespTime': False,
                                'RecTime': False}

        self.colorDic = {'Palette1': self.colorsList1,
                         'Palette2': self.colorsList2,
                         'Palette3': self.colorsList3}

        self.palette = self.colorDic['Palette1']

        self.startMainLayout()

    def startMainLayout(self):
        """
            ##########################################################

            This function builds the main layout of the Interface:

            The main layout is a plot area that will get all the space
            of the central widget and a dock area that can float around
            but can't be closed. The dock widget can only be inserted 
            in the left area.

            cw is the central widget that will hold the main pyplot Figure
            dw is dock widget that will contain the application buttons

            ##########################################################
        """

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

        # create and define mainLayout as a VBox
        self.mainLayout = QVBoxLayout()
        self.cw.setLayout(self.mainLayout)
        self.mainLayout.addWidget(self.mainFigureCanvas)
        self.mainLayout.addWidget(self.mainFigureToolBar)

        # Create DW and define its features:
        self.dw = QDockWidget()
        self.dw.setWindowTitle('Menu')
        self.dw.setAllowedAreas(
            QtCore.Qt.LeftDockWidgetArea)
        self.dw.setFeatures(QDockWidget.DockWidgetFloatable |
                            QDockWidget.DockWidgetMovable)

        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.dw)
        self.dw.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)

        # create the frame that contain the buttons inside
        self.dwWidget = QWidget()
        self.dw.setWidget(self.dwWidget)

        self.lbl1 = QLabel(self.dwWidget)
        self.lbl1.setText('Open/Export:')

        self.openFileBtn = QPushButton(self.dwWidget)
        self.openFileBtn.setText('Open CSV File')
        self.openFileBtn.clicked.connect(self.openFileRoutine)

        self.exportBtn = QPushButton(self.dwWidget)
        self.exportBtn.setText('Export Data')
        self.exportBtn.setDisabled(True)
        self.exportBtn.clicked.connect(self.openExportDataDialog)

        self.lbl2 = QLabel(self.dwWidget)
        self.lbl2.setText('Plotting Options:')

        self.visualizationBtn = QPushButton(self.dwWidget)
        self.visualizationBtn.setText('Visualization')
        self.visualizationBtn.setDisabled(True)
        self.visualizationBtn.clicked.connect(self.openVisualizationDialog)

        self.normalizationBtn = QPushButton(self.dwWidget)
        self.normalizationBtn.setText('Normalization')
        self.normalizationBtn.setDisabled(True)
        self.normalizationBtn.clicked.connect(self.openNormalizationDialog)

        self.responseBtn = QPushButton(self.dwWidget)
        self.responseBtn.setText('Calc. Resp.')
        self.responseBtn.setDisabled(True)
        self.responseBtn.clicked.connect(self.openResponseDialog)

        self.fitBtn = QPushButton(self.dwWidget)
        self.fitBtn.setText('PowerLaw Fit')
        self.fitBtn.setDisabled(True)
        self.fitBtn.clicked.connect(self.fitRespData)

        self.lbl3 = QLabel(self.dwWidget)
        self.lbl3.setText('Show:')

        self.showVisualizationBtn = QPushButton(self.dwWidget)
        self.showVisualizationBtn.setText('Data Set')
        self.showVisualizationBtn.clicked.connect(self.plotVisualizationData)

        self.showNormalizationBtn = QPushButton(self.dwWidget)
        self.showNormalizationBtn.setText('Normalized')
        self.showNormalizationBtn.clicked.connect(self.plotNormalizationData)

        self.showResponseBtn = QPushButton(self.dwWidget)
        self.showResponseBtn.setText('Response')
        self.showResponseBtn.clicked.connect(self.plotRespData)

        self.showFitBtn = QPushButton(self.dwWidget)
        self.showFitBtn.setText('Fit')
        self.showFitBtn.clicked.connect(self.plotFittedData)

        self.showRespTimeBtn = QPushButton(self.dwWidget)
        self.showRespTimeBtn.setText('Resp time')
        self.showRespTimeBtn.clicked.connect(self.plotRespTimeData)

        self.showRecTimeBtn = QPushButton(self.dwWidget)
        self.showRecTimeBtn.setText('Rec time')
        self.showRecTimeBtn.clicked.connect(self.plotRecTimeData)

        self.lbl4 = QLabel(self.dwWidget)
        self.lbl4.setText('Configs:')

        self.settingsBtn = QPushButton(self.dwWidget)
        self.settingsBtn.setText('Settings')
        self.settingsBtn.clicked.connect(self.openSettingsDialog)

        self.aboutBtn = QPushButton(self.dwWidget)
        self.aboutBtn.setText('About')
        # self.aboutBtn.clicked.connect(self.showAboutDialog)
        self.aboutBtn.clicked.connect(self.saveHighQualityFig)

        self.exitBtn = QPushButton(self.dwWidget)
        self.exitBtn.setText('Exit')
        self.exitBtn.clicked.connect(self.close)

        # create DW layout and management
        self.dwLayout = QGridLayout(self.dwWidget)

        self.dwLayout.addWidget(self.lbl1, 0, 0, 1, 1)
        self.dwLayout.addWidget(self.openFileBtn, 1, 0, 1, 1)
        self.dwLayout.addWidget(self.exportBtn, 2, 0, 1, 1)

        self.dwLayout.addItem(QSpacerItem(5, 1), 3, 0, 1, 1)
        self.dwLayout.addWidget(self.lbl2, 9, 0, 1, 1)
        self.dwLayout.addWidget(self.visualizationBtn, 10, 0, 1, 1)
        self.dwLayout.addWidget(self.normalizationBtn, 11, 0, 1, 1)
        self.dwLayout.addWidget(self.responseBtn, 12, 0, 1, 1)
        self.dwLayout.addWidget(self.fitBtn, 13, 0, 1, 1)

        self.dwLayout.addItem(QSpacerItem(5, 1), 14, 0, 1, 1)
        self.dwLayout.addWidget(self.lbl3, 20, 0, 1, 1)
        self.dwLayout.addWidget(self.showVisualizationBtn, 21, 0, 1, 1)
        self.dwLayout.addWidget(self.showNormalizationBtn, 22, 0, 1, 1)
        self.dwLayout.addWidget(self.showResponseBtn, 23, 0, 1, 1)
        self.dwLayout.addWidget(self.showFitBtn, 24, 0, 1, 1)
        self.dwLayout.addWidget(self.showRespTimeBtn, 25, 0, 1, 1)
        self.dwLayout.addWidget(self.showRecTimeBtn, 26, 0, 1, 1)

        self.dwLayout.addItem(QSpacerItem(5, 1), 27, 0, 1, 1)
        self.dwLayout.addWidget(self.lbl4, 32, 0, 1, 1)
        self.dwLayout.addWidget(self.settingsBtn, 33, 0, 1, 1)
        self.dwLayout.addWidget(self.aboutBtn, 34, 0, 1, 1)
        self.dwLayout.addWidget(self.exitBtn, 35, 0, 1, 1)

        self.dwLayout.setRowStretch(36, 1)

    def openFileDialog(self):
        """ 
            ##########################################################

            This function will construct the dialog to open/import data.

            Here, the user has to browse for the file to open, define 
            what is the separator used in the data table, define the number
            of channels, being 8 the maximum value.

            Also, there is the possibility of dividing the time or the 
            channel columns by a factor, to convert the time/resistance
            to the desired unit

            ##########################################################
        """

        self.importDlg = QDialog()
        self.importDlg.setWindowFlag(
            QtCore.Qt.WindowContextHelpButtonHint, on=False)
        self.importDlg.setWindowTitle('Import data')

        # First Frame of Main layout
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

        # Second Frame of Main layout
        self.channelFactorsFrame = QWidget(self.importDlg)
        self.channelFactorsFrame.setSizePolicy(
            QSizePolicy.Maximum, QSizePolicy.Maximum)

        self.numberOfChannelsLbl = QLabel(self.channelFactorsFrame)
        self.numberOfChannelsLbl.setText('Number of Channels')

        self.numberOfChannelsSpin = QSpinBox(self.channelFactorsFrame)
        self.numberOfChannelsSpin.setMinimum(1)
        self.numberOfChannelsSpin.setMaximum(8)
        self.numberOfChannelsSpin.setValue(self.numberOfChannels)

        self.divideTimeFactorLbl = QLabel(self.channelFactorsFrame)
        self.divideTimeFactorLbl.setText('Divide time column by:')

        self.timeFactorStr = QLineEdit(self.channelFactorsFrame)
        self.timeFactorStr.setFixedWidth(50)
        self.timeUnitInput = QLineEdit(self.channelFactorsFrame)
        self.timeUnitInput.setPlaceholderText('unit')
        self.timeUnitInput.setFixedWidth(50)

        self.divideChannelsFactorLbl = QLabel(self.channelFactorsFrame)
        self.divideChannelsFactorLbl.setText('Divide channels columns by:')

        self.channelsFactorStr = QLineEdit(self.channelFactorsFrame)
        self.channelsFactorStr.setFixedWidth(50)
        self.channelsUnitInput = QLineEdit(self.channelFactorsFrame)
        self.channelsUnitInput.setPlaceholderText('unit')
        self.channelsUnitInput.setFixedWidth(50)

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
        self.channelFactorsLayout.addWidget(self.timeUnitInput, 1, 2, 1, 1)
        self.channelFactorsLayout.addWidget(
            self.divideChannelsFactorLbl, 3, 0, 1, 1)
        self.channelFactorsLayout.addWidget(self.channelsFactorStr, 3, 1, 1, 1)
        self.channelFactorsLayout.addWidget(self.channelsUnitInput, 3, 2, 1, 1)
        self.channelFactorsLayout.addWidget(self.previewBtn, 4, 0, 1, 3)

        # Third Object is a QTextEditor of Main layout
        self.previewTextBox = QTextEdit(self.importDlg)
        self.previewTextBox.setReadOnly(True)
        self.previewTextBox.setLineWrapMode(0)
        self.previewTextBox.setFont(QFont('Courier'))

        # fourth line of Main layout
        self.lowerBtnFrame = QWidget(self.importDlg)
        self.lowerBtnFrame.setSizePolicy(
            QSizePolicy.Maximum, QSizePolicy.Maximum)

        self.acceptBtnImportDlg = QPushButton(self.lowerBtnFrame)
        self.acceptBtnImportDlg.setText('Accept')
        self.acceptBtnImportDlg.setDisabled(True)
        self.acceptBtnImportDlg.clicked.connect(self.plotPreviewDF)

        self.closeBtnImportDlg = QPushButton(self.lowerBtnFrame)
        self.closeBtnImportDlg.setText('Close')
        self.closeBtnImportDlg.clicked.connect(self.importDlg.accept)

        self.lowerBtnFrameImportLayout = QHBoxLayout(self.lowerBtnFrame)
        self.lowerBtnFrameImportLayout.addWidget(self.acceptBtnImportDlg)
        self.lowerBtnFrameImportLayout.addWidget(self.closeBtnImportDlg)

        # main layout is a VBox
        self.mainLayoutImportDlg = QVBoxLayout(self.importDlg)
        self.mainLayoutImportDlg.addWidget(self.separatorsFrame)
        self.mainLayoutImportDlg.addWidget(self.channelFactorsFrame)
        self.mainLayoutImportDlg.addWidget(self.previewTextBox)
        self.mainLayoutImportDlg.addWidget(
            self.lowerBtnFrame, alignment=QtCore.Qt.Alignment(QtCore.Qt.AlignCenter))

        self.importDlg.exec_()

    def openVisualizationDialog(self):
        """
            ##########################################################

            This function builds the dialog in which the user defines 
            the parameters for data visualization.

            It may be of interest to analyze only a defined number
            of channels, or just a region. Also, for convenience
            there is an option to set initial time to zero

            ##########################################################
        """

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

        self.mainVisDlgLayout.addWidget(self.plotVisDataBtn, 6, 0, 1, 2)
        self.mainVisDlgLayout.addWidget(self.closeDlgBtn, 6, 2, 1, 2)

        self.visualizationDlg.exec_()

    def openNormalizationDialog(self):
        """
            ########################################################## 

            This function opens the Normalization dialog.
            Normalization means that the system will divide each
            column by its own value at a given time. The resulting
            data table will be plotted together for comparison.

            This option is available only when  there are more than
            2 columns in the visualizationDF

            ##########################################################
        """

        self.normalizationDlg = QDialog()
        self.normalizationDlg.setWindowFlag(
            QtCore.Qt.WindowContextHelpButtonHint, on=False)
        self.normalizationDlg.resize(200, 100)
        self.normalizationDlg.setWindowTitle('Normalization')

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

        self.normCloseBtn = QPushButton(self.BottomNormDialogWidget)
        self.normCloseBtn.setText('Close')
        self.normCloseBtn.clicked.connect(self.normalizationDlg.reject)

        # bottom layout is a HBox:
        self.bottomNormDialogLayout = QHBoxLayout(self.BottomNormDialogWidget)
        self.bottomNormDialogLayout.addWidget(self.normSetBtn)
        self.bottomNormDialogLayout.addWidget(self.normCloseBtn)

        self.normalizationDlg.exec_()

    def openResponseDialog(self):
        """
            ##########################################################

            This is the box to calculate the response, response time,
            and recovery time of each exposure. The user has to input
            the concentration of a given exposure cycle, the start of
            exposure time, the end of the exposure time, and the time
            of the end of recovery.

            Based on these three values, the system will calculate the
            response in dR/R0 in percentage or Rgas/Rair according to
            the user’s choice. It will also calculate the response time
            and recovery time will be given in time units.

            ##########################################################
        """

        self.responseDlg = QDialog()
        self.responseDlg.setWindowFlag(
            QtCore.Qt.WindowContextHelpButtonHint, on=False)

        self.responseDlg.setWindowTitle('Response/Recovery calculation')

        self.leftPanel = QWidget(self.responseDlg)

        self.sensorPropertiesTablePreview = QTextEdit(self.responseDlg)
        self.sensorPropertiesTablePreview.setText(
            self.propertiesDF.to_string(float_format='%10.2f', justify='match-parent'))
        self.sensorPropertiesTablePreview.setMinimumSize(400, 300)
        self.sensorPropertiesTablePreview.setReadOnly(True)
        self.sensorPropertiesTablePreview.setLineWrapMode(0)
        self.sensorPropertiesTablePreview.setFont(QFont('Courier'))

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

        self.clearLastRespBtn = QPushButton(self.leftPanel)
        self.clearLastRespBtn.setText('Clear last')
        self.clearLastRespBtn.clicked.connect(self.clearLastResponseDF)

        self.clearAllRespBtn = QPushButton(self.leftPanel)
        self.clearAllRespBtn.setText('Clear all')
        self.clearAllRespBtn.clicked.connect(self.clearAllResponseDF)

        self.plotRespBtn = QPushButton(self.leftPanel)
        self.plotRespBtn.setText('Plot')
        self.plotRespBtn.clicked.connect(self.plotRespData)

        self.closeRespBtn = QPushButton(self.leftPanel)
        self.closeRespBtn.setText('Close')
        self.closeRespBtn.clicked.connect(self.responseDlg.accept)



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
            self.clearAllRespBtn, 12, 0, 1, 1)
        self.leftPanelRespDialogLayout.addWidget(self.clearLastRespBtn, 12, 1, 1, 1)
        self.leftPanelRespDialogLayout.addWidget(
            self.plotRespBtn, 13, 0, 1, 1)
        self.leftPanelRespDialogLayout.addWidget(
            self.closeRespBtn, 13, 1, 1, 1)

        self.leftPanelRespDialogLayout.setColumnStretch(0, 1)
        self.leftPanelRespDialogLayout.setColumnStretch(1, 1)

        self.responseDlg.exec_()

    def openExportDataDialog(self):
        """
            ##########################################################
            This function opens the export Data dialog.

            The user can choose to export to CSV files the data from each
            one of the DataFrames as long as they are holding data. The 
            options are visualizationDF, normalizationDF, propertiesDF, 
            fit data and info.

            ##########################################################    
        """

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
        """
            ##########################################################

            This box allows the user to choose the response type, number 
            of fitting points the plotting style and color palette.

            The most important settings here are the response type, conc
            unit, and number of fitting points. The number of fitting
            points will be the parameter that will generate the fitted
            function If the number is to big, it can make the
            fitting process slow.

            ##########################################################
        """

        self.settingsDlg = QDialog()
        self.settingsDlg.setWindowFlag(
            QtCore.Qt.WindowContextHelpButtonHint, on=False)
        self.settingsDlg.setWindowTitle('Settings')

        # Line 1
        self.settingsDlgWidget1 = QWidget(self.settingsDlg)
        self.settingsDlgWidget1.setSizePolicy(
            QSizePolicy.Maximum, QSizePolicy.Maximum)

        self.settingsRespTypeLbl = QLabel(self.settingsDlgWidget1)
        self.settingsRespTypeLbl.setText('Signal type (S):')

        self.responseOpt1 = QRadioButton(self.settingsDlgWidget1)
        self.responseOpt1.setText(u'\u0394S/S0 (%) ')
        if self.responseType['dR/R0']:
            self.responseOpt1.setChecked(True)

        self.responseOpt2 = QRadioButton(self.settingsDlgWidget1)
        self.responseOpt2.setText(u'\u0394S'+f' ({self.channelsUnitStr})')
        if self.responseType['dR']:
            self.responseOpt2.setChecked(True)

        self.responseOpt3 = QRadioButton(self.settingsDlgWidget1)
        self.responseOpt3.setText('S(gas)/S(air)')
        if self.responseType['Rgas/Rair']:
            self.responseOpt3.setChecked(True)

        self.responseOpt4 = QCheckBox(self.settingsDlgWidget1)
        self.responseOpt4.setText('Signal/conc?')
        if self.responseType['sigconc']:
            self.responseOpt4.setChecked(True)

        self.sensitivityOpt = QCheckBox(self.settingsDlgWidget1)
        self.sensitivityOpt.setText('Sensitivity?')
        if self.responseType['sensitivity']:
            self.sensitivityOpt.setChecked(True)
        
        self.concentrationUnitLbl = QLabel(self.settingsDlgWidget1)
        self.concentrationUnitLbl.setText('Conc. unit:  ')

        self.concentrationUnitInput = QLineEdit(self.settingsDlgWidget1)
        self.concentrationUnitInput.setPlaceholderText(self.concentrationUnitStr)
        self.concentrationUnitInput.setFixedWidth(50)

        self.numberOfFitPointsLbl = QLabel('N fit points:')

        self.numberOfFitPointsInput = QLineEdit(self.settingsDlgWidget1)
        self.numberOfFitPointsInput.setPlaceholderText(f'{self.numberOfFitPoints}')
        self.numberOfFitPointsInput.setFixedWidth(50)

        self.settingsDlgWidget1Layout = QGridLayout(self.settingsDlgWidget1)
        self.settingsDlgWidget1Layout.addWidget(self.settingsRespTypeLbl, 0, 0, 1, 1)
        self.settingsDlgWidget1Layout.addWidget(self.responseOpt1, 1, 0, 1, 1)
        self.settingsDlgWidget1Layout.addWidget(self.responseOpt2, 2, 0, 1, 1)
        self.settingsDlgWidget1Layout.addWidget(self.responseOpt3, 3, 0, 1, 1)
        self.settingsDlgWidget1Layout.addWidget(self.responseOpt4, 1, 1, 1, 1)
        self.settingsDlgWidget1Layout.addWidget(self.sensitivityOpt, 2, 1, 1, 1)
        self.settingsDlgWidget1Layout.addWidget(self.concentrationUnitLbl, 1, 3, 1, 1)
        self.settingsDlgWidget1Layout.addWidget(self.concentrationUnitInput, 1, 4, 1, 1)
        self.settingsDlgWidget1Layout.addWidget(self.numberOfFitPointsLbl, 2, 3, 1, 1)
        self.settingsDlgWidget1Layout.addWidget(self.numberOfFitPointsInput, 2, 4, 1, 1)
        self.settingsDlgWidget1Layout.setColumnStretch(5, 1)

        # Line 2
        self.settingsDlgWidget2 = QWidget(self.settingsDlg)

        self.matplotlibStyleLbl = QLabel(self.settingsDlgWidget2)
        self.matplotlibStyleLbl.setText('matplotlib Style: ')

        self.matplotlibStyleOpt1 = QRadioButton(self.settingsDlgWidget2)
        self.matplotlibStyleOpt1.setText('bmh')
        self.matplotlibStyleOpt1.setChecked(True)

        self.matplotlibStyleOpt2 = QRadioButton(self.settingsDlgWidget2)
        self.matplotlibStyleOpt2.setText('seaborn')

        self.matplotlibStyleOpt3 = QRadioButton(self.settingsDlgWidget2)
        self.matplotlibStyleOpt3.setText('greyScale')

        self.matplotlibStyleOpt4 = QRadioButton(self.settingsDlgWidget2)
        self.matplotlibStyleOpt4.setText('default')

        self.settingsDlgWidget2Layout = QGridLayout(self.settingsDlgWidget2)
        self.settingsDlgWidget2Layout.addWidget(self.matplotlibStyleLbl, 0, 0, 1, 4)
        self.settingsDlgWidget2Layout.addWidget(self.matplotlibStyleOpt1, 1, 0, 1, 1)
        self.settingsDlgWidget2Layout.addWidget(self.matplotlibStyleOpt2, 1, 1, 1, 1)
        self.settingsDlgWidget2Layout.addWidget(self.matplotlibStyleOpt3, 1, 2, 1, 1)
        self.settingsDlgWidget2Layout.addWidget(self.matplotlibStyleOpt4, 1, 3, 1, 1)
        self.settingsDlgWidget2Layout.setColumnStretch(5, 1)

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

        self.settingsDlgWidget3Layout.addWidget(self.colorPaletteLbl, 0, 0, 1, 1)
        self.settingsDlgWidget3Layout.addWidget(self.colorPaletteOpt1, 1, 0, 1, 1)
        self.settingsDlgWidget3Layout.addWidget(self.colorPalette1, 2, 0, 1, 1)
        self.settingsDlgWidget3Layout.addWidget(self.colorPaletteOpt2, 1, 1, 1, 1)
        self.settingsDlgWidget3Layout.addWidget(self.colorPalette2, 2, 1, 1, 1)
        self.settingsDlgWidget3Layout.addWidget(self.colorPaletteOpt3, 1, 2, 1, 1)
        self.settingsDlgWidget3Layout.addWidget( self.colorPalette3, 2, 2, 1, 1)
        self.settingsDlgWidget2Layout.setColumnStretch(3, 1)

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
        self.settingsDlgMainLayout.addWidget(self.settingsDlgWidget1, 0, 0, 1, 3)
        self.settingsDlgMainLayout.addItem(QSpacerItem(1, 10), 1, 0, 1, 4)
        self.settingsDlgMainLayout.addWidget(self.settingsDlgWidget2, 2, 0, 1, 3)
        self.settingsDlgMainLayout.addItem(QSpacerItem(1, 10), 3, 0, 1, 4)
        self.settingsDlgMainLayout.addWidget(self.settingsDlgWidget3, 4, 0, 1, 3)
        self.settingsDlgMainLayout.addItem(QSpacerItem(1, 10), 5, 0, 1, 4)
        self.settingsDlgMainLayout.addWidget(self.settingsDlgWidget4, 6, 1, 1, 2)

        self.settingsDlg.exec_()

    def openFileRoutine(self):
        """ ##########################################################

            This function will get the file path using the QFileDialog
            and set the fileName that will be used to insert the data 
            into the rawDF. If there is data in the variable fileName, 
            it will clean the figure, the dataFrames, and it will call 
            the function openFileDialog.

            ###########################################################
        """

        # self.fileDirectory = QFileDialog.getOpenFileName(options=QFileDialog.DontUseNativeDialog)
        self.fileDirectory = QFileDialog.getOpenFileName()
        self.fileName = f'{self.fileDirectory[0]}'

        if self.fileName:
            self.propertiesDF = pd.DataFrame()
            self.previewDF = pd.DataFrame()
            self.visualizationDF = pd.DataFrame()
            self.normalizationDF = pd.DataFrame()
            self.propertiesDF = pd.DataFrame()
            self.fitDF = pd.DataFrame()
            self.mainFigure.clf()
            self.openFileDialog()

        else:
            pass

    def previewData(self):
        """
            ##########################################################

            This function is activated when the preview button (previewBtn)
            in the open file dialog box is clicked. This function will run
            the following steps:

            #1. The algorithm then empties the  rawDF and previewDF.
                This is designed to make this function able to work
                multiple times after the software is running. It also
                gets the value from the unitInputs and assign them
                to the corresponding variables;

            #2.	It checks what is the separator chosen and uses the
                separatorList to assign it to the separator variable;

            #3. Creates the rawDF using the read_csv from pandas;

            #4. If it does not have at least 2 columns, the separator is
                probably wrong. It warns the user about this;

            #5. Builds the previewDF by putting the name of ch1, ch2, ch3… 
                up to the length of the number of columns in the rawDF. 
                If the number is columns in the rawDF is smaller than what 
                is set in the number of channels spin, it goes the maximum 
                and returns a  warning.

                Get the new time values and channel values
                based on the users input.

                If these inputs are not floatable,
                it will return an error.

            #6.	By the end of the routine it will put the data in the 
                previewTextBox and enable the acceptButton and the visualization
                button in the dock widget;

            #7.	The name of each column here is ch1, ch2… For each of these
                columns, it will make each variable stored in the dictionary
                showingChannelsControl True

            ##########################################################    
        """

        try:
            # 1
            self.rawDF = pd.DataFrame()
            self.previewDF = pd.DataFrame()

            if self.timeUnitInput.text():
                self.timeUnitStr = self.timeUnitInput.text()
            else:
                self.timeUnitStr = 'unit'

            if self.channelsUnitInput.text():
                self.channelsUnitStr = self.channelsUnitInput.text()
            else:
                self.channelsUnitStr = 'unit'

            self.numberOfChannels = self.numberOfChannelsSpin.value()

            # make sure every showchannel is False in the beginning
            for key in self.showingChannelsControl:
                self.showingChannelsControl[key] = False

            # 2
            if self.tabSeparatorOpt.isChecked():
                self.separator = self.separatorList[0]

            elif self.commaSeparatorOpt.isChecked():
                self.separator = self.separatorList[1]

            elif self.spaceSeparatorOpt.isChecked():
                self.separator = self.separatorList[2]

            elif self.semicolonSeparatorOpt.isChecked():
                self.separator = self.separatorList[3]

            # 3
            self.rawDF = pd.read_csv(
                self.fileName, sep=self.separator, header=None)

            # 4
            if len(self.rawDF.columns) == 1:
                self.warningDialog('Invalid column separator!')

            # 5
            else:
                """for referencing in the code, there is a colX list
                    to get the lists of the rawDF"""

                self.rawDFColNames = []

                for i in range(len(self.rawDF.columns)):
                    self.rawDFColNames.append(f'col{i}')

                self.rawDF.columns = self.rawDFColNames

                # here it assumes that the first column is the time data
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

                    self.warningDialog(
                        f'For this dataset the max \n number of Channels is {len(self.rawDF.columns)-1}')

                    self.numberOfChannelsSpin.setValue(
                        len(self.rawDF.columns)-1)

                self.previewDF.set_index('Time', inplace=True)

                if self.timeFactorStr.text():
                    try:
                        self.timeFactor = float(self.timeFactorStr.text())

                    except ValueError:
                        self.warningDialog(
                            'Invalid time factor !')

                else:
                    self.timeFactor = 1

                if self.channelsFactorStr.text():
                    try:
                        self.channelFactor = float(
                            self.channelsFactorStr.text())

                    except ValueError:
                        self.warningDialog('Invalid channel factor !')

                else:
                    self.channelFactor = 1

                # 6
                self.previewDF.index = self.previewDF.index/self.timeFactor

                for i in range(len(self.previewDF.columns)):
                    colName = self.previewDF.columns[i]
                    self.previewDF[colName] = self.previewDF[colName] / \
                        self.channelFactor

                self.previewTextBox.setText(
                    self.previewDF.to_string(max_rows=10, float_format='%10.2f', justify='match-parent'))

                self.acceptBtnImportDlg.setDisabled(False)
                self.visualizationBtn.setDisabled(False)

                # 7
                for i in self.previewDF.columns:
                    self.showingChannelsControl[i] = True

        except:
            self.warningDialog('Error :(\t Check your dataset!')

    def setVisualizationDF(self):
        """
            ##########################################################

            This function is called by the plot button (plotVisDataBtn)
            in the visualization dialog box. It will run the following
            steps:

            #1. Empty the visualizationDF;

            #2. Check if the user has entered values to start and end time.
                If so, it will assign the variable startVisualizationTime and
                endVisualizationTime to the closest value that the user has entered.
                If there is none, it will get the first and/or last values from
                the previewDF;

            #3. Then, it makes the visualizationDF equals previewDF but with 
                the interval between startVisualizationTime and 
                endVisualizationTime of the previewDF;

            #4.	It checks if the user wants to set the time to zero. If so, 
                it will subtract the startVisualizationTime of the time data
                in the visualizationDF;

            #5. Creates and populate a list (showingChannelsList) with the 
                channels selected. Each of the checkbox was already made enabled
                or disabled after values present in the showingChannelsControl 
                that ware set in the step #8 of previewData function.

            #6. If the users do not select at least one channel, it returns an error,
                else, it makes the visualizationDF equals itself but with only these 
                columns, make the buttons response, and export available and plot
                the visualization data.

            #7.	Finally, it creates the propertiesTableColNames and settingColumnOrderList.
                Both lists are going to be used in the calculation parameters. First it 
                calculates each channels, then it sets the propertiesDF in order more
                appealing to the user This is based on what columns are inside the
                visualizationDF.

            #8. Calls the  plotVisualizationData function

            ##########################################################
        """
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
                self.warningDialog('No data Select')
                self.plotPreviewDF()
                self.responseBtn.setDisabled(True)
                self.exportBtn.setDisabled(True)

            else:
                self.visualizationDF = self.visualizationDF[self.showingChannelsList]

                if len(self.visualizationDF.columns) > 1:

                    self.normalizationBtn.setDisabled(False)

                # 7
                self.propertiesTableColNames = []
                self.propertiesTableColNames.append('concentration')

                for column in self.visualizationDF.columns:
                    self.propertiesTableColNames.append(f'{column} resp')
                    self.propertiesTableColNames.append(f'{column} respTime')
                    self.propertiesTableColNames.append(f'{column} recTime')

                self.settingColumnOrderList = []
                self.settingColumnOrderList.append('concentration')

                for column in self.visualizationDF.columns:
                    self.settingColumnOrderList.append(f'{column} resp')

                for column in self.visualizationDF.columns:
                    self.settingColumnOrderList.append(
                        f'{column} respTime')

                for column in self.visualizationDF.columns:
                    self.settingColumnOrderList.append(
                        f'{column} recTime')

                # 8
                self.responseBtn.setDisabled(False)
                self.exportBtn.setDisabled(False)
                self.plotVisualizationData()

        except ValueError:
            self.warningDialog('Invalid Parameters!')

    def setNormalizationDF(self):
        """
            ##########################################################
            
            This function will normalize the data inside the visualizationDF
            as long as it has at least two columns by dividing each column
            by its own value at the chosentime. It runs the following steps:

            #1. Empty the normalizationDF;

            #2.	If there is text in the normTimeInput, it makes the 
                normalizationPoint as the closest value from the user’s input.

            #3.	It makes the normalizationDF indexes the same as the
                visualizationDF;

            #4.	Then it inserts the visualization data divided by the 
                normalizationPoint;

            #5.	Calls plotNormalizationData;

            ##########################################################
        """

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
            self.warningDialog('Invalid parameter!')

    def calcResponse(self):
        """
            ##########################################################

            This function calculates the response, the response Time
            and the recovery time of a given exposure-recovery cycle
            for all channels present in the visualizationDF.

            This function is called by pressing the calcRespBtn on the 
            responseDlg. The system does that by running the following
            steps:

            #1.	After entering the concentration, start of exposure time,
                end of exposure time, and end of recovery time, it will
                look into the visualizationDF for the closest values present
                in the data table. It will assign the variables 
                startExposureTime, endExposureTime, endRecoveryTime with these 
                values. Finally, It creates two temporary DF to hold the response
                and recovery data;

            #2.	Creates a list called properties list and append the concentration
                value to it For each column in the visualizationDF it will find 
                the initial resistance r0, final exposure resistance rf, and final 
                recovery resistance rf2. These values correspond to the resistance 
                values of startExposureTime, endExposureTime, endRecoveryTime, 
                respectively.

            #3.	Calculates the absolute variations in the adsorption and 
                desorption cycles;

            #4. It calculates the response according to the user’s settings (in the 
                settings dialog). The default is dR/R0 in %. For each type of response,
                if the user has selected the sensitivity option, the response will
                be given by dividing the actual response by the concentration

            #5.	Calculate the values corresponding to 90% respose and recovery
                variation, and finds the corresponding values in the visualizationDF.
                The routine is different if the  resistance variation is positive
                or negative.

                This variation depends on the nature of the semiconductor
                material/gas interaction;

            #6.	Find the time in the time table corresponding to these values,
                and subtracts the startExposureTime, endExposureTime to
                calculate the response time and recovery time, respectively;

            #7. If the resp/rec times are negative, it will warn the user;

            #8.	Append the values of response, response time and recovery time
                to the properties list, set the append button enabled,

            #9. Update the channel 1 preview panel and if the propertiesDF has 
                at least three rows, it opens the enables the button in the
                dock widget for the powerLaw fit.

            ##########################################################  
        """

        try:
            # 1
            self.startExposureTime = min(self.visualizationDF.index, key=lambda x: abs(
                float(self.initialExpTimeInput.text())-x))

            self.endExposureTime = min(self.visualizationDF.index, key=lambda x: abs(
                float(self.finalExpTimeInput.text())-x))

            self.endRecoveryTime = min(self.visualizationDF.index, key=lambda x: abs(
                float(self.finalRecTimeInput.text())-x))

            self.analysisRespDF = self.visualizationDF[self.startExposureTime:self.endExposureTime]
            self.analysisRecDF = self.visualizationDF[self.endExposureTime:self.endRecoveryTime]

            # 2
            self.propertiesList = []
            self.propertiesList.append(float(self.concentrationInput.text()))

            for colName in self.visualizationDF.columns:

                self.r0 = self.analysisRespDF[colName][self.startExposureTime]
                self.rf = self.analysisRespDF[colName][self.endExposureTime]
                self.rf2 = self.analysisRecDF[colName][self.endRecoveryTime]

                # 3
                self.deltaR1 = abs(self.rf-self.r0)
                self.deltaR2 = abs(self.rf2-self.rf)

                # 4
                if self.responseType['dR/R0']:
                    self.response = (self.deltaR1*100)/self.r0

                    if self.responseType['sigconc']:
                        self.response = self.response / \
                            float(self.concentrationInput.text())

                elif self.responseType['dR']:
                    self.response = self.rf-self.r0

                    if self.responseType['sigconc']:
                        self.response = self.response / \
                            float(self.concentrationInput.text())

                elif self.responseType['Rgas/Rair']:
                    self.response = self.rf/self.r0

                    if self.responseType['sigconc']:
                        self.response = self.response / \
                            float(self.concentrationInput.text())

                # 5
                if self.rf > self.r0:
                    self.resp90Resistance = min(
                        self.analysisRespDF[colName], key=lambda x: abs(((self.r0+(0.9*self.deltaR1))-x)))

                    self.rec90Resistance = min(self.analysisRecDF[colName], key=lambda x: abs(
                        ((self.rf-(0.9*self.deltaR2))-x)))

                else:
                    self.resp90Resistance = min(
                        self.analysisRespDF[colName], key=lambda x: abs(((self.r0-(0.9*self.deltaR1))-x)))

                    self.rec90Resistance = min(self.analysisRecDF[colName], key=lambda x: abs(
                        ((self.rf+(0.9*self.deltaR2))-x)))

                # 6
                self.responseTime = self.analysisRespDF[self.analysisRespDF[colName] == self.resp90Resistance].index.tolist()[
                    0]-self.startExposureTime

                self.recoveryTime = self.analysisRecDF[self.analysisRecDF[colName] == self.rec90Resistance].index.tolist()[
                    0]-self.endExposureTime

                # 7
                if self.responseTime < 0 or self.recoveryTime < 0:
                    self.warningDialog(
                        'Negative resp/rec time!\t Verify your cycle time values!')

                # 8
                self.propertiesList.append(self.response)
                self.propertiesList.append(self.responseTime)
                self.propertiesList.append(self.recoveryTime)

            # 9
            self.calcSensitivityResult.setText(f'{self.propertiesList[1]:.3f}')
            self.calcRespTimeResult.setText(f'{self.propertiesList[2]:.3f}')
            self.calcRecoveryTimeResult.setText(
                f'{self.propertiesList[3]:.3f}')

            self.appendRespBtn.setDisabled(False)

            if len(self.propertiesDF.index) > 1:
                self.fitBtn.setDisabled(False)

        except:
            self.warningDialog('Invalid values!')

    def appendResponseToDF(self):
        """
            ##########################################################

            This function gets the propertiesList and added to the 
            propertiesDF. It does that by:

            #1. converting this list into a pandas’ series with the
                propertiesTableColNames and the name being the 
                concentration value;

            #2. This series becomes the row that is appended to the 
                propertiesDF. then it it put in order, response first,
                response time second, recovery time third.

            #3. It updates the text shown in the 
                sensorPropertiesTablePreview;

            ##########################################################
        """

        try:
            # 1
            self.newResponseRow = pd.Series(self.propertiesList,
                                            index=self.propertiesTableColNames)

            # 2
            self.propertiesDF = self.propertiesDF.append(
                self.newResponseRow, ignore_index=True)

            self.propertiesDF.index = self.propertiesDF.index + 1
            self.propertiesDF.index.name = 'cycle'

            self.propertiesDF = self.propertiesDF[self.settingColumnOrderList]

            # 3
            self.sensorPropertiesTablePreview.setText(self.propertiesDF.to_string(
                float_format='%10.2f', justify='match-parent'))
        except:
            self.warningDialog('Error!')

    def clearLastResponseDF(self):
        """
            ##########################################################

            The user can clear the last line of the properties DF to
            start over

            ##########################################################
        """

        if self.propertiesDF.index.empty:
            self.warningDialog('The DF is empty!')
        else:
            self.propertiesDF.drop(
                axis=0, index=self.propertiesDF.last_valid_index(), inplace=True)

            self.sensorPropertiesTablePreview.setText(self.propertiesDF.to_string(
                float_format='%10.2f', justify='match-parent'))

    def clearAllResponseDF(self):
        """
            ##########################################################

            The user can clear the the properties DF to
            start over

            ##########################################################
        """

        if self.propertiesDF.index.empty:
            self.warningDialog('The DF is empty!')
        else:
            self.propertiesDF = pd.DataFrame ()

            self.sensorPropertiesTablePreview.setText(self.propertiesDF.to_string())

    def powerLawFunc(self, x, a, b):
        return a*(x**b)

    def fitRespData(self):
        """
            ##########################################################

            This function will fit the response data to the powerLawFunc
            described previously. It does it by using the curve_fit from
            the scipy.optmize. The algorithm run as follows:

            #1.	Empty the fitDF;

            #2.	Calculate the fitting step by dividing the last data point 
                from the propertiesDF concentration column by the numberOfFitPoints
                that can be entered in the settings menu. If the last concentration
                is 5, and the number of points is 100, each step will be equal 
                to 0.05;

            #3.	Enter the values in the x_fit_values that represent the 
                concentration values according to the step value, and 
                starting at zero;


            #4.	Insert these values in the fitDF;

            #5.	For each column in the propertiesDF it will fit the curve
                using the function curve_fit and it uses the visualizationDF.columns
                to get the proper names of each column. This is important
                because the user can choose any sort of combination of channels 
                to fit; 

            #6.	The curve_fit function returns the coefficient that are added to the
                coef1_list and coef2_list. Each of these lists will hold a number 
                of values equivalent to the number of columns analyzed.

            #7.	Creates a str with this information that will be used in the legend
                when plotting. These strings are stored in the variable fitListLabel

            #8.	It calculates the y_fit_values and add to the fitDF;

            #9.	Call the function plotRespData that plots both
                the fitDF and the response data from propertiesDF;

            #10. If the user has chosen to calculate sensitivity, this function
                will carry out a linear regression between the data of concentration
                and the response data, and it will show both the slope as sensitivity
                and the R-squared value.

            ##########################################################
        """
        
        # 1
        self.fitDF = pd.DataFrame()
        self.x_fit_values = []
        self.fitListLabel = []
        self.sensitivityList = []
        self.sensitivityRValues = []

        # 2
        step = max(self.propertiesDF['concentration'])/self.numberOfFitPoints

        # 3
        for i in range(self.numberOfFitPoints):
            if len(self.x_fit_values) == 0:
                self.x_fit_values.append(0)
            else:
                self.x_fit_values.append(self.x_fit_values[-1]+step)

        # 4
        self.fitDF.insert(0, 'x_fit_values', self.x_fit_values)

        # 5
        for i, column in enumerate(self.visualizationDF.columns):
            name = f'y_fit_{i+1}'

            popt = optimize.curve_fit(self.powerLawFunc, self.propertiesDF['concentration'],
                             self.propertiesDF[f'{column} resp'])

            # 6
            self.coef1_list.append(popt[0][0])
            self.coef2_list.append(popt[0][1])

            # 7
            self.fitListLabel.append(
                f'fit {column}: a={popt[0][0]:.2f}, b={popt[0][1]:.2f}')

            # 8
            y_fit_values = self.powerLawFunc(
                self.x_fit_values, popt[0][0], popt[0][1])

            # 9
            self.fitDF.insert(i+1, name, y_fit_values)

            # 10
            if self.responseType['sensitivity']:
                regression = stats.linregress(self.propertiesDF['concentration'],
                                              self.propertiesDF[f'{column} resp'])

                self.sensitivityList.append(regression.slope)
                self.sensitivityRValues.append(regression.rvalue*regression.rvalue)

                if self.responseType['dR/R0']:
                    unit = f'%/{self.concentrationUnitStr}'
                    
                elif self.responseType['dR']:
                    unit = f'{self.channelsUnitStr}/{self.concentrationUnitStr}'

                elif self.responseType['Rgas/Rair']:
                    unit = f'/{self.concentrationUnitStr}'
                
                finalStrP1 = f'sensitivity = {self.sensitivityList[i]:.2f} {unit},'
                finalStrP2 = f' R-sq = {self.sensitivityRValues[i]:.3f}'
                
                self.sensitivityResultsList.append(finalStrP1+finalStrP2)

        self.fitDF.set_index('x_fit_values', inplace=True)
        self.plotFittedData()

    def getExportFileDirectory(self):
        """
            ##########################################################

            This function creates the string to the path to export the
            data.

            ##########################################################
        """

        self.exportDirectory = QFileDialog.getExistingDirectory(self.exportDlg)

        if self.exportDirectory:
            self.exportDlgBtn.setDisabled(False)

    def setSettings(self):
        """
            ##########################################################   

            This function will set the values chosen in the settings
            dialog box.

            #1. sets type of response type by assigning the to 
                responseType dic

            #2. sets the fitting number points

            #3. sets the matplotlib style

            #4. sets color pallet

            #5. plot with new settings

            ##########################################################
        """
        try:
            # 1
            if self.responseOpt1.isChecked():
                self.responseLabel = u'\u0394S/S0 (%)'
                self.responseType['dR/R0'] = True
                self.responseType['dR'] = False
                self.responseType['Rgas/Rair'] = False

            elif self.responseOpt2.isChecked():
                self.responseLabel = u'\u0394S '+f'({self.channelsUnitStr})'
                self.responseType['dR/R0'] = False
                self.responseType['dR'] = True
                self.responseType['Rgas/Rair'] = False

            elif self.responseOpt3.isChecked():
                self.responseLabel = u'Rgas/Rair (a.u.)'
                self.responseType['dR/R0'] = False
                self.responseType['dR'] = False
                self.responseType['Rgas/Rair'] = True

            if self.responseOpt4.isChecked():
                self.responseType['sigconc'] = True
                self.responseLabel = self.responseLabel + \
                    f'/{self.concentrationUnitStr}'

            elif not self.responseOpt4.isChecked():
                self.responseType['sigconc'] = False
            
            if self.sensitivityOpt.isChecked():
                self.responseType['sensitivity'] = True

            elif not self.sensitivityOpt.isChecked():
                self.responseType['sensitivity'] = False
            
            if self.responseOpt4.isChecked() and self.sensitivityOpt.isChecked():
                self.warningDialog('Please, select only one between sensitivity or signal/conc')
                self.responseOpt4.setChecked(False)
                self.sensitivityOpt.setChecked(False)
                self.responseType['sensitivity'] = False
                self.responseType['sigconc'] = False

            # 2
            if self.numberOfFitPointsInput.text():
                self.numberOfFitPoints = int(
                    self.numberOfFitPointsInput.text())

            if self.concentrationUnitInput.text():
                self.concentrationUnitStr = self.concentrationUnitInput.text()
            else:
                self.concentrationUnitStr = 'ppm'

            # 3
            if self.matplotlibStyleOpt1.isChecked():
                matplotlib.style.use('bmh')

            elif self.matplotlibStyleOpt2.isChecked():
                matplotlib.style.use('seaborn')

            elif self.matplotlibStyleOpt3.isChecked():
                matplotlib.style.use('grayscale')

            elif self.matplotlibStyleOpt4.isChecked():
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

            elif self.plottingControl['Response']:
                self.plotRespData()

            elif self.plottingControl['Fit']:
                self.plotFittedData()

            elif self.plottingControl['RespTime']:
                self.plotRespTimeData()

            elif self.plottingControl['RecTime']:
                self.plotRecTimeData()

            else:
                pass

        except ValueError:
            self.warningDialog('Invalid parameters!')

    def plotDataFrame(self, data_frame, x_axis_name,
                      y_axis_name, plot_titles, plot_labels,
                      number_of_axis, marker='', linestyle=''):
        """
            ##########################################################

            This function plots a data frame, sets its axis labels, 
            the title of the dataset and the labels, number of axis.
            Also, it offers the possibility to choose the marker and 
            linestyle.

            ##########################################################
        """
        self.data_frame = data_frame
        self.x_axis_name = x_axis_name
        self.y_axis_name = y_axis_name
        self.plot_titles = plot_titles
        self.plot_labels = plot_labels
        self.number_of_axis = number_of_axis
        self.marker = marker
        self.linestyle = linestyle

        self.mainFigure.clf()

        self.mainFigure.text(0.55, 0.025,
                             self.x_axis_name,
                             ha='center',
                             va='center',
                             fontsize=18)

        self.mainFigure.text(0.025, 0.5,
                             self.y_axis_name,
                             ha='center',
                             va='center',
                             rotation=90,
                             fontsize=18)

        if self.number_of_axis == 1:
            self.ax1 = self.mainFigure.add_subplot(111)
            self.ax1.set_title(self.plot_titles[0], visible=False)

            for i, column in enumerate(self.data_frame.columns):
                if self.marker:
                    self.ax1.plot(self.data_frame.iloc[:, i],
                                  color=self.palette[i],
                                  marker=self.marker,
                                  linestyle=self.linestyle,
                                  label=self.plot_labels[i])

                else:
                    self.ax1.plot(self.data_frame.iloc[:, i],
                                  color=self.palette[i],
                                  label=self.plot_labels[i])

            self.ax1.legend(loc='best', shadow=True)

        elif self.number_of_axis == 2:

            self.ax1 = self.mainFigure.add_subplot(211)
            self.ax1.set_title(self.plot_titles[0], visible=False)
            self.ax1.plot(self.data_frame.iloc[:, 0],
                          color=self.palette[0],
                          label=self.plot_labels[0])
            self.ax1.legend(loc='upper right', shadow=True)

            self.ax2 = self.mainFigure.add_subplot(212)
            self.ax2.set_title(self.plot_titles[1], visible=False)
            self.ax2.plot(self.data_frame.iloc[:, 1],
                          color=self.palette[1],
                          label=self.plot_labels[1])
            self.ax2.legend(loc='upper right', shadow=True)

        elif self.number_of_axis == 3:
            self.ax1 = self.mainFigure.add_subplot(221)
            self.ax1.set_title(self.plot_titles[0], visible=False)
            self.ax1.plot(self.data_frame.iloc[:, 0],
                          color=self.palette[0],
                          label=self.plot_labels[0])
            self.ax1.legend(loc='upper right', shadow=True)

            self.ax2 = self.mainFigure.add_subplot(222)
            self.ax2.set_title(self.plot_titles[1], visible=False)
            self.ax2.plot(self.data_frame.iloc[:, 1],
                          color=self.palette[1],
                          label=self.plot_labels[1])
            self.ax2.legend(loc='upper right', shadow=True)

            self.ax3 = self.mainFigure.add_subplot(223)
            self.ax3.set_title(self.plot_titles[2], visible=False)
            self.ax3.plot(self.data_frame.iloc[:, 2],
                          color=self.palette[2],
                          label=self.plot_labels[2])
            self.ax3.legend(loc='upper right', shadow=True)

        elif self.number_of_axis == 4:

            self.ax1 = self.mainFigure.add_subplot(221)
            self.ax1.set_title(self.plot_titles[0], visible=False)
            self.ax1.plot(self.data_frame.iloc[:, 0],
                          color=self.palette[0],
                          label=self.plot_labels[0])
            self.ax1.legend(loc='upper right', shadow=True)

            self.ax2 = self.mainFigure.add_subplot(222)
            self.ax2.set_title(self.plot_titles[1], visible=False)
            self.ax2.plot(self.data_frame.iloc[:, 1],
                          color=self.palette[1],
                          label=self.plot_labels[1])
            self.ax2.legend(loc='upper right', shadow=True)

            self.ax3 = self.mainFigure.add_subplot(223)
            self.ax3.set_title(self.plot_titles[2], visible=False)
            self.ax3.plot(self.data_frame.iloc[:, 2],
                          color=self.palette[2],
                          label=self.plot_labels[2])
            self.ax3.legend(loc='upper right', shadow=True)

            self.ax4 = self.mainFigure.add_subplot(224)
            self.ax4.set_title(self.plot_titles[3], visible=False)
            self.ax4.plot(self.data_frame.iloc[:, 3],
                          color=self.palette[3],
                          label=self.plot_labels[3])
            self.ax4.legend(loc='upper right', shadow=True)

        elif self.number_of_axis == 5:

            self.ax1 = self.mainFigure.add_subplot(231)
            self.ax1.set_title(self.plot_titles[0], visible=False)
            self.ax1.plot(self.data_frame.iloc[:, 0],
                          color=self.palette[0],
                          label=self.plot_labels[0])
            self.ax1.legend(loc='upper right', shadow=True)

            self.ax2 = self.mainFigure.add_subplot(232)
            self.ax2.set_title(self.plot_titles[1], visible=False)
            self.ax2.plot(self.data_frame.iloc[:, 1],
                          color=self.palette[1],
                          label=self.plot_labels[1])
            self.ax2.legend(loc='upper right', shadow=True)

            self.ax3 = self.mainFigure.add_subplot(233)
            self.ax3.set_title(self.plot_titles[2], visible=False)
            self.ax3.plot(self.data_frame.iloc[:, 2],
                          color=self.palette[2],
                          label=self.plot_labels[2])
            self.ax3.legend(loc='upper right', shadow=True)

            self.ax4 = self.mainFigure.add_subplot(234)
            self.ax4.set_title(self.plot_titles[3], visible=False)
            self.ax4.plot(self.data_frame.iloc[:, 3],
                          color=self.palette[3],
                          label=self.plot_labels[3])
            self.ax4.legend(loc='upper right', shadow=True)

            self.ax5 = self.mainFigure.add_subplot(235)
            self.ax5.set_title(self.plot_titles[4], visible=False)
            self.ax5.plot(self.data_frame.iloc[:, 4],
                          color=self.palette[4],
                          label=self.plot_labels[4])
            self.ax5.legend(loc='upper right', shadow=True)

        elif self.number_of_axis == 6:

            self.ax1 = self.mainFigure.add_subplot(231)
            self.ax1.set_title(self.plot_titles[0], visible=False)
            self.ax1.plot(self.data_frame.iloc[:, 0],
                          color=self.palette[0],
                          label=self.plot_labels[0])
            self.ax1.legend(loc='upper right', shadow=True)

            self.ax2 = self.mainFigure.add_subplot(232)
            self.ax2.set_title(self.plot_titles[1], visible=False)
            self.ax2.plot(self.data_frame.iloc[:, 1],
                          color=self.palette[1],
                          label=self.plot_labels[1])
            self.ax2.legend(loc='upper right', shadow=True)

            self.ax3 = self.mainFigure.add_subplot(233)
            self.ax3.set_title(self.plot_titles[2], visible=False)
            self.ax3.plot(self.data_frame.iloc[:, 2],
                          color=self.palette[2],
                          label=self.plot_labels[2])
            self.ax3.legend(loc='upper right', shadow=True)

            self.ax4 = self.mainFigure.add_subplot(234)
            self.ax4.set_title(self.plot_titles[3], visible=False)
            self.ax4.plot(self.data_frame.iloc[:, 3],
                          color=self.palette[3],
                          label=self.plot_labels[3])
            self.ax4.legend(loc='upper right', shadow=True)

            self.ax5 = self.mainFigure.add_subplot(235)
            self.ax5.set_title(self.plot_titles[4], visible=False)
            self.ax5.plot(self.data_frame.iloc[:, 4],
                          color=self.palette[4],
                          label=self.plot_labels[4])
            self.ax5.legend(loc='upper right', shadow=True)

            self.ax6 = self.mainFigure.add_subplot(236)
            self.ax6.set_title(self.plot_titles[5], visible=False)
            self.ax6.plot(self.data_frame.iloc[:, 5],
                          color=self.palette[5],
                          label=self.plot_labels[5])
            self.ax6.legend(loc='upper right', shadow=True)

        elif self.number_of_axis == 7:

            self.ax1 = self.mainFigure.add_subplot(241)
            self.ax1.set_title(self.plot_titles[0], visible=False)
            self.ax1.plot(self.data_frame.iloc[:, 0],
                          color=self.palette[0],
                          label=self.plot_labels[0])
            self.ax1.legend(loc='upper right', shadow=True)

            self.ax2 = self.mainFigure.add_subplot(242)
            self.ax2.set_title(self.plot_titles[1], visible=False)
            self.ax2.plot(self.data_frame.iloc[:, 1],
                          color=self.palette[1],
                          label=self.plot_labels[1])
            self.ax2.legend(loc='upper right', shadow=True)

            self.ax3 = self.mainFigure.add_subplot(243)
            self.ax3.set_title(self.plot_titles[2], visible=False)
            self.ax3.plot(self.data_frame.iloc[:, 2],
                          color=self.palette[2],
                          label=self.plot_labels[2])
            self.ax3.legend(loc='upper right', shadow=True)

            self.ax4 = self.mainFigure.add_subplot(244)
            self.ax4.set_title(self.plot_titles[3], visible=False)
            self.ax4.plot(self.data_frame.iloc[:, 3],
                          color=self.palette[3],
                          label=self.plot_labels[3])
            self.ax4.legend(loc='upper right', shadow=True)

            self.ax5 = self.mainFigure.add_subplot(245)
            self.ax5.set_title(self.plot_titles[4], visible=False)
            self.ax5.plot(self.data_frame.iloc[:, 4],
                          color=self.palette[4],
                          label=self.plot_labels[4])
            self.ax5.legend(loc='upper right', shadow=True)

            self.ax6 = self.mainFigure.add_subplot(246)
            self.ax6.set_title(self.plot_titles[5], visible=False)
            self.ax6.plot(self.data_frame.iloc[:, 5],
                          color=self.palette[5],
                          label=self.plot_labels[5])
            self.ax6.legend(loc='upper right', shadow=True)

            self.ax7 = self.mainFigure.add_subplot(246)
            self.ax7.set_title(self.plot_titles[6], visible=False)
            self.ax7.plot(self.data_frame.iloc[:, 6],
                          color=self.palette[6],
                          label=self.plot_labels[6])
            self.ax7.legend(loc='upper right', shadow=True)

        else:
            self.ax1 = self.mainFigure.add_subplot(241)
            self.ax1.set_title(self.plot_titles[0], visible=False)
            self.ax1.plot(self.data_frame.iloc[:, 0],
                          color=self.palette[0],
                          label=self.plot_labels[0])
            self.ax1.legend(loc='upper right', shadow=True)

            self.ax2 = self.mainFigure.add_subplot(242)
            self.ax2.set_title(self.plot_titles[1], visible=False)
            self.ax2.plot(self.data_frame.iloc[:, 1],
                          color=self.palette[1],
                          label=self.plot_labels[1])
            self.ax2.legend(loc='upper right', shadow=True)

            self.ax3 = self.mainFigure.add_subplot(243)
            self.ax3.set_title(self.plot_titles[2], visible=False)
            self.ax3.plot(self.data_frame.iloc[:, 2],
                          color=self.palette[2],
                          label=self.plot_labels[2])
            self.ax3.legend(loc='upper right', shadow=True)

            self.ax4 = self.mainFigure.add_subplot(244)
            self.ax4.set_title(self.plot_titles[3], visible=False)
            self.ax4.plot(self.data_frame.iloc[:, 3],
                          color=self.palette[3],
                          label=self.plot_labels[3])
            self.ax4.legend(loc='upper right', shadow=True)

            self.ax5 = self.mainFigure.add_subplot(245)
            self.ax5.set_title(self.plot_titles[4], visible=False)
            self.ax5.plot(self.data_frame.iloc[:, 4],
                          color=self.palette[4],
                          label=self.plot_labels[4])
            self.ax5.legend(loc='upper right', shadow=True)

            self.ax6 = self.mainFigure.add_subplot(246)
            self.ax6.set_title(self.plot_titles[5], visible=False)
            self.ax6.plot(self.data_frame.iloc[:, 5],
                          color=self.palette[5],
                          label=self.plot_labels[5])
            self.ax6.legend(loc='upper right', shadow=True)

            self.ax7 = self.mainFigure.add_subplot(247)
            self.ax7.set_title(self.plot_titles[6], visible=False)
            self.ax7.plot(self.data_frame.iloc[:, 6],
                          color=self.palette[6],
                          label=self.plot_labels[6])
            self.ax7.legend(loc='upper right', shadow=True)

            self.ax8 = self.mainFigure.add_subplot(248)
            self.ax8.set_title(self.plot_titles[7], visible=False)
            self.ax8.plot(self.data_frame.iloc[:, 7],
                          color=self.palette[7],
                          label=self.plot_labels[7])
            self.ax8.legend(loc='upper right', shadow=True)

        self.mainFigure.subplots_adjust(top=0.975,
                                        bottom=0.09,
                                        left=0.075,
                                        right=0.975,
                                        hspace=0.15,
                                        wspace=0.15)

        self.mainFigureCanvas.draw()

    def plotPreviewDF(self):
        """
            ##########################################################    

            This function first adjusts the plotting control to the 
            previewDW and then it plots it using the plotDataFrame
            function.

            ##########################################################
        """

        if self.previewDF.empty:
            self.warningDialog('Empty Data Frame!')

        else:
            for key in self.plottingControl.keys():
                self.plottingControl[key] = False

            self.plottingControl['previewDF'] = True

            self.plotDataFrame(data_frame=self.previewDF,
                               x_axis_name=f'Time ({self.timeUnitStr})',
                               y_axis_name=f'Sensor data ({self.channelsUnitStr})',
                               plot_titles=self.previewDF.columns,
                               plot_labels=self.previewDF.columns,
                               number_of_axis=len(self.previewDF.columns))

    def plotVisualizationData(self):
        """
            ##########################################################

            This function first adjusts the plotting control to the
            previewDW and then it plots it using the plotDataFrame
            function.

            ##########################################################
        """

        if self.visualizationDF.empty:
            self.warningDialog('Empty Data Frame!')

        else:
            for key in self.plottingControl.keys():
                self.plottingControl[key] = False

            self.plottingControl['visualizationDF'] = True

            self.plotDataFrame(data_frame=self.visualizationDF,
                               x_axis_name=f'Time ({self.timeUnitStr})',
                               y_axis_name=f'Sensor data ({self.channelsUnitStr})',
                               plot_titles=self.visualizationDF.columns,
                               plot_labels=self.visualizationDF.columns,
                               number_of_axis=len(self.visualizationDF.columns))

    def plotNormalizationData(self):
        """
            ##########################################################

            This function plots the normalizedDF in one axis.

            ##########################################################
        """

        if self.normalizationDF.empty:
            self.warningDialog('Empty Data Frame!')

        else:
            for key in self.plottingControl.keys():
                self.plottingControl[key] = False

            self.plottingControl['normalizationDF'] = True

            self.plotDataFrame(data_frame=self.normalizationDF,
                               x_axis_name=f'{self.normalizationDF.index.name} ({self.timeUnitInput.text()})',
                               y_axis_name='Normalized Resistance (arb. units)',
                               plot_titles=['Normalization'],
                               plot_labels=self.visualizationDF.columns,
                               number_of_axis=1)

    def plotRespData(self):
        """
            ##########################################################
            
            This function will plot the response data. 
            
            ##########################################################
        """

        if self.propertiesDF.empty:
            self.warningDialog('Properties DF is empty!')

        else:
            for key in self.plottingControl.keys():
                self.plottingControl[key] = False

            self.plottingControl['Response'] = True

            self.respDF = pd.DataFrame()

            self.respDF.insert(0, 'concentration',
                               value=self.propertiesDF['concentration'])

            for i, column in enumerate(self.visualizationDF.columns):
                self.respDF.insert(i+1, column+' resp',
                                   value=self.propertiesDF[column+' resp'])

            self.respDF.set_index('concentration', inplace=True)

            self.plotDataFrame(self.respDF,
                               x_axis_name=f'Concentration ({self.concentrationUnitStr})',
                               y_axis_name=self.responseLabel,
                               plot_titles=['Response'],
                               plot_labels=self.visualizationDF.columns,
                               number_of_axis=1,
                               marker='o')

    def plotFittedData(self):
        """
            ##########################################################

            This function will plot the response and the fitting data.

            ##########################################################
        """

        if self.fitDF.empty:
            self.warningDialog('Properties DF is empty!')

        else:
            self.plotRespData()

            for key in self.plottingControl.keys():
                self.plottingControl[key] = False

            self.plottingControl['Fit'] = True

            for i, column in enumerate(self.visualizationDF.columns):
                
                legend = f'{self.fitListLabel[i]}'

                if self.responseType['sensitivity'] and self.sensitivityList:
                    legend = legend + '\n' + self.sensitivityResultsList[i]

                self.ax1.plot(self.fitDF.iloc[:, i],
                              linestyle='dashed',
                              color=self.palette[i],
                              label=legend)

            self.ax1.legend(loc='best', shadow=True)
            self.mainFigureCanvas.draw()

    def plotRespTimeData(self):
        """
            ##########################################################

            This function will plot the response time versus concentration

            ##########################################################
        """
        if self.propertiesDF.empty:
            self.warningDialog('The properties DF is empty!')

        else:
            for key in self.plottingControl.keys():
                self.plottingControl[key] = False

            self.plottingControl['RespTime'] = True

            self.respTimeDF = pd.DataFrame()

            self.respTimeDF.insert(
                0, 'concentration', value=self.propertiesDF['concentration'])

            for i, column in enumerate(self.visualizationDF.columns):
                self.respTimeDF.insert(
                    i+1, column+' respTime', value=self.propertiesDF[column+' respTime'])

            self.respTimeDF.set_index('concentration', inplace=True)

            self.plotDataFrame(self.respTimeDF,
                               x_axis_name=f'Concentration ({self.concentrationUnitStr})',
                               y_axis_name=f'Response time ({self.timeUnitStr})',
                               plot_titles=['Resp time'],
                               plot_labels=self.visualizationDF.columns,
                               number_of_axis=1,
                               marker='o',
                               linestyle='dashed')

    def plotRecTimeData(self):
        """
            ##########################################################

            This function will plot the recovery time versus concentration

            ##########################################################
        """

        if self.propertiesDF.index.empty:
            self.warningDialog('The properties DF is empty!')

        else:
            for key in self.plottingControl.keys():
                self.plottingControl[key] = False

            self.plottingControl['RecTime'] = True

            self.recTimeDF = pd.DataFrame()

            self.recTimeDF.insert(0, 'concentration',
                                  value=self.propertiesDF['concentration'])

            for i, column in enumerate(self.visualizationDF.columns):
                self.recTimeDF.insert(
                    i+1, column+' recTime', value=self.propertiesDF[column+' recTime'])

            self.recTimeDF.set_index('concentration', inplace=True)

            self.plotDataFrame(self.recTimeDF,
                               x_axis_name=f'Concentration ({self.concentrationUnitStr})',
                               y_axis_name=f'Recovery time ({self.timeUnitStr})',
                               plot_titles=['Rec time'],
                               plot_labels=self.visualizationDF.columns,
                               number_of_axis=1,
                               marker='o',
                               linestyle='dashed')

    def exportData(self):
        """
            ##########################################################

            This function will export the data frames into CSV files
            according to the folder that the user has chosen

            # 1 Gets the export file names from the input box

            # 2 Create paths according to the exportDirectory
                from the getExportFileDirectory function

            # 3 Creates an header in each file containing the date time
                and the name of the analysis chosen by the user. 
                Export the data that is checked. The check boxes are disabled
                if there is no data in the respective dataFrame. The fitDF
                generates two tables, one with the data, another with the
                fit info

            ##########################################################
        """

        # 1
        self.exportFileName = self.exportFileNameInput.text()

        # 2
        self.path1 = self.exportDirectory+'/'+self.exportFileName+' VIS_DATA.dat'
        self.path2 = self.exportDirectory+'/'+self.exportFileName+' NORM_DATA.dat'
        self.path3 = self.exportDirectory+'/'+self.exportFileName+' RESPONSE_DATA.dat'
        self.path4 = self.exportDirectory+'/'+self.exportFileName+' FIT_INFO.dat'
        self.path5 = self.exportDirectory+'/'+self.exportFileName+' FIT_DATA.dat'

        # 3
        t = datetime.now()

        if self.exportVisDataCheck.isChecked():
            self.visDataFile = open(self.path1, 'w')
            self.visDataFile.write(f'# {t.strftime("%m/%d/%Y, %H:%M:%S")} \n')
            self.visDataFile.write(f'# {self.exportFileName} \n\n')
            self.visDataFile.write(f'# Visualization data\n')
            self.visDataFile.write(f'# time unit: {self.timeUnitStr}\n')
            self.visDataFile.write(
                f'# channels unit: {self.channelsUnitStr}\n\n\n')
            self.visDataFile.close()

            self.visualizationDF.to_csv(
                self.path1, float_format='%10.4f', sep=self.separator, mode='a', index=True)

        if self.exportNormDataCheck.isChecked():
            self.normDataFile = open(self.path2, 'w')
            self.normDataFile.write(f'# {t.strftime("%m/%d/%Y, %H:%M:%S")} \n')
            self.normDataFile.write(f'# {self.exportFileName} \n\n')
            self.normDataFile.write(f'# Normalization data\n')
            self.normDataFile.write(f'# time unit: {self.timeUnitStr}\n')
            self.normDataFile.write(
                f'# normalization point: {self.normalizationPoint} {self.timeUnitStr}\n\n\n')
            self.normDataFile.close()

            self.normalizationDF.to_csv(
                self.path2, float_format='%10.7f', sep=self.separator, mode='a', index=True)

        if self.exportPropDataCheck.isChecked():
            self.propDataFile = open(self.path3, 'w')
            self.propDataFile.write(f'# {t.strftime("%m/%d/%Y, %H:%M:%S")} \n')
            self.propDataFile.write(f'# {self.exportFileName} \n\n')
            self.propDataFile.write(f'# Properties data \n')

            if self.responseType['dR/R0']:
                if self.responseType['sigconc']:
                    self.propDataFile.write(
                        f'# Response in %/{self.concentrationUnitStr}\n')
                else:
                    self.propDataFile.write(f'# Response in %\n')

            elif self.responseType['dR']:
                if self.responseType['sigconc']:
                    self.propDataFile.write(
                        f'# Response in {self.channelsUnitStr}/{self.concentrationUnitStr}\n')
                else:
                    self.propDataFile.write(
                        f'# Response in {self.channelsUnitStr}\n')

            elif self.responseType['Rgas/Rair']:
                if self.responseType['sigconc']:
                    self.propDataFile.write(
                        f'# Response in Rgas/Rair/{self.concentrationUnitStr}\n')
                else:
                    self.propDataFile.write(f'# Response in a.u. (Rgas/Rair)\n')

            self.propDataFile.write(
                f'# Resp and Rec times unit: {self.timeUnitStr}\n\n\n')
            self.propDataFile.close()

            self.propertiesDF.to_csv(
                self.path3, float_format='%10.3f', sep=self.separator, mode='a', index=True)

        if self.exportFitInfoCheck.isChecked():
            self.fitDataFile = open(self.path4, 'w')
            self.fitDataFile.write(f'# {t.strftime("%m/%d/%Y, %H:%M:%S")} \n')
            self.fitDataFile.write(f'# {self.exportFileName} \n\n')

            self.fitDataFile.write('Power Law Fit function\n')
            self.fitDataFile.write('Response = a*(Conc.)^b\n\n\n')

            for i, label in enumerate(self.fitListLabel):
                self.fitDataFile.write(label+'\n')
            
                if self.responseType['sensitivity']:
                    self.fitDataFile.write(self.sensitivityResultsList[i]+'\n')

            self.fitDataFile.close()

            self.fitDataFile2 = open(self.path5, 'w')
            self.fitDataFile2.write(f'# {t.strftime("%m/%d/%Y, %H:%M:%S")} \n')
            self.fitDataFile2.write(f'# {self.exportFileName} \n\n')
            self.fitDataFile2.write(f'# Power Law Fit data\n\n\n')
            self.fitDataFile2.close()

            self.fitDF.to_csv(self.path5, float_format='%10.3f',
                              sep=self.separator, mode='a', index=True)

        self.warningDialog('Export done!')

    def showAboutDialog(self):
        """
            ##########################################################

            Opens up the About Dialog

            ##########################################################
        """

        self.aboutDlg = QDialog()
        self.aboutDlg.setFixedSize(300, 400)
        self.aboutDlg.setWindowFlag(
            QtCore.Qt.WindowContextHelpButtonHint, on=False)
        self.aboutDlg.setWindowTitle('About')

        self.aboutLbl1 = QLabel(self.aboutDlg)
        self.aboutLbl1.setText('Gas Sensor Data Analysis system')
        self.aboutLbl1.setAlignment(QtCore.Qt.AlignLeft)
        self.aboutLbl1.setSizePolicy(
            QSizePolicy.Maximum, QSizePolicy.Maximum)

        self.aboutLbl2 = QLabel(self.aboutDlg)
        self.aboutLbl2.setText('Beta Version 0.9.3')
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

    def warningDialog(self, message):
        """
            ##########################################################

            Warning box for error handling.

            ##########################################################
        """

        self.message = message

        self.warningBox = QMessageBox()
        self.warningBox.setIcon(QMessageBox.Warning)
        self.warningBox.setWindowTitle('Warning')
        self.warningBox.setText(self.message)
        self.warningBox.exec_()

    def closeEvent(self, event):
        """
            ##########################################################

            Close event with a message to confirm.

            ##########################################################
        """
        self.warningBox_2 = QMessageBox.question(self,
                                                 'Close window',
                                                 'Would you like to quit?',
                                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if self.warningBox_2 == QMessageBox.Yes:
            event.accept()

        else:
            event.ignore()

    def saveHighQualityFig(self):
        self.mainFigure.savefig('test.svg', dpi=300)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GasSensorDataAnalysisSystem()
    window.show()
    sys.exit(app.exec_())
