from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.mysql import DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Products(Base):
    __tablename__ = "products"

    Product_id = Column(Integer, primary_key=True, index=True)
    Product_name = Column(String(255), index=True, nullable=False)
    Product_category = Column(String(100), index=True, nullable=False)
    price = Column(Integer, nullable=False)
    Product_quantity = Column(Integer, nullable=False)

    cart_items = relationship("Cart", back_populates="product", cascade="all, delete-orphan")


class Cart(Base):
    __tablename__ = "cart"

    cart_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.Product_id", ondelete="CASCADE"), nullable=False)
    cart_product_name = Column(String(255), index=True, nullable=False)
    cart_quantity = Column(Integer, default=1, nullable=False)
    cart_price = Column(DECIMAL(10, 2), nullable=False)

    product = relationship("Products", back_populates="cart_items")
