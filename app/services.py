from .extensions import db
from .models import AuditLog

def grade_from_total(total):
    if total >= 80:
        return "A"
    if total >= 70:
        return "B"
    if total >= 60:
        return "C"
    if total >= 50:
        return "D"
    return "F"

def remark_from_grade(grade):
    return {
        "A": "Excellent",
        "B": "Very Good",
        "C": "Good",
        "D": "Pass",
        "F": "Needs Improvement",
    }.get(grade, "")

def log_action(user_id, action, entity_type=None, entity_id=None, description=None, ip_address=None):
    audit = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        description=description,
        ip_address=ip_address,
    )
    db.session.add(audit)
    db.session.commit()
