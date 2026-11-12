import re
from datetime import datetime, timedelta, timezone
import bcrypt
import jwt
from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, EmailStr, Field
import mysql.connector
from app import config

from app.services.database import get_database

# Reuse the existing JWT cookie verification.
from app.services.auth import get_current_user_id

# Group user endpoints and set the login lifetime to one hour.
user_router = APIRouter(prefix="/api/users")
TOKEN_SECONDS = 3600

# Validate the request body for signup and login.
class Credentials(BaseModel):
    email: EmailStr = Field(max_length=254)
    password: str = Field(min_length=1, max_length=72)


# Group user endpoints and set the login lifetime to one hour.
@user_router.post("/signup")
def sign_up(payload: Credentials, database=Depends(get_database)):
    # Enforce the email domain even when the frontend is bypassed.
    email = str(payload.email).lower()
    if email.rsplit("@", 1)[1] != "skidmore.edu":
        raise HTTPException(status_code=400, detail="Please use your @skidmore.edu email to sign up.")

    # Continue with the existing password checks.
    password = payload.password

    # Bcrypt limits passwords to 72 bytes, including multi-byte characters.
    if len(password.encode("utf-8")) > 72:
        raise HTTPException(status_code=400, detail="Password must be at most 72 bytes.")

    if (
        len(password) < 8
        or not re.search(r"[A-Z]", password)
        or not re.search(r"[0-9]", password)
        or not re.search(r"[^A-Za-z0-9\s]", password)
    ):
        raise HTTPException(
            status_code=400,
            detail="Password needs 8 characters, an uppercase letter, a number, and a symbol."
        )

    # Generate a salted hash and normalize email consistently.
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    email = str(payload.email).lower()
    cursor = database.cursor()

    # Bind values separately from SQL instead of building a SQL string.
    try:
        cursor.execute(
            "INSERT INTO users (email, password_hash) VALUES (%s, %s)",
            (email, password_hash)
        )
        database.commit()
    except mysql.connector.IntegrityError as error:
        database.rollback()
        if error.errno == 1062:
            raise HTTPException(status_code=409, detail="Email is already registered.")
        raise
    finally:
        cursor.close()

    return {"message": "Account created. Please log in."}


# Verify the password and issue a JWT cookie.
@user_router.post("/login")
def log_in(payload: Credentials, response: Response, database=Depends(get_database)):
    password = payload.password.encode("utf-8")
    if len(password) > 72:
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    # Look up the account without returning its password hash to the browser.
    cursor = database.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT id, email, password_hash FROM users WHERE email = %s",
            (str(payload.email).lower(),)
        )
        user = cursor.fetchone()
    finally:
        cursor.close()

    if user is None or not bcrypt.checkpw(password, user["password_hash"].encode("utf-8")):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    # Sign a token containing the user ID and its expiration time.
    now = datetime.now(timezone.utc)
    token = jwt.encode(
        {
            "sub": str(user["id"]),
            "iat": now,
            "exp": now + timedelta(seconds=TOKEN_SECONDS)
        },
        config.JWT_SECRET,
        algorithm="HS256"
    )

    # Let the browser store and send the token automatically.
    response.set_cookie(
        key="access_token",
        value=token,
        max_age=TOKEN_SECONDS,
        httponly=True,
        secure=config.COOKIE_SECURE,
        samesite="lax",
        path="/"
    )

    return {"message": "Logged in successfully.", "user": {"id": user["id"], "email": user["email"]}}


# Confirm that the browser still has a valid login cookie.
@user_router.get("/me")
def get_session(user_id: str = Depends(get_current_user_id)):
    return {"user_id": user_id}
