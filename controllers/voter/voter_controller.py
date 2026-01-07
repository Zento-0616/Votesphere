from PyQt6.QtWidgets import QApplication, QRadioButton, QFrame, QHBoxLayout, QVBoxLayout, QLabel
from PyQt6.QtGui import QPixmap, QPainter, QPainterPath
from PyQt6.QtCore import QTimer, QDateTime, Qt, QObject
from models.voter.voter_model import VoterModel
from view.voter.voter_view import VoterDashboardView, GlowPositionButton, CustomPopup, VoteReceiptDialog

class VoterController(QObject):
    def __init__(self, db, user_id, session_token):
        super().__init__()
        self.model = VoterModel(db)
        self.user_id = user_id
        self.session_token = session_token
        self.user_name = self.model.get_user_name(user_id)
        self.view = VoterDashboardView(self.user_name)
        self.selected_candidates = {}
        self.clean_exit = False
        self.is_submitting = False
        self.pos_group = []
        self.view.btn_submit.clicked.connect(self.handle_submit)
        self.view.btn_logout.clicked.connect(self.handle_logout)
        self.timer = QTimer(self); self.timer.timeout.connect(self.sync_state); self.timer.start(1000)
        self.init_data()

    def init_data(self):
        if self.model.check_voted(self.user_id): return
        if self.model.get_election_status() != 'active': return
        self.load_positions()
        self.update_trends()

    def load_positions(self):
        while self.view.layout_pos.count():
            item = self.view.layout_pos.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        self.pos_group = []
        positions = self.model.get_positions()
        for i, pos in enumerate(positions):
            btn = GlowPositionButton(pos)
            btn.clicked.connect(lambda _, p=pos: self.load_candidates(p))
            self.view.layout_pos.addWidget(btn)
            self.pos_group.append(btn)
            if i == 0: btn.click()
        self.view.layout_pos.addStretch()

    def load_candidates(self, position):
        self.view.lbl_current_pos.setText(position)
        for btn in self.pos_group: btn.setChecked(btn.text() == position)
        while self.view.layout_cand.count():
            item = self.view.layout_cand.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        candidates = self.model.get_candidates(position)
        for cid, name, grade, img in candidates:
            card = QFrame(); card.setObjectName("candCard")
            is_sel = (self.selected_candidates.get(position) == cid)
            self.view.apply_glow(card, is_sel)
            card.setStyleSheet(f"QFrame#candCard {{ background-color: {'rgba(52, 152, 219, 0.1)' if is_sel else 'rgba(255, 255, 255, 0.05)'}; border: 1px solid {'#3498db' if is_sel else '#334155'}; border-radius: 12px; }}")
            lay = QHBoxLayout(card); rb = QRadioButton(); rb.setFixedSize(0, 0); rb.setChecked(is_sel)
            rb.toggled.connect(lambda c, p=position, i=cid: self.record_selection(c, p, i))
            lay.addWidget(rb); card.mousePressEvent = lambda e, r=rb: r.setChecked(True)
            img_lbl = QLabel(); img_lbl.setFixedSize(60, 60)
            if img:
                px = QPixmap(); px.loadFromData(img); tgt = QPixmap(60, 60); tgt.fill(Qt.GlobalColor.transparent)
                ptr = QPainter(tgt); ptr.setRenderHint(QPainter.RenderHint.Antialiasing); path = QPainterPath(); path.addEllipse(0, 0, 60, 60); ptr.setClipPath(path)
                ptr.drawPixmap(0, 0, px.scaled(60, 60, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)); ptr.end(); img_lbl.setPixmap(tgt)
            else: img_lbl.setText("?"); img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter); img_lbl.setStyleSheet("font-size:24px; color:#94a3b8; background:rgba(255,255,255,0.05); border-radius:30px;")
            lay.addWidget(img_lbl); inf = QVBoxLayout(); n_lbl = QLabel(name); n_lbl.setStyleSheet("font-weight:bold; color:white; border:none;"); g_lbl = QLabel(grade); g_lbl.setStyleSheet("color:#94a3b8; border:none;"); inf.addWidget(n_lbl); inf.addWidget(g_lbl); lay.addLayout(inf); lay.addStretch()
            if is_sel: chk = QLabel("✓"); chk.setStyleSheet("color:#3498db; font-weight:bold; font-size:20px; border:none;"); lay.addWidget(chk)
            self.view.layout_cand.addWidget(card)

    def record_selection(self, checked, pos, cid):
        if checked:
            self.selected_candidates[pos] = cid
            self.view.lbl_summary.setText(f"{len(self.selected_candidates)} Position(s) Selected")
            self.view.btn_submit.setText(f"SUBMIT BALLOT ({len(self.selected_candidates)})")
            self.load_candidates(pos)

    def sync_state(self):
        if self.is_submitting: return
        if self.session_token != "ADMIN_SESSION":
            if not self.model.update_heartbeat(self.user_id, self.session_token):
                self.timer.stop(); self.logout(True); return
        self.update_trends()
        if self.model.get_election_status() != 'active': self.view.timer_frame.update_time("--:--:--")
        target = self.model.get_target_time()
        if target:
            sec = QDateTime.currentDateTime().secsTo(QDateTime.fromString(target, Qt.DateFormat.ISODate))
            if sec > 0:
                self.view.timer_frame.update_time(f"{sec//3600:02}:{(sec%3600)//60:02}:{sec%60:02}")
                self.view.timer_frame.set_urgent(sec <= 600)

    def update_trends(self):
        if self.view.isHidden() or self.is_submitting: return
        while self.view.leaders_layout.count():
            it = self.view.leaders_layout.takeAt(0)
            if it.widget(): it.widget().deleteLater()
        trends = self.model.get_trends()
        for pos, cands in trends.items():
            f = QFrame(); f.setStyleSheet("background:rgba(255,255,255,0.05); border-radius:8px;"); l = QVBoxLayout(f)
            t = QLabel(pos.upper()); t.setStyleSheet("color:#3498db; font-weight:bold; border:none;"); l.addWidget(t)
            if not cands: l.addWidget(QLabel("Awaiting data...", styleSheet="color:#64748b; font-style:italic; border:none;"))
            else:
                for i, (n, v) in enumerate(cands):
                    h = QHBoxLayout(); r = QLabel(str(i+1)); r.setFixedWidth(20); r.setStyleSheet("color:white; font-weight:bold; border:none;"); nl = QLabel(n); nl.setStyleSheet("color:#cbd5e1; border:none;"); vl = QLabel(str(v)); vl.setStyleSheet("color:#3498db; font-weight:bold; border:none;"); h.addWidget(r); h.addWidget(nl, 1); h.addWidget(vl); l.addLayout(h)
            self.view.leaders_layout.addWidget(f)

    def handle_submit(self):
        all_pos = self.model.get_positions()
        missing = [p for p in all_pos if p not in self.selected_candidates]
        if missing:
            CustomPopup.show_warning(self.view, "Incomplete", "Required positions:\n" + "\n".join([f"• {p}" for p in missing]))
            return
        if CustomPopup.ask_question(self.view, "Confirm", "Finalize your ballot?"):
            self.is_submitting = True; self.view.btn_submit.setEnabled(False); self.timer.stop(); self.view.submit_animation.start_animation()
            QTimer.singleShot(2500, self.execute_submission)

    def execute_submission(self):
        success, receipt = self.model.submit_ballot(self.user_id, self.user_name, self.selected_candidates)
        if success: self.view.submit_animation.stop_animation(); VoteReceiptDialog(receipt, self.view).exec(); self.logout(True)
        else: self.is_submitting = False; self.view.btn_submit.setEnabled(True); self.view.submit_animation.stop_animation(); self.timer.start(1000)

    def handle_logout(self):
        if CustomPopup.ask_question(self.view, "Logout", "End session?"): self.logout(True)

    def logout(self, force=False):
        self.timer.stop(); self.model.clear_session(self.user_id)
        from controllers.login_controller import LoginController
        self.login_ctrl = LoginController(self.model.db); self.view.close()