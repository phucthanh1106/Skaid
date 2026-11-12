import jwt
from fastapi import Cookie, HTTPException
from app import config


# Verify the login cookie and return its user ID.
def get_current_user_id(access_token: str | None = Cookie(default=None)):
    if not access_token:
        raise HTTPException(status_code=401, detail="Please log in.")

    # Verify the signature and require an expiration and user ID.
    try:
        payload = jwt.decode(
            access_token,
            config.JWT_SECRET,
            algorithms=["HS256"],
            options={"require": ["exp", "sub"]}
        )
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Your session is invalid or expired. Please log in again.")

    # Accept only the positive numeric user IDs issued by login.
    user_id = payload["sub"]
    if not isinstance(user_id, str) or not user_id.isdecimal() or int(user_id) < 1:
        raise HTTPException(status_code=401, detail="Invalid session.")

    return user_id
