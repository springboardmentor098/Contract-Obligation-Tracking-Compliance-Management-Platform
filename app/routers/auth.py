from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.all_models import User
from app.core.security import pwd_context, create_access_token

router = APIRouter(tags=["Authentication"])

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # 1. Find user in database
    user = db.query(User).filter(User.email == form_data.username).first()
    
    # 2. Check if user exists AND password matches
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # 3. Create the JWT Token containing the user's role AND id
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role, "id": user.id} # 👈 Added "id" here!
    )
    
    # 4. Return the token to Swagger UI
    return {"access_token": access_token, "token_type": "bearer"}