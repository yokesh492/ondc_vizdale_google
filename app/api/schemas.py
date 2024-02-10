from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class UserBase(BaseModel):
    username : str

class UserCreate(UserBase):
    password : str

class UserLogin(UserBase):
    password : str

class ProductBase(BaseModel):
    name: str
    description: str
    category: str
    sub_categories: List[str]
    image: str
class ProductCreate(ProductBase):
    pass
class Variant(BaseModel):
    size: Optional[str] = None
    flavour: Optional[str] = None

class ProductCatalogCreate(BaseModel):
    # Product fields
    name: str
    description: str
    category: str
    sub_categories: List[str]
    variants: List[Variant]
    image: str

    # Catalog fields
    sku_id: str
    inv: int
    price: int
    discount_price: Optional[int] = None

    # User and Product IDs
    pid: Optional[int] = 0

class CatalogItemBase(BaseModel):
    sku_id: str
    inv: int
    price: int
    discount_price: int
    variants: List[Variant]
    pid: int

class CatalogItemCreate(CatalogItemBase):
    pass
    
class CatalogItemResponse(CatalogItemBase):
    id: int

# class CatalogueResponse(BaseModel):
#     catalogue: List[CatalogueItem]

class InputData(BaseModel):
    input: str

class ProductDetail(BaseModel):
    id : int
    name: str
    description: str
    category: str
    sub_categories: List[str]
    image: str
   
class CatalogDetail(BaseModel):
    catalogid : int
    inv: int
    price: int
    discount_price: Optional[int] = None
    variants: List[Dict[str, Any]]  

class ProductCatalogResponse(BaseModel):
    product: ProductDetail
    catalog: List[CatalogDetail] 

class ProductCatalogDetail(BaseModel):
    product: ProductDetail
    catalog: CatalogDetail