from contextlib import asynccontextmanager
from typing import Annotated
from sqlmodel import Session, SQLModel
from fastapi import FastAPI, Depends, HTTPException
from typing import AsyncGenerator
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import asyncio
import json

from app.db_engine import engine
from app.models.order_model import Order, UpdateOrder
from app.crud.order_crud import get_all_orders, get_order_by_id, update_order_by_id
from app.deps import get_session, get_kafka_producer
from app.consumers.order_consumer import consume_messages


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


# The first part of the function, before the yield, will
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("Creating tabl...")

    task = asyncio.create_task(consume_messages(
        "order-response", 'broker:19092'))
    create_db_and_tables()
    print("\n\n LIFESPAN created!! \n\n")
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    return {"Hello": "Order Service"}


@app.post("/manage-order/", response_model=Order)
async def create_new_order(order: Order, session: Annotated[Session, Depends(get_session)], producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]):
    """ Create a new order and send it to Kafka"""

    order_dict = {field: getattr(order, field) for field in order.dict()}
    order_json = json.dumps(order_dict).encode("utf-8")
    print("order_JSON:", order_json)
    # Produce message
    await producer.send_and_wait("Order", order_json)
    # new_order = add_new_order(order, session)
    return order

@app.get("/manage-order/all", response_model=list[Order])
def all_orders(session: Annotated[Session, Depends(get_session)]):
    """ Get all order from the database"""
    return get_all_orders(session)

@app.get("/manage-order/{order_id}", response_model=Order)
def single_order(order_id: int, session: Annotated[Session, Depends(get_session)]):
    """ Get a single order by ID"""
    try:
        return get_order_by_id(order_id=order_id, session=session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/manage-order/{order_id}", response_model=Order)
def update_single_order(order_id: int, order: UpdateOrder, session: Annotated[Session, Depends(get_session)]):
    """ Update a single order by ID"""
    try:
        return update_order_by_id(order_id=order_id, to_update_order_data=order, session=session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
