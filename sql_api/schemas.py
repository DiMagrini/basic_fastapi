from typing import List, Optional
from pydantic import BaseModel


#Os schemas facilitam a interação com as tabelas no db

#Items
class ItemBase(BaseModel):
    item_name: str
    description: Optional[str] = None
    avaliable: bool
    quantity: int

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True

#users
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str #deixamos informações sensiveis, como senhas, apenas na criação da coluna do usuario.
 #dessa forma podemos exibir as informações do usuario sem necesssariamente comprometer essas informações sensiveis

class User(UserBase):
    id: int
    active: bool
    items: List[Item] = []

    class Config:
        orm_mode = True