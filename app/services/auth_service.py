import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy import and_

import config
from model.user.users import User
from model.user.jwt_tokens import JWTToken
from core.common.exceptions import HRSystemBaseException
from starlette import status


class AuthService:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return self.pwd_context.hash(password)

    def authenticate_user(
        self, db: Session, email: str, password: str
    ) -> Optional[User]:
        """Authenticate a user by email and password"""
        user = (
            db.query(User)
            .filter(
                and_(
                    User.email == email,
                    User.is_active == True,
                    User.deleted_at.is_(None),
                )
            )
            .first()
        )

        if not user or not self.verify_password(password, user.password):
            return None
        return user

    def create_access_token(
        self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None
    ) -> Tuple[str, str, int]:
        """Create an access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=config.ACCESS_TOKEN_EXPIRED)

        to_encode.update({"exp": expire, "type": "access"})
        jti = str(uuid.uuid4())
        to_encode.update({"jti": jti})

        encoded_jwt = jwt.encode(
            to_encode, config.JWT_ACCESS_SECRET_KEY, algorithm=config.ALGORITHM
        )
        return encoded_jwt, jti, int(expire.timestamp())

    def create_refresh_token(
        self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None
    ) -> Tuple[str, str, int]:
        """Create a refresh token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=config.REFRESH_TOKEN_EXPIRED)

        to_encode.update({"exp": expire, "type": "refresh"})
        jti = str(uuid.uuid4())
        to_encode.update({"jti": jti})

        encoded_jwt = jwt.encode(
            to_encode, config.JWT_REFRESH_SECRET_KEY, algorithm=config.ALGORITHM
        )
        return encoded_jwt, jti, int(expire.timestamp())

    def store_token(
        self,
        db: Session,
        user_id: int,
        token: str,
        token_type: str,
        jti: str,
        expires_at: int,
    ):
        """Store token in database"""
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        jwt_token = JWTToken(
            user_id=user_id,
            token_type=token_type,
            token_hash=token_hash,
            jti=jti,
            expires_at=expires_at,
            is_blacklisted=False,
        )
        db.add(jwt_token)
        db.commit()
        return jwt_token

    def verify_token(
        self, db: Session, token: str, token_type: str
    ) -> Optional[Dict[str, Any]]:
        """Verify and decode a token"""
        try:
            # Choose the correct secret key based on token type
            secret_key = (
                config.JWT_ACCESS_SECRET_KEY
                if token_type == "access"
                else config.JWT_REFRESH_SECRET_KEY
            )

            # Decode the token
            payload = jwt.decode(token, secret_key, algorithms=[config.ALGORITHM])

            # Check if token type matches
            if payload.get("type") != token_type:
                return None

            # Check if token is blacklisted
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            jwt_token = (
                db.query(JWTToken)
                .filter(
                    and_(
                        JWTToken.token_hash == token_hash,
                        JWTToken.jti == payload.get("jti"),
                        JWTToken.is_blacklisted == False,
                    )
                )
                .first()
            )

            if not jwt_token:
                return None

            return payload

        except jwt.ExpiredSignatureError:
            return None
        except InvalidTokenError:
            return None
        except Exception:
            # Catch any other JWT-related errors
            return None

    def blacklist_token(self, db: Session, jti: str):
        """Blacklist a token by its JTI"""
        jwt_token = db.query(JWTToken).filter(JWTToken.jti == jti).first()
        if jwt_token:
            jwt_token.is_blacklisted = True
            db.commit()

    def blacklist_user_tokens(self, db: Session, user_id: int):
        """Blacklist all tokens for a user"""
        db.query(JWTToken).filter(
            and_(JWTToken.user_id == user_id, JWTToken.is_blacklisted == False)
        ).update({"is_blacklisted": True})
        db.commit()

    def login(self, db: Session, email: str, password: str) -> Dict[str, Any]:
        """Login user and return tokens"""
        user = self.authenticate_user(db, email, password)
        if not user:
            raise HRSystemBaseException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                message="Invalid email or password",
            )

        # Create tokens
        access_token, access_jti, access_expires = self.create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )
        refresh_token, refresh_jti, refresh_expires = self.create_refresh_token(
            data={"sub": str(user.id), "email": user.email}
        )

        # Store tokens in database
        self.store_token(
            db, user.id, access_token, "access", access_jti, access_expires
        )
        self.store_token(
            db, user.id, refresh_token, "refresh", refresh_jti, refresh_expires
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role_id": user.role_id,
            },
        }

    def refresh_access_token(self, db: Session, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token using refresh token"""
        payload = self.verify_token(db, refresh_token, "refresh")
        if not payload:
            raise HRSystemBaseException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                message="Invalid refresh token",
            )

        user_id = int(payload.get("sub"))
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise HRSystemBaseException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                message="User not found or inactive",
            )

        # Create new access token
        access_token, access_jti, access_expires = self.create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )

        # Store new access token
        self.store_token(
            db, user.id, access_token, "access", access_jti, access_expires
        )

        return {"access_token": access_token, "token_type": "bearer"}

    def logout(self, db: Session, access_token: str):
        """Logout user by blacklisting their tokens"""
        payload = self.verify_token(db, access_token, "access")
        if payload:
            user_id = int(payload.get("sub"))
            self.blacklist_user_tokens(db, user_id)


# Create singleton instance
auth_service = AuthService()
