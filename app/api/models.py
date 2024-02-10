from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)  # Correct
    products = relationship("Product", back_populates="owner")  # Add this line

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    category = Column(String)
    sub_categories = Column(JSON)
    image = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="products")  # Correct this line
    catalogs = relationship("Catalog", back_populates="product")  # Add this line

class Catalog(Base):
    __tablename__ = "catalogs"
    id = Column(Integer, primary_key=True)
    sku_id = Column(String)
    inv = Column(Integer)
    price = Column(Integer)
    discount_price = Column(Integer)
    variants = Column(JSON)
    pid = Column(Integer, ForeignKey("products.id"))
    product = relationship("Product", back_populates="catalogs")



