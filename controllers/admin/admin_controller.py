from PyQt6.QtCore import QTimer, QDateTime, Qt
from PyQt6.QtWidgets import QMessageBox
from models.admin.admin_model import AdminModel
from controllers.admin.candidate_controller import CandidateController
from controllers.voter.voter_controller import VoterController
from controllers.admin.results_controller import ResultsController
from controllers.admin.audit_controller import AuditLogController
from controllers.admin.settings_controller import SettingsController


class AdminController:
    def __init__(self, db, user_id):
        self.db = db
        self.model = AdminModel(db)
        from view.admin.admin_view import AdminDashboard
        self.view = AdminDashboard()

        self.cand_ctrl = CandidateController(db)
        self.voter_ctrl = VoterController(db, user_id, "ADMIN_SESSION")
        self.results_ctrl = ResultsController(db)
        self.audit_ctrl = AuditLogController(db)
        self.settings_ctrl = SettingsController(db)

        self.view.stacked.addWidget(self.cand_ctrl.view)
        self.view.stacked.addWidget(self.voter_ctrl.view)
        self.view.stacked.addWidget(self.results_ctrl.view)
        self.view.stacked.addWidget(self.audit_ctrl.view)
        self.view.stacked.addWidget(self.settings_ctrl.view)

        for i, btn in enumerate(self.view.sidebar_buttons):
            btn.clicked.connect(lambda checked, idx=i: self.switch_page(idx))

        self.view.logout_btn.clicked.connect(self.handle_logout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh)
        self.timer.start(2000)

        self.switch_page(0)
        self.refresh()
        self.view.showMaximized()

    def switch_page(self, index):
        self.view.stacked.setCurrentIndex(index)
        for i, btn in enumerate(self.view.sidebar_buttons):
            btn.set_active(i == index)
        if index == 1:
            self.cand_ctrl.refresh_all()
        elif index == 3:
            self.results_ctrl.refresh_display()
        elif index == 4:
            self.audit_ctrl.update_logs()

    def refresh(self):
        try:
            if not self.view.isVisible(): return
            v, c = self.model.get_stats()
            self.view.voters_frame.value_lbl.setText(str(v))
            self.view.votes_frame.value_lbl.setText(str(c))
            self.view.graph.update_data(self.model.get_leader_data())
            conf = self.model.get_election_config()
            self.view.title_lbl.setText(conf['name'] or "Dashboard")
            self.view.status_frame.value_lbl.setText(conf['status'].upper())
            if conf['status'] == 'active' and conf['target_time']:
                target = QDateTime.fromString(conf['target_time'], Qt.DateFormat.ISODate)
                sec = QDateTime.currentDateTime().secsTo(target)
                if sec <= 0:
                    self.model.stop_election()
                else:
                    self.view.timer_frame.value_lbl.setText(f"{sec // 3600:02}:{(sec % 3600) // 60:02}:{sec % 60:02}")
            else:
                self.view.timer_frame.value_lbl.setText("--:--:--")
        except:
            pass

    def handle_logout(self):
        if QMessageBox.question(self.view, "Logout", "Confirm?") == QMessageBox.StandardButton.Yes:
            self.timer.stop()
            from controllers.login_controller import LoginController
            self.login_ctrl = LoginController(self.db)
            self.view.close()