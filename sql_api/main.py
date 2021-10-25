from typing import List
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import delete
from . import crud, models, schemas
from .database import SessionLocal, engine


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def paswrd_verify(db: Session, user_name: str, paswrd: str):
    db_user = crud.read_user_by_name(db, username=user_name)
    fake_hashed_password = paswrd + "notreallyhashed"
    if fake_hashed_password == db_user.hashed_password:
        return True

#Create
@app.post("/new_user/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user_name = crud.read_user_by_name(db, username=user.username)
    if db_user_name:
        raise HTTPException(status_code=400, detail="Name already registered by another user")
    
    return crud.create_user(db=db, user=user)

@app.post("/new_item/", response_model=schemas.Item)
def create_item(user_name: str, item: schemas.ItemCreate, db: Session = Depends(get_db)):
    db_user = crud.read_user_by_name(db, username=user_name)

    db_item = crud.read_item_by_name(db, item.item_name, user_id=db_user.id)
    if db_item:
        raise HTTPException(status_code=400, detail="User already has this item")
    
    return crud.create_user_item(db, item=item, user_id=db_user.id)

#read
@app.get("/users/", response_model=list[schemas.User])
def get_users(skip: int=0, limit: int=0, db: Session = Depends(get_db)):
    
    return crud.read_all(db, models.User, skip=skip, limit=limit)

@app.get("/user/", response_model=schemas.User)
def get_user(user_name: str, db: Session = Depends(get_db)):
    db_user = crud.read_user_by_name(db, username=user_name)

    if db_user:
        return db_user
    
    raise HTTPException(status_code=400, detail="User not found")

@app.get("/items/", response_model=list[schemas.Item])
def get_itens(skip: int=0, limit: int=0, db: Session = Depends(get_db)):
    
    return crud.read_all(db, models.Item, skip=skip, limit=limit)

@app.get("/item/", response_model=schemas.Item)
def get_item(item_name: str, user_name: str, db: Session = Depends(get_db)):
    db_user = crud.read_user_by_name(db, username=user_name)

    if db_user:
        user_id = db_user.id
        db_item = crud.read_item_by_name(db, item_name=item_name, user_id=user_id)
        if db_item:
            return db_item
        raise HTTPException(status_code=400, detail="Item not found")

    raise HTTPException(status_code=400, detail="User not found")


#Update
@app.put("/user_name/")
def update_user(User_name: str, password: str, new_username: str, db: Session = Depends(get_db)):
    db_user = crud.read_user_by_name(db, username=User_name)

    if db_user:
        verify = paswrd_verify(db, user_name=User_name, paswrd=password)
        if verify:
            crud.update_username(db, new_username=new_username, user_id=db_user.id)
            return "username updated successfully"
        raise HTTPException(status_code=403, detail="Invalide password")
    
    raise HTTPException(status_code=400, detail="User not found")

@app.put("/user_password/")
def update_user_password(user_name: str, password: str, new_password: str, db: Session = Depends(get_db)):
    db_user = crud.read_user_by_name(db, username=user_name)

    if db_user:
        verify = paswrd_verify(db, user_name=user_name, paswrd=password)
        if verify:
            crud.update_user_paswrd(db, new_paswrd=new_password, user_id=db_user.id)
            return "Password updated successfully"
        raise HTTPException(status_code=403, detail="Invalide password")
    
    raise HTTPException(status_code=400, detail="User not found")

@app.put("/item_quantity/", response_model=schemas.Item)
def update_item_quantity(user_name: str, password: str, item_name: str, item_qnt: int,
db: Session = Depends(get_db)):
    db_user = crud.read_user_by_name(db, username=user_name)

    if db_user:
        verify = paswrd_verify(db, user_name=user_name, paswrd=password)
        if verify:
            db_item = crud.read_item_by_name(db, item_name=item_name, user_id= db_user.id)
            if db_item:
                return crud.update_item_qnt(db, item_id=db_item.id, new_qnt=item_qnt,
                user_id=db_user.id)
            raise HTTPException(status_code=400, detail="Item not found")
        raise HTTPException(status_code=403, detail="Invalide password")
    
    raise HTTPException(status_code=400, detail="User not found")


#delete
@app.delete("/delete_user")
def user_delete(user_name: str, password, db: Session = Depends(get_db)):
    db_user = crud.read_user_by_name(db, username=user_name)

    if db_user:
        verify = paswrd_verify(db, user_name=user_name, paswrd=password)
        if verify:
            crud.delete_user(db, user_id=db_user.id)
            return "Deleted user"
        raise HTTPException(status_code=403, detail="Invalide password")
    
    raise HTTPException(status_code=400, detail="User not found")

@app.delete("/delete_item")
def item_delete(user_name: str, password, item_name: str, db: Session = Depends(get_db)):
    db_user = crud.read_user_by_name(db, username=user_name)

    if db_user:
        verify = paswrd_verify(db, user_name=user_name, paswrd=password)
        if verify:
            db_item = crud.read_item_by_name(db, item_name=item_name, user_id= db_user.id)
            if db_item:
                crud.delete_Item(db, user_id=db_user.id, item_id=db_item.id)
                return "Deleted item"
            raise HTTPException(status_code=400, detail="Item not found")
        raise HTTPException(status_code=403, detail="Invalide password")
    
    raise HTTPException(status_code=400, detail="User not found")
