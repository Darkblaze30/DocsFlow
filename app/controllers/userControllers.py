from fastapi import Request, HTTPException, status
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
import os

from app.utils.db_operations import fetch_one, fetch_all, execute
import app.models.userModels as userModels

SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey_change_me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

revoked_tokens = set()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def revoke_token(token: str):
    revoked_tokens.add(token)

def is_token_revoked(token: str) -> bool:
    return token in revoked_tokens

def get_user_by_email(email: str):
    sql = f"SELECT * FROM `{userModels.TABLE_USERS}` WHERE `{userModels.USER_COL_EMAIL}` = %s LIMIT 1"
    return fetch_one(sql, (email,))

def register_user(name: str, email: str, password: str, rol: str = 'user', department_name: str | None = None):
    existing = get_user_by_email(email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    rol_enum = userModels.RoleEnum.user.value
    if rol:
        try:
            rol_enum = userModels.RoleEnum(rol).value
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid role")

    dept_id = None
    if department_name:
        dep_name_clean = department_name.strip()
        if dep_name_clean:
            sql_find = f"SELECT `{userModels.DEPT_COL_ID}`, `{userModels.DEPT_COL_NAME}` FROM `{userModels.TABLE_DEPARTMENTS}` WHERE LOWER(`{userModels.DEPT_COL_NAME}`) = LOWER(%s) LIMIT 1"
            dept = fetch_one(sql_find, (dep_name_clean,))
            if not dept:
                sql_insert_dept = f"INSERT INTO `{userModels.TABLE_DEPARTMENTS}` (`{userModels.DEPT_COL_NAME}`) VALUES (%s)"
                new_dept_id = execute(sql_insert_dept, (dep_name_clean,))
                dept_id = new_dept_id
            else:
                dept_id = dept.get(userModels.DEPT_COL_ID)

    hashed = get_password_hash(password)
    sql_insert_user = f"""
        INSERT INTO `{userModels.TABLE_USERS}`
        (`{userModels.USER_COL_NAME}`, `{userModels.USER_COL_EMAIL}`, `{userModels.USER_COL_PASSWORD}`, `{userModels.USER_COL_ROL}`, `{userModels.USER_COL_DEPARTMENT_ID}`)
        VALUES (%s, %s, %s, %s, %s)
    """
    user_id = execute(sql_insert_user, (name, email, hashed, rol_enum, dept_id))
    user = fetch_one(f"SELECT * FROM `{userModels.TABLE_USERS}` WHERE `{userModels.USER_COL_ID}` = %s LIMIT 1", (user_id,))
    return user

def authenticate_user(email: str, password: str):
    user = get_user_by_email(email)
    if not user:
        return False
    if not verify_password(password, user.get(userModels.USER_COL_PASSWORD)):
        return False
    return user

def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    if is_token_revoked(token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has been revoked")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

    user = fetch_one(f"SELECT * FROM `{userModels.TABLE_USERS}` WHERE `{userModels.USER_COL_ID}` = %s LIMIT 1", (int(user_id),))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

def get_current_admin_user(request: Request):
    current_user = get_current_user(request)
    user_role = current_user.get(userModels.USER_COL_ROL)
    if user_role != userModels.RoleEnum.admin.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Access denied. Admin role required."
        )
    return current_user