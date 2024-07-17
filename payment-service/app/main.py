# main.py
from contextlib import asynccontextmanager
from typing import Annotated
from sqlmodel import Session, SQLModel
from fastapi import FastAPI, Depends, HTTPException
from typing import AsyncGenerator



from app.db_engine import engine
from app.models.payment_model import Payment
from app.crud.payment_crud import get_all_payments, get_payment_by_id, add_new_payment
import stripe


def get_session():
    with Session(engine) as session:
        yield session

def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)

# The first part of the function, before the yield, will
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("Creating tabl...")
    create_db_and_tables()
    print("\n\n LIFESPAN created!! \n\n")
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    return {"Payment": "Service"}



# Replace with your Stripe secret key
stripe.api_key = "sk_test_your_stripe_secret_key"

app = FastAPI()

@app.post("/process-payment/")
async def process_payment(amount: float, currency: str, token: str,payment: Payment, session: Annotated[Session, Depends(get_session)]):
    try:
        # Create a charge using the Stripe API
        charge = stripe.Charge.create(
            amount=amount,
            currency=currency,
            source=token,  # Stripe token obtained from the client-side (e.g., Stripe.js)
            description="Payment for FastAPI Store",  # Add a description for the payment
        )

        # You can handle the charge object as per your requirements
        # For example, log the payment or perform other actions

        # Return a success response
        payment_data = add_new_payment(payment=payment, session=session)
        return {"status": "success", "charge_id": charge.id,"payment data": payment_data}

    except stripe.error.CardError as e:
        # Handle specific Stripe errors
        return {"status": "error", "message": str(e)}
    except stripe.error.StripeError as e:
        # Handle generic Stripe errors
        return {"status": "error", "message": "Something went wrong. Please try again later."}

@app.get("/payments/", response_model=list[Payment])
def read_payments(session: Annotated[Session, Depends(get_session)]):
    """Get all payments"""
    return get_all_payments(session)


@app.get("/payments/{payment_id}", response_model=Payment)
def read_single_payment(payment_id: int, session: Annotated[Session, Depends(get_session)]):
    """Read a single payment by ID"""
    try:
        return get_payment_by_id(payment_id=payment_id, session=session)
    except HTTPException as e:
        raise e