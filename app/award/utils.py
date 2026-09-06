
from ..extensions import db
from ..models import Award


def get_awards(user=None):
    
    filters = []
    if user:
        filters.append(Award.user_id == user.id)
    
    awards = (
        db.session.query(Award)
        .filter(*filters)
        .all()
    )
    
    return awards
    

def get_award(award_id):
    if not award_id:
        return None
    return db.session.query(Award).filter_by(id=award_id).first()