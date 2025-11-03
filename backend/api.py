# backend/api.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from database import (
    get_products, add_product, update_product, delete_product, init_db,
    add_sale, get_sales, add_ingredient, get_ingredients, update_ingredient, delete_ingredient
)

app = FastAPI(title="Food Inventory API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Models
# -----------------------------
class ProductIn(BaseModel):
    name: str
    category: str = ""
    quantity: int
    production_date: Optional[str] = ""
    expiration_date: Optional[str] = ""

class ProductOut(ProductIn):
    id: int

class SaleIn(BaseModel):
    product_id: int
    quantity: int
    seller: str
    date: Optional[str] = ""  # YYYY-MM-DD

class SaleOut(SaleIn):
    id: int

class IngredientIn(BaseModel):
    name: str
    quantity: int
    unit: str = ""  # e.g., kg, pcs
    expiration_date: Optional[str] = ""

class IngredientOut(IngredientIn):
    id: int

# -----------------------------
# Helpers
# -----------------------------
def row_to_dict(row):
    return {
        "id": row[0],
        "name": row[1],
        "category": row[2] or "",
        "quantity": row[3] or 0,
        "production_date": row[4] or "",
        "expiration_date": row[5] or "",
    }

def get_product_or_404(product_id: int):
    for r in get_products():
        if r[0] == product_id:
            return r
    raise HTTPException(status_code=404, detail="Product not found")

# -----------------------------
# Startup
# -----------------------------
@app.on_event("startup")
def startup():
    init_db()
 


# -----------------------------
# Product Routes
# -----------------------------
@app.get("/products", response_model=List[ProductOut])
def list_products():
    return [row_to_dict(r) for r in get_products()]

@app.post("/products", response_model=ProductOut)
def create_product(p: ProductIn):
    add_product(p.name, p.category, p.quantity, p.production_date or "", p.expiration_date or "")
    rows = get_products()
    return row_to_dict(rows[-1])

@app.put("/products/{product_id}", response_model=ProductOut)
def edit_product(product_id: int, p: ProductIn):
    _ = get_product_or_404(product_id)
    update_product(product_id, p.name, p.category, p.quantity, p.production_date or "", p.expiration_date or "")
    updated_row = get_product_or_404(product_id)
    return row_to_dict(updated_row)

@app.delete("/products/{product_id}")
def remove_product(product_id: int):
    _ = get_product_or_404(product_id)
    delete_product(product_id)
    return {"ok": True}

# -----------------------------
# Sales Routes
# -----------------------------
@app.get("/sales", response_model=List[SaleOut])
def list_sales():
    return get_sales()

@app.post("/sales", response_model=SaleOut)
def create_sale(s: SaleIn):
    product = get_product_or_404(s.product_id)
    if s.quantity > product[3]:  # quantity check
        raise HTTPException(status_code=400, detail="Not enough stock")
    add_sale(s.product_id, s.quantity, s.seller, s.date or "")
    update_product(product[0], quantity=product[3] - s.quantity)  # subtract sold quantity
    sales = get_sales()
    return sales[-1]

# -----------------------------
# Ingredients Routes
# -----------------------------
@app.get("/ingredients", response_model=List[IngredientOut])
def list_ingredients():
    return get_ingredients()

@app.post("/ingredients", response_model=IngredientOut)
def create_ingredient(i: IngredientIn):
    add_ingredient(i.name, i.quantity, i.unit, i.expiration_date or "")
    ingredients = get_ingredients()
    return ingredients[-1]

@app.put("/ingredients/{ingredient_id}", response_model=IngredientOut)
def edit_ingredient(ingredient_id: int, i: IngredientIn):
    update_ingredient(ingredient_id, i.name, i.quantity, i.unit, i.expiration_date or "")
    ingredients = get_ingredients()
    for ing in ingredients:
        if ing["id"] == ingredient_id:  # ✅ use dictionary key
            return ing
    raise HTTPException(status_code=404, detail="Ingredient not found")


@app.delete("/ingredients/{ingredient_id}")
def remove_ingredient(ingredient_id: int):
    delete_ingredient(ingredient_id)
    return {"ok": True}
