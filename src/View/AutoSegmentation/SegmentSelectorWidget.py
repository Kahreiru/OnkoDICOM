import sys
import pandas
from PySide6 import QtWidgets
from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem, QSizePolicy
from PySide6.QtCore import Qt

from src.Controller.PathHandler import resource_path

class SegmentSelectorWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(SegmentSelectorWidget, self).__init__(parent)

        # To store the selected segments
        self._selected_list: list[str] = []

        # Setting Up the Window
        layout: QtWidgets.QLayout = QtWidgets.QFormLayout()

        # Creating Tree using PySide6
        tree: QTreeWidget = QtWidgets.QTreeWidget(self)
        tree.setObjectName("Segmentation_Selection_Tree")
        tree.setHeaderLabels(["Body Section", "Organ Structure"])
        tree.resize(tree.sizeHint().width(), tree.sizeHint().height())
        tree.setSizePolicy(QSizePolicy(
            QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding))
        tree.setColumnCount(2)

        # Adding Data To Tree using Pandas
        structure_data: pandas.DataFrame = pandas.read_csv(resource_path("res/segmentation_lists.csv"))
        structure_data["BodySection"]: pandas.Series = structure_data["BodySection"].str.strip()
        structure_data["Structure"]: pandas.Series = structure_data["Structure"].str.strip()
        for BodySection in structure_data ["BodySection"].unique():
            body_input: QTreeWidgetItem = QTreeWidgetItem(tree)
            body_input.setFlags(body_input.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            body_input.setCheckState(0, Qt.CheckState.Unchecked)
            body_input.setText(0, "   " + BodySection) # Spaces added here to prevent check box from going over the first letter

            # Getting the Structure list from the Pandas Table
            structure_list: pandas.DataFrame = structure_data.loc[structure_data["BodySection"] == BodySection]
            for StructureName in structure_list.Structure.unique():
                structure_input: QTreeWidgetItem = QTreeWidgetItem(body_input)
                structure_input.setFlags(structure_input.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                structure_input.setCheckState(1, Qt.CheckState.Unchecked)
                structure_input.setText(1, "   " + StructureName) # Spaces added here to prevent check box from going over the first letter
            tree.addTopLevelItem(body_input)

        # Adding the layout and the Widget to the parent Widget
        layout.addWidget(tree)
        tree.resizeColumnToContents(0)
        tree.resizeColumnToContents(1)
        tree.itemClicked.connect(self._body_section_clicked)
        self.setLayout(layout)

    def get_segment_list(self):
        return self.selected_list

    def _body_section_clicked(self, item: QTreeWidgetItem, column: int):
        body_text: str = item.text(column).strip()

        # Adds full body section when the body section is checked
        if item.checkState(0) == Qt.CheckState.Checked:
            for i in range(0, item.childCount()):
                item.child(i).setCheckState(1, Qt.CheckState.Checked)
                item_text: str = item.child(i).text(1).strip()
                if item_text not in self._selected_list:
                    self._selected_list.append(item_text)

        # Removes full body section when the body section unchecked
        if item.checkState(0) == Qt.CheckState.Unchecked:
            if body_text in self._selected_list:
                for i in range(0, item.childCount()):
                    item.child(i).setCheckState(1, Qt.CheckState.Unchecked)
                    self._selected_list.remove(item.child(i).text(1).strip())

        # Adds the specific Structure to the list when checked
        if item.checkState(1) == Qt.CheckState.Checked:
            if body_text not in self._selected_list:
                self._selected_list.append(body_text)

                # To change the parent check box when one is unchecked
                item.parent().setCheckState(0, Qt.CheckState.PartiallyChecked)

                # To uncheck the parent check box when all children are unchecked
                active_count: int = 0
                parent_count: int = item.parent().childCount()
                for i in range(0, parent_count):
                    if item.parent().child(i).checkState(1) == Qt.CheckState.Checked:
                        active_count += 1
                if active_count == parent_count:
                    item.parent().setCheckState(0, Qt.CheckState.Checked)


        # Removes the specific structure from the list when unchecked
        if item.checkState(1) == Qt.CheckState.Unchecked:
            if body_text in self._selected_list:
                self._selected_list.remove(body_text)

                # To change the parent check box when one is unchecked
                item.parent().setCheckState(0, Qt.CheckState.PartiallyChecked)

                # To uncheck the parent check box when all children are unchecked
                active_count: int = 0
                for i in range(0, item.parent().childCount()):
                    if item.parent().child(i).checkState(1) == Qt.CheckState.Checked:
                        active_count += 1
                if active_count == 0:
                    item.parent().setCheckState(0, Qt.CheckState.Unchecked)

if __name__ == "__main__":
    app: QtWidgets.QApplication = QtWidgets.QApplication(sys.argv)
    widget: QtWidgets.QWidget = SegmentSelectorWidget()
    widget.show()
    sys.exit(app.exec())





