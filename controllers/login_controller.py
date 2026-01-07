from models.login_model import LoginModel
from view.common.login_view import LoginView, CustomPopup
from controllers.admin.admin_controller import AdminController
from controllers.voter.voter_controller import VoterController


class LoginController:
    def __init__(self, db):
        self.db = db
        self.model = LoginModel(db)
        self.view = LoginView()
        self.view.login_btn.clicked.connect(self.handle_login)
        self.admin_ctrl = None
        self.voter_ctrl = None

    def handle_login(self):
        self.view.login_btn.setEnabled(False)
        username, password = self.view.get_credentials()

        if not username or not password:
            CustomPopup.show_warning(self.view, "Required Fields", "ID and Password required.")
            self.view.login_btn.setEnabled(True)
            return

        user = self.model.authenticate(username, password)

        if user:
            user_id, uname, pword, role, voted, last_active = user
            if role == "voter" and self.model.check_session_conflict(last_active):
                CustomPopup.show_error(self.view, "Security Alert", "Active session detected.")
                self.view.login_btn.setEnabled(True)
                return

            token = self.model.create_session(user_id)
            status = self.model.get_election_status()

            if role == "admin":
                self.view.show_loading()
                self.admin_ctrl = AdminController(self.db, user_id)
                self.view.hide()
            elif role == "voter":
                if status != 'active':
                    CustomPopup.show_error(self.view, "Closed", "Election is closed.")
                elif voted:
                    CustomPopup.show_info(self.view, "Voted", "Already voted.")
                else:
                    self.voter_ctrl = VoterController(self.db, user_id, token)
                    self.view.hide()
        else:
            CustomPopup.show_error(self.view, "Auth Failure", "Invalid credentials.")

        self.view.login_btn.setEnabled(True)