from fastapi import HTTPException
from sqlmodel import Session, select
from app.models.order_model import Order, UpdateOrder

# Add a New Order to the Database
def add_new_order(order_data: Order, session: Session):
    print("Adding Order Item to Database")
    
    session.add(order_data)
    session.commit()
    session.refresh(order_data)
    return order_data

# Get All Orders from the Database
def get_all_orders(session: Session):
    all_orders = session.exec(select(Order)).all()
    return all_orders

# Get an Order by ID
def get_order_by_id(order_id: int, session: Session):
    order = session.exec(select(Order).where(Order.id == order_id)).one_or_none()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

# Update Order by ID
def update_order_by_id(order_id: int, to_update_order_data:UpdateOrder, session: Session):
    # Step 1: Get the Product by ID
    order = session.exec(select(Order).where(Order.id == order_id)).one_or_none()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    # Step 2: Update the Product
    hero_data = to_update_order_data.model_dump(exclude_unset=True)
    order.sqlmodel_update(hero_data)
    session.add(order)
    session.commit()
    return order