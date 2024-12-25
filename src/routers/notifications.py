from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.models import Notification, User
from app.schemas import NotificationCreate, NotificationOut
from app.services.email_service import send_email
from app.services.sms_service import send_sms
from app.dependencies import get_current_user, get_current_admin_user, get_db

router = APIRouter(prefix="/notifications", tags=["Notifications"])

# Простые счётчики для лимитов (демонстрация)
SMS_LIMIT_PER_DAY = 10
EMAIL_LIMIT_PER_DAY = 10
sms_sent_today = 0
emails_sent_today = 0

@router.post("/", response_model=NotificationOut)
def create_notification(
    notification_data: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Проверим общий лимит в 50 уведомлений (условно)
    total_notifications_count = db.query(Notification).count()
    if total_notifications_count >= 50:
        raise HTTPException(status_code=400, detail="Reached the limit of 50 notifications in the service")

    # Создаем запись в БД (notification_type: 'service', 'sms', 'email')
    new_notification = Notification(
        title=notification_data.title,
        message=notification_data.message,
        notification_type=notification_data.notification_type,
        owner_id=current_user.id
    )
    db.add(new_notification)
    db.commit()
    db.refresh(new_notification)

    # Отправляем в завис-ти от типа
    if notification_data.notification_type == "email":
        global emails_sent_today
        if emails_sent_today >= EMAIL_LIMIT_PER_DAY:
            raise HTTPException(status_code=400, detail="Email limit reached for today")
        if current_user.email:
            send_email(
                to_email=current_user.email,
                subject=notification_data.title,
                body=notification_data.message
            )
            emails_sent_today += 1
        else:
            raise HTTPException(status_code=400, detail="User has no email")
    elif notification_data.notification_type == "sms":
        global sms_sent_today
        if sms_sent_today >= SMS_LIMIT_PER_DAY:
            raise HTTPException(status_code=400, detail="SMS limit reached for today")
        if current_user.phone_number:
            send_sms(
                to_phone=current_user.phone_number,
                text=notification_data.message
            )
            sms_sent_today += 1
        else:
            raise HTTPException(status_code=400, detail="User has no phone number")
    else:
        # Если notification_type = "service", ничего дополнительного не делаем,
        # так как это чисто внутреннее уведомление в системе.
        pass

    return new_notification

@router.get("/", response_model=List[NotificationOut])
def get_my_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notifications = db.query(Notification).filter(Notification.owner_id == current_user.id).all()
    return notifications

@router.post("/broadcast", response_model=dict)
def broadcast_notification(
    notification_data: NotificationCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    # Админ может всем разослать
    users = db.query(User).all()

    # Проверим общий лимит в 50 уведомлений
    total_notifications_count = db.query(Notification).count()
    if total_notifications_count + len(users) > 50:
        raise HTTPException(status_code=400, detail="Broadcast would exceed the limit of 50 notifications")

    # Создадим уведомление для каждого
    for user in users:
        new_notification = Notification(
            title=notification_data.title,
            message=notification_data.message,
            notification_type=notification_data.notification_type,
            owner_id=user.id
        )
        db.add(new_notification)

        # Отправка в зависимости от типа
        if notification_data.notification_type == "email":
            global emails_sent_today
            if emails_sent_today >= EMAIL_LIMIT_PER_DAY:
                continue  # или прерываем, или скипаем
            if user.email:
                send_email(
                    to_email=user.email,
                    subject=notification_data.title,
                    body=notification_data.message
                )
                emails_sent_today += 1

        elif notification_data.notification_type == "sms":
            global sms_sent_today
            if sms_sent_today >= SMS_LIMIT_PER_DAY:
                continue
            if user.phone_number:
                send_sms(
                    to_phone=user.phone_number,
                    text=notification_data.message
                )
                sms_sent_today += 1

    db.commit()
    return {"message": "Broadcast sent"}