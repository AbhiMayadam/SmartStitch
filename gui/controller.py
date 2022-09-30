import os

from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QDialog, QFileDialog

from assets.SmartStitchLogo import icon
from core.services import SettingsHandler
from core.utils.constants import OUTPUT_SUFFIX
from gui.process import GuiStitchProcess

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))


class ProcessThread(QThread):
    progress = Signal(int, str)

    def __init__(self, parent):
        super(ProcessThread, self).__init__(parent)

    def run(self):
        process = GuiStitchProcess()
        process.run_with_error_msgs(
            input_path=MainWindow.inputField.text(),
            output_path=MainWindow.outputField.text(),
            status_func=self.progress.emit,
        )


def initalize_gui():
    global MainWindow
    global settings
    global appVersion
    global appAuthor
    global processThread
    MainWindow = QUiLoader().load(os.path.join(SCRIPT_DIRECTORY, 'layout.ui'))
    settings = SettingsHandler()
    # Sets Window Title & Icon
    pixmap = QPixmap()
    pixmap.loadFromData(icon)
    appIcon = QIcon(pixmap)
    MainWindow.setWindowIcon(appIcon)
    # Sets Window Title
    appVersion = "3.0"
    appAuthor = "MechTechnology"
    MainWindow.setWindowTitle("SmartStitch By {0} [{1}]".format(appAuthor, appVersion))
    # Controls Setup
    on_load()
    bind_signals()
    # Sets up process thread
    processThread = ProcessThread(MainWindow)
    processThread.progress.connect(update_process_progress)
    # Show Window
    MainWindow.show()


def on_load():
    # App Fields
    MainWindow.statusField.setText("Idle")
    MainWindow.statusProgressBar.setValue(0)
    # Settings Fields
    MainWindow.outputTypeDropdown.setCurrentText(settings.load("output_type"))
    MainWindow.lossyField.setValue(settings.load("lossy_quality"))
    MainWindow.heightField.setValue(settings.load("split_height"))
    MainWindow.widthEnforcementDropdown.setCurrentIndex(settings.load("enforce_type"))
    MainWindow.customWidthField.setValue(settings.load("enforce_width"))
    MainWindow.detectorTypeDropdown.setCurrentIndex(settings.load("detector_type"))
    MainWindow.detectorSensitivityField.setValue(settings.load("senstivity"))
    MainWindow.scanStepField.setValue(settings.load("scan_step"))
    MainWindow.ignoreMarginField.setValue(settings.load("ignorable_pixels"))
    MainWindow.runProcessCheckbox.setChecked(settings.load("run_postprocess"))
    MainWindow.postProcessAppField.setText(settings.load("postprocess_app"))
    MainWindow.postProcessArgsField.setText(settings.load("postprocess_arguments"))
    output_type_changed(False)
    enforce_type_changed(False)
    detector_type_changed(False)


def bind_signals():
    MainWindow.inputField.textChanged.connect(input_field_changed)
    MainWindow.browseButton.clicked.connect(browse_location)
    MainWindow.outputTypeDropdown.currentTextChanged.connect(output_type_changed)
    MainWindow.lossyField.valueChanged.connect(lossy_quality_changed)
    MainWindow.heightField.valueChanged.connect(split_height_changed)
    MainWindow.widthEnforcementDropdown.currentTextChanged.connect(enforce_type_changed)
    MainWindow.customWidthField.valueChanged.connect(custom_width_changed)
    MainWindow.detectorTypeDropdown.currentTextChanged.connect(detector_type_changed)
    MainWindow.detectorSensitivityField.valueChanged.connect(
        detector_sensitivity_changed
    )
    MainWindow.scanStepField.valueChanged.connect(scan_step_changed)
    MainWindow.ignoreMarginField.valueChanged.connect(ignorable_margin_changed)
    MainWindow.runProcessCheckbox.stateChanged.connect(run_postprocess_changed)
    MainWindow.browsePostProcessAppButton.clicked.connect(browse_postprocess_app)
    MainWindow.postProcessAppField.textChanged.connect(postprocess_app_changed)
    MainWindow.postProcessArgsField.textChanged.connect(postprocess_args_changed)
    MainWindow.startProcessButton.clicked.connect(launch_process_async)


def input_field_changed():
    input_path = MainWindow.inputField.text() or ""
    if input_path:
        MainWindow.outputField.setText(input_path + OUTPUT_SUFFIX)
    else:
        MainWindow.outputField.setText("")


def browse_location():
    dialog = QFileDialog(
        MainWindow,
        'Select Input Directory Files',
        FileMode=QFileDialog.FileMode.Directory,
    )
    if dialog.exec_() == QDialog.Accepted:
        input_path = dialog.selectedFiles()[0] or ""
        MainWindow.inputField.setText(input_path)
        MainWindow.outputField.setText(input_path + OUTPUT_SUFFIX)


def output_type_changed(save=True):
    file_type = MainWindow.outputTypeDropdown.currentText()
    if save:
        settings.save("output_type", file_type)
    if file_type in ['.jpg', '.webp']:
        MainWindow.lossyWrapper.setHidden(False)
    else:
        MainWindow.lossyWrapper.setHidden(True)


def lossy_quality_changed():
    settings.save("lossy_quality", MainWindow.lossyField.value())


def split_height_changed():
    settings.save("split_height", MainWindow.heightField.value())


def enforce_type_changed(save=True):
    enforce_type = MainWindow.widthEnforcementDropdown.currentIndex()
    if save:
        settings.save("enforce_type", enforce_type)
    if enforce_type == 2:
        MainWindow.customWidthWrapper.setHidden(False)
    else:
        MainWindow.customWidthWrapper.setHidden(True)


def custom_width_changed():
    settings.save("enforce_width", MainWindow.customWidthField.value())


def detector_type_changed(save=True):
    detector_type = MainWindow.detectorTypeDropdown.currentIndex()
    if save:
        settings.save("detector_type", detector_type)
    if detector_type == 1:
        MainWindow.detectorSensitvityWrapper.setHidden(False)
        MainWindow.scanStepWrapper.setHidden(False)
        MainWindow.ignoreMarginWrapper.setHidden(False)
    else:
        MainWindow.detectorSensitvityWrapper.setHidden(True)
        MainWindow.scanStepWrapper.setHidden(True)
        MainWindow.ignoreMarginWrapper.setHidden(True)


def detector_sensitivity_changed():
    settings.save("senstivity", MainWindow.detectorSensitivityField.value())


def scan_step_changed():
    settings.save("scan_step", MainWindow.scanStepField.value())


def ignorable_margin_changed():
    settings.save("ignorable_pixels", MainWindow.ignoreMarginField.value())


def run_postprocess_changed():
    settings.save("run_postprocess", MainWindow.runProcessCheckbox.isChecked())


def browse_postprocess_app():
    dialog = QFileDialog(
        MainWindow,
        'Select Post Process Application Directory',
        FileMode=QFileDialog.FileMode.ExistingFile,
    )
    if dialog.exec_() == QDialog.Accepted:
        input_path = dialog.selectedFiles()[0] or ""
        MainWindow.postProcessAppField.setText(input_path)


def postprocess_app_changed():
    settings.save("postprocess_app", MainWindow.postProcessAppField.text())


def postprocess_args_changed():
    settings.save("postprocess_args", MainWindow.postProcessArgsField.text())


def update_process_progress(percentage: int, message: str):
    MainWindow.statusField.setText(message)
    MainWindow.statusProgressBar.setValue(percentage)


def launch_process_async():
    processThread.start()
