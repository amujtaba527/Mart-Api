from sqlmodel import Session , select
from fastapi import HTTPException
from app.models.notification_models import Notification


# Add a New Notification to the Database
def add_new_notification(notification_data: Notification, session: Session):
    session.add(notification_data)
    session.commit()
    session.refresh(notification_data)
    return notification_data

# Get All Notifications from the Database
def get_all_notifications(session: Session):
    all_notifications = session.exec(select(Notification)).all()
    return all_notifications

# Get Notification by ID
def get_notification_by_id(notification_id: int, session: Session):
    notification = session.exec(select(Notification).where(Notification.id == notification_id)).one_or_none()
    if notification is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification     