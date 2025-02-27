from sqlalchemy.orm import Session
from models import Products,Cart

def get_all_item(db: Session):
    return db.query(Products).all()

def get_products_by_id(db: Session, product_id: int):
    product = db.query(Products).filter(Products.Product_id == product_id).first()
    print(f"Looking for product ID {product_id}: {product}")
    return product


def create_product(db: Session, name: str, category: str, price: int, quantity: int):
    db_product = Products(Product_name=name, Product_category=category, price=price, Product_quantity=quantity)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def get_all_cart_product(db: Session):
    return db.query(Cart).all()

def decrement_cart_quantity(db: Session, cart_id: int):
    # Fetch the cart item
    cart_item = db.query(Cart).filter(Cart.cart_id == cart_id).first()

    if cart_item is None:
        return None  # No cart item found

    # Fetch the corresponding product
    product = db.query(Products).filter(Products.Product_id == cart_item.product_id).first()

    if product:
        # Increment product quantity by 1
        product.Product_quantity += 1

    # Decrease cart quantity by 1
    if cart_item.cart_quantity > 1:
        cart_item.cart_quantity -= 1
    else:
        # If quantity reaches 0, remove the cart item
        db.delete(cart_item)

    db.commit()
    db.refresh(product)  # Refresh the product entry
    return cart_item

def restock_product(db: Session, product_id: int):
    product = db.query(Products).filter(Products.Product_id == product_id).first()
    if product:
        product.Product_quantity += 10  # Increment quantity by 10
        db.commit()
        db.refresh(product)
        return {"message": f"Product {product_id} restocked successfully", "new_quantity": product.Product_quantity}
    else:
        return {"error": "Product not found"}

def clear_cart(db: Session):
    """Deletes all items from the cart table."""
    db.query(Cart).delete()
    db.commit()
