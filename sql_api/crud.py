from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import mode
from . import models, schemas


#nesse arquvio deixamos todas as funções de crud no banco de dados
def read_all(db: Session, row, skip: int = 0, limit: int = 100):
    return db.query(row).offset(skip).limit(limit).all()

#users crud
def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"

    db_user = models.User(username=user.username, 
    hashed_password=fake_hashed_password)

    db.add(db_user)
    db.commit()

    return read_user_by_name(db, username=user.username)

def read_user_by_name(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def update_user_paswrd(db: Session, new_paswrd: str, user_id: int):
    db.query(models.User).filter(models.User.id == user_id).update(
    {models.User.hashed_password: new_paswrd})
    db.commit()

def update_username(db: Session, new_username: str, user_id: int):
    db.query(models.User).filter(models.User.id == user_id).update(
    {models.User.username: new_username})
    db.commit()

    return read_user_by_name(db, new_username)

def delete_user(db: Session, user_id: int):
    db.query(models.User).filter(models.User.id == user_id).delete()
    db.commit()


#items crud
def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
    db_item = models.Item(**item.dict(), owner_id=user_id)

    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    return db_item

def read_item_by_name(db: Session, item_name: str, user_id: int):
    return db.query(models.Item).filter(models.Item.item_name == item_name,
    models.Item.owner_id).first()

def update_item_qnt(db: Session, item_id: int, new_qnt: int, user_id: int):
    db.query(models.Item).filter(models.Item.id == item_id,
    models.Item.owner_id == user_id).update(
    {models.Item.quantity: new_qnt})
    db.commit()

    if new_qnt == 0:
        db.query(models.Item).filter(models.Item.id == item_id,
    models.Item.owner_id == user_id).update(
    {models.Item.avaliable: False})
    db.commit()

    return db.query(models.Item).filter(models.Item.id == item_id,
    models.Item.owner_id == user_id).first()

def delete_Item(db: Session, user_id: int, item_id: int):
    db.query(models.Item).filter(models.Item.id == item_id,
    models.Item.owner_id == user_id).delete()
    db.commit()
