class AuditModel:
    def __init__(self, db):
        self.db = db

    def fetch_logs(self):
        raw_logs = self.db.get_audit_logs()
        formatted_logs = []
        for log in raw_logs:
            timestamp = log[0]
            time_str = timestamp.strftime('%Y-%m-%d %H:%M:%S') if hasattr(timestamp, 'strftime') else str(timestamp)
            formatted_logs.append({
                "time": time_str,
                "user": str(log[1]),
                "module": str(log[2]),
                "action": str(log[3]),
                "description": str(log[4])
            })
        return formatted_logs

    def get_module_color(self, module_name):
        module_colors = {
            "Security": "#e74c3c",
            "Election": "#f1c40f",
            "Voters": "#3498db",
            "Candidates": "#2ecc71",
            "System": "#9b59b6"
        }
        return module_colors.get(module_name, "white")