import sys
from typing import Callable
from PySide6 import QtWidgets
from PySide6.QtGui import QTextCursor, QPixmap, QIcon

from SegmentSelectorWidget import SegmentSelectorWidget
import src.View.StyleSheetReader as StyleSheetReader
from src.Controller.AutoSegmentationController import AutoSegmentationController
from src.Controller.PathHandler import resource_path


class AutoSegmentWindow(QtWidgets.QWidget):

    _controller: AutoSegmentationController | None = None

    def __init__(self):
        super(AutoSegmentWindow, self).__init__()

        # Adding Window Title
        self.setWindowTitle("OnkoDICOM: Auto-Segmentation")

        # Adding Window Icon
        window_icon = QIcon()
        window_icon.addPixmap(QPixmap(resource_path(
            "res/images/icon.ico")), QIcon.Mode.Normal, QIcon.State.Off)
        self.setWindowIcon(window_icon)

        self._fast_compatible_tasks = {"total",
                                       "body",
                                       }

        # Setting Up Window
        self.setStyleSheet(StyleSheetReader.get_stylesheet())

        # Adding Widgets
        self._tree_selector = SegmentSelectorWidget(self)

        # Setting up Layout
        window_layout = QtWidgets.QHBoxLayout()

        # Left Section of the Window
        self._left_layout = QtWidgets.QFormLayout()
        self._make_segmentation_task_selection()  # Adding Segmentation Task Combo Box
        self._make_fast_checkbox()
        self._make_progress_text()
        self._make_start_button(self._start_button_clicked)
        window_layout.addLayout(self._left_layout)

        # Right Section of the Window
        window_layout.addWidget(self._tree_selector)

        # Setting the Window Layout
        self.setLayout(window_layout)

        # Creating Controller Class
        if AutoSegmentWindow._controller is None:
            AutoSegmentWindow._controller = AutoSegmentationController(self)
        else:
            AutoSegmentWindow._controller.set_view(self)

        # Check task setting against fast mode - set check box false if not compatible
        self._task_combo.currentIndexChanged.connect(self._check_task_is_fast_compatible)

    def _make_segmentation_task_selection(self) -> None:
        """
        Protected method to create the segmentation task label and
        combo box for segmentation task selection.
        :rtype: None
        """
        _task_label: QtWidgets.QLabel = QtWidgets.QLabel("Segmentation Task:")
        self._left_layout.addWidget(_task_label)

        self._task_combo: QtWidgets.QComboBox = QtWidgets.QComboBox()
        # List of items which can be selected and segmented for
        self._task_combo.addItems([
            "total", "total_mr", "lung_vessels", "body", "body_mr",
            "vertebrae_mr", "hip_implant", "pleural_pericard_effusion", "cerebral_bleed",
            "head_glands_cavities", "head_muscles", "headneck_bones_vessels",
            "headneck_muscles", "liver_vessels", "oculomotor_muscles",
            "lung_nodules", "kidney_cysts", "breasts", "liver_segments",
            "liver_segments_mr", "craniofacial_structures", "abdominal_muscles"
        ])  # Need to figure out if we can make this an Enum
        self._task_combo.setCurrentIndex(0)
        self._task_combo.setToolTip("Select for Segmentation Task to be completed.\n"
                                    "This will be the specific area of the body to create a segment for")
        self._left_layout.addWidget(self._task_combo)

    def _make_fast_checkbox(self) -> None:
        """
        Protected method to create the checkbox with label to
        determine if the fast option is selected.
        :rtype: None
        """
        self._fast_checkbox: QtWidgets.QCheckBox = QtWidgets.QCheckBox("Fast")
        self._fast_checkbox.setToolTip("When Activated this will allow for faster processing times with the \n"
                                       "downside of lower resolution of the resulting segmentations.\n"
                                       "This option is only available on particular tasks such as total. \n"
                                       "BENEFIT: Faster Segmentations\n"
                                       "DOWNSIDE: Not as Accurate Segmentations")
        self._left_layout.addWidget(self._fast_checkbox)

    def _make_progress_text(self) -> None:
        """
        Protected method to create the progress text label and progress text box.
        To give the user feedback on what the current activity which is occurring.
        :rtype: None
        """
        _progress_text_label: QtWidgets.QLabel = QtWidgets.QLabel("\n\nCurrent Task:")
        self._left_layout.addWidget(_progress_text_label)

        self._progress_text = QtWidgets.QTextEdit()
        self._progress_text.setText("Waiting...")
        self._progress_text.setReadOnly(True)
        self._progress_text.setToolTip("What task the auto-segmentator is currently performing")
        self._left_layout.addWidget(self._progress_text)

    def _make_start_button(self, button_action: Callable[[], None]) -> None:
        """
        Protected Method to create the start button
        To start the auto-segmentation task which has been selected.
        :param button_action: function
        :rtype: None
        """
        self._start_button: QtWidgets.QPushButton = QtWidgets.QPushButton("Start")
        self._start_button.setObjectName("start_button")
        # Button Action
        self._start_button.clicked.connect(button_action)
        self._left_layout.addWidget(self._start_button)

    def _start_button_clicked(self) -> None:
        """
        Protected method to be called when the start button is clicked.
        :rtype: None
        """
        self._controller.start_button_clicked()

    def set_progress_text(self, text: str) -> None:
        """
        Public Method to set the progress text in the progress text box.
        To display the text to the user of what is currently being performed,
        to inform the user as to the current aspect of the task being performed.
        :param text: str
        :rtype: None
        """
        self._progress_text.append(text)
        cursor = self._progress_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self._progress_text.setTextCursor(cursor)
        self._progress_text.ensureCursorVisible()

    def enable_start_button(self):
        """Enables the start button and sets its text to "Start".

        This method is used to reactivate the start button after it has been
        disabled, typically after a segmentation task has completed or failed.
        """
        self._start_button.setEnabled(True)
        self._start_button.setText("Start")

    def disable_start_button(self):
        """Disables the start button and sets its text to "Wait".

        This method is used to deactivate the start button,
        typically during the segmentation process.
        """
        self._start_button.setEnabled(False)
        self._start_button.setText("Wait")

    def _check_task_is_fast_compatible(self):
        """
        Protected method to check if the currently selected task
        is compatible with the fast option. If the task is not
        compatible then the fast checkbox is disabled and unchecked.
        :rtype: None
        """
        if self._task_combo.currentText() not in self._fast_compatible_tasks:
            self._fast_checkbox.setChecked(False)
            self._fast_checkbox.setEnabled(False)
        else:
            self._fast_checkbox.setEnabled(True)

    def get_segmentation_task(self) -> str:
        """
        Public Method to retrieve the current selection
        from the segmentation task combo box.
        :rtype: str
        """
        return self._task_combo.currentText()

    def get_fast_value(self) -> bool:
        """
        Public Method to retrieve the value of the fast checkbox.
        TO see if the fast option has been selected.
        :rtype: bool
        """
        return self._fast_checkbox.isChecked()

    def get_autoseg_controller(self):
        return self._controller


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = AutoSegmentWindow()
    window.show()
    sys.exit(app.exec())