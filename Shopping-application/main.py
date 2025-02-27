from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, Products, Cart
from crud import get_all_item, create_product, get_products_by_id, get_all_cart_product, decrement_cart_quantity,restock_product,clear_cart
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)


class ProductCreate(BaseModel):
    name: str
    category: str
    price: int
    quantity: int

class ProductUpdate(BaseModel):
    name: str
    category: str
    price: int
    quantity: int


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def get_product_endpoint(db: Session = Depends(get_db)):
    products = get_all_item(db)
    return products

@app.post("/product")
async def create_product_endpoint(product: ProductCreate, db: Session = Depends(get_db)):
    return create_product(db, product.name, product.category, product.price, product.quantity)


@app.get("/products/{product_id}")
async def get_item_endpoint(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Products).filter(Products.Product_id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found")

    return {
        "Product_id": product.Product_id,
        "Product_name": product.Product_name,
        "Product_category": product.Product_category,
        "price": product.price,
        "Product_quantity": product.Product_quantity
    }


@app.put("/product/{product_id}")
async def update_product_endpoint(
        product_id: int,
        product_data: ProductUpdate,
        db: Session = Depends(get_db)
):
    product = db.query(Products).filter(Products.Product_id == product_id).first()

    if product is None:
        raise HTTPException(status_code=404, detail="Item not found")

    product.Product_name = product_data.name
    product.Product_category = product_data.category
    product.price = product_data.price
    product.Product_quantity = product_data.quantity

    db.commit()
    db.refresh(product)

    return product


@app.delete("/product/{product_id}")
async def delete_item_endpoint(product_id: str, db: Session = Depends(get_db)):
    product = db.query(Products).filter(Products.Product_id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(product)
    db.commit()

    return {"detail": "Product deleted"}


@app.post("/cart/{product_id}")
async def add_to_cart(product_id: int, db: Session = Depends(get_db)):
    print(f"Received request to add product_id {product_id} to cart")  # ✅ Debugging

    product = db.query(Products).filter(Products.Product_id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if product.Product_quantity <= 0:
        raise HTTPException(status_code=400, detail="Product out of stock")

    # Check if product already exists in cart
    cart_item = db.query(Cart).filter(Cart.product_id == product_id).first()

    if cart_item:
        cart_item.cart_quantity += 1
    else:
        cart_item = Cart(
            product_id=product_id,
            cart_quantity=1,
            cart_product_name= product.Product_name,
            cart_price=product.price
        )
        db.add(cart_item)

    # Reduce product quantity from Products table
    product.Product_quantity -= 1

    db.commit()
    db.refresh(cart_item)
    db.refresh(product)

    return {
        "cart_id": cart_item.cart_id,
        "product_id": product.Product_id,
        "product_name": product.Product_name,
        "category": product.Product_category,
        "price": product.price,
        "quantity": cart_item.cart_quantity
    }



@app.get("/cart")
async def get_product_endpoint(db: Session = Depends(get_db)):
    cart_items = get_all_cart_product(db)

    # Convert SQLAlchemy objects into JSON response
    cart_response = [
        {
            "cart_id": item.cart_id,
            "product_id": item.product_id,
            "product_name": item.product.Product_name if item.product else "Unknown",
            "category": item.product.Product_category if item.product else "Unknown",
            "price": item.cart_price,
            "quantity": item.cart_quantity
        }
        for item in cart_items
    ]

    return cart_response

@app.put("/cart/{cart_id}/decrement")
async def decrement_cart_item(cart_id: int, db: Session = Depends(get_db)):
    cart_item = decrement_cart_quantity(db, cart_id)

    if cart_item is None:
        raise HTTPException(status_code=404, detail="Cart item not found")

    return {"message": "Cart quantity updated successfully"}

@app.put("/products/{product_id}/restock")
def restock_endpoint(product_id: int, db: Session = Depends(get_db)):
    return restock_product(db, product_id)


@app.delete("/cart/clear", response_model=dict)
def purchase_items(db: Session = Depends(get_db)):
    clear_cart(db)
    return {"message": "Purchase successful! Cart has been cleared."}