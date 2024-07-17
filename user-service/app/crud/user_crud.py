from fastapi import HTTPException
from sqlmodel import Session, select
from bcrypt import hashpw, gensalt
from app.models.user_model import User,UserCreate

# Add a New User to the Database
def create_user(user: UserCreate, session: Session ):
    try:
        # Print statement for debugging purposes
        print(f"Creating user {user}")

        # Hash the user's password
        hashed_password = hashpw(user.password.encode("utf-8"), gensalt())

        # Create a new User object
        new_user = User(
            name=user.name,
            email=user.email,
            password=hashed_password.decode("utf-8"),
            role=user.role
        )

        # Add the new user to the session
        session.add(new_user)

        # Commit the transaction to save the user in the database
        session.commit()

        # Refresh the instance to reflect the database state
        session.refresh(new_user)

        # Return the newly created user
        return {
            "user": new_user
        }
    except Exception as e:
        # Roll back the transaction in case of an error
        session.rollback()
        print(f"An error occurred: {e}")
        raise e

# Get User by Email
def get_user_by_email(user_email: str, session: Session ):
    try:
        user = session.exec(select(User).where(User.email == user_email)).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred")