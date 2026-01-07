from PyQt6.QtWidgets import QMessageBox, QWidget, QHBoxLayout, QPushButton, QDialog
from models.admin.candidate_model import CandidateModel
from view.admin.candidate_view import ManageCandidatesView, AddCandidateDialog


class CandidateController:
    def __init__(self, db):
        self.model = CandidateModel(db)
        self.view = ManageCandidatesView()

        self.view.add_btn.clicked.connect(self.add_candidate)
        self.view.search_input.textChanged.connect(self.refresh_table)
        self.view.pos_filter.currentTextChanged.connect(self.refresh_table)

        self.refresh_all()

    def refresh_all(self):
        self.update_filters()
        self.refresh_table()

    def update_filters(self):
        current = self.view.pos_filter.currentText()
        self.view.pos_filter.blockSignals(True)
        self.view.pos_filter.clear()
        self.view.pos_filter.addItem("All Positions")
        for p in self.model.fetch_positions():
            self.view.pos_filter.addItem(p)
        self.view.pos_filter.setCurrentText(current if current in [self.view.pos_filter.itemText(i) for i in range(
            self.view.pos_filter.count())] else "All Positions")
        self.view.pos_filter.blockSignals(False)

    def refresh_table(self):
        search = self.view.search_input.text()
        pos = self.view.pos_filter.currentText()
        candidates = self.model.fetch_candidates(search, pos)

        self.view.table.setRowCount(0)
        from PyQt6.QtWidgets import QTableWidgetItem
        for row, (cid, name, position, grade) in enumerate(candidates):
            self.view.table.insertRow(row)
            self.view.table.setItem(row, 0, QTableWidgetItem(str(name)))
            self.view.table.setItem(row, 1, QTableWidgetItem(str(position)))
            self.view.table.setItem(row, 2, QTableWidgetItem(str(grade)))
            self.view.table.setCellWidget(row, 3, self.create_actions(cid))

    def create_actions(self, cid):
        w = QWidget()
        l = QHBoxLayout(w)
        l.setContentsMargins(5, 2, 5, 2)
        e = QPushButton("Edit")
        e.setStyleSheet("background: #3498db; color: white; border-radius: 4px;")
        e.clicked.connect(lambda: self.edit_candidate(cid))
        d = QPushButton("Delete")
        d.setStyleSheet("background: #e74c3c; color: white; border-radius: 4px;")
        d.clicked.connect(lambda: self.delete_candidate(cid))
        l.addWidget(e)
        l.addWidget(d)
        return w

    def add_candidate(self):
        if self.model.get_election_status() == 'active':
            QMessageBox.warning(self.view, "Error", "Election is LIVE")
            return
        d = AddCandidateDialog(self.view)
        if d.exec() == QDialog.DialogCode.Accepted:
            n, p, g, img = d.get_values()
            if n and p and g:
                if self.model.is_duplicate(n):
                    QMessageBox.warning(self.view, "Error", "Name Exists")
                    return
                self.model.add_candidate(n, p, g, img)
                self.model.log_action("Add", f"Added {n}")
                self.refresh_all()

    def edit_candidate(self, cid):
        if self.model.get_election_status() == 'active':
            QMessageBox.warning(self.view, "Error", "Election is LIVE")
            return
        data = self.model.get_candidate_details(cid)
        d = AddCandidateDialog(self.view, data)
        if d.exec() == QDialog.DialogCode.Accepted:
            n, p, g, img = d.get_values()
            if n and p and g:
                if self.model.is_duplicate(n, cid):
                    QMessageBox.warning(self.view, "Error", "Name Exists")
                    return
                self.model.update_candidate(cid, n, p, g, img)
                self.model.log_action("Edit", f"Edited {n}")
                self.refresh_all()

    def delete_candidate(self, cid):
        if self.model.get_election_status() == 'active':
            QMessageBox.warning(self.view, "Error", "Election is LIVE")
            return
        if QMessageBox.question(self.view, "Confirm", "Archive candidate?") == QMessageBox.StandardButton.Yes:
            self.model.delete_candidate(cid)
            self.model.log_action("Delete", f"Archived ID {cid}")
            self.refresh_all()