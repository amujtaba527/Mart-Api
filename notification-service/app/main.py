# main.py
from contextlib import asynccontextmanager
from typing import Annotated
from sqlmodel import Session, SQLModel
from fastapi import FastAPI, Depends, HTTPException
from aiokafka import  AIOKafkaConsumer
import asyncio
from app.db_engine import engine
from app.models.notification_models import Notification
from app.crud.notification_crud import  get_notification_by_id, get_all_notifications, add_new_notification
from app.deps import get_session
import smtplib
from aiokafka.errors import KafkaConnectionError, KafkaError
import logging
import notification_pb2

@asynccontextmanager
async def lifespan(app: FastAPI):
    loop = asyncio.get_event_loop()
    consumer_task = loop.create_task(consume())
    create_db_and_tables()
    yield
    consumer_task.cancel()
    await consumer_task

app = FastAPI(lifespan=lifespan)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)

async def send_mail(sender: str, receiver: str, subject: str, message: str):
    email_message = f"""\
    Subject: {subject}
    To: {receiver}
    From: {sender}

    {message}"""
    try:
        with smtplib.SMTP("sandbox.smtp.mailtrap.io", 587) as server:            
            server.starttls()
            server.login("e227d3eff1c055", "9c9bed77bbef51")
            server.sendmail(sender, receiver, email_message)
            logger.info("Email sent")
    except Exception as e:
        logger.error(f"Error sending email: {e}")


async def consume():
    consumer = AIOKafkaConsumer(
        'notification',  # topic name
        bootstrap_servers='broker:19092',  # kafka broker
        group_id='notification-group'
    )
    while True:
        try:
            await consumer.start()
            break
        except KafkaConnectionError as e:
            logger.error(f"Kafka connection error: {e}")
            await asyncio.sleep(5)
    try:
        async for msg in consumer:
            notification = notification_pb2.Notification()
            notification.ParseFromString(msg.value)
            logger.info(f"Received message: {notification}")
            await send_mail(notification.sender, notification.receiver, notification.subject, notification.message)
            # Extract information from notification and send email
            sender = "abc@gmail.com"
            receiver = "123@gmail.com"
            subject = "Notification Received"
            message = f"You have received a new notification: {notification}"
            
            # Send email asynchronously
            asyncio.create_task(send_mail(sender, receiver, subject, message))
            with next(get_session()) as session:
                print("SAVING DATA TO DATABSE")
                # Notification_data: notificaiton
                db_insert_product = add_new_notification(
                    notification_data=Notification(**notification), 
                    session=session)
                logger.info(f"DB Insert: {db_insert_product}")
    except KafkaError as e:
        logger.error(f"Error while consuming message: {e}")
    finally:
        await consumer.stop()

@app.get("/")
def read_root():
    return {"Hello": "Notification Service"}

@app.get("/notifications/", response_model=list[Notification])
def read_notifications(session: Annotated[Session, Depends(get_session)]):
    """Get all notifications from the database"""
    return get_all_notifications(session)

@app.get("/notifications/{notification_id}", response_model=Notification)
def read_single_notification(notification_id: int, session: Annotated[Session, Depends(get_session)]):
    """Read a single notification"""
    try:
        return get_notification_by_id(notification_id=notification_id, session=session)
    except HTTPException as e:
        raise e