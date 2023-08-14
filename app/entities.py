from pydantic import BaseModel, RootModel
from typing import List


class Product(BaseModel):
    name: str


class SystemProduct(BaseModel):
    id: int
    amount: int


class System(BaseModel):
    id: int
    amount: int


class Order(BaseModel):
    products: List[SystemProduct]
    systems: List[System]


class SystemProductList(BaseModel):
    system: List[SystemProduct]


class Email(BaseModel):
    email: str


class ProductStockUpdate(BaseModel):
    remaining_amount: int
    total_amount: int
