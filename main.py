from backend.database import add_product

# List of products to add (name, category, quantity, production_date, expiration_date)
products = [
    ("DONUTTO COCO", "", 15, "", ""),
    ("DONUTTO NOISETTE", "", 0, "", ""),
    ("BOKIK", "", 6, "", ""),
    ("MAFINA NATURE 1PCS", "", 5, "", ""),
    ("MAFINA CREME 1PCS", "", 0, "", ""),
    ("MAFINA SAVEUR 1PCS", "", 0, "", ""),
    ("MAFINA NATURE 6P", "", 0, "", ""),
    ("MAFINA CREME 6P", "", 6, "", ""),
    ("MAFINA FRAMBOISE 6P", "", 15, "", ""),
    ("BLEU CAKE NATURE 2PCS", "", 5, "", ""),
    ("BLEU CAKE CREME 2PCS", "", 5, "", ""),
    ("BOWOY ORANGE", "", 0, "", ""),
    ("BOWOY NOISETTE", "", 0, "", ""),
    ("BLEU CAKE NATURE 12PCS", "", 0, "", ""),
    ("BLEU CAKE CREME 12PCS", "", 0, "", ""),
    ("BLEU CAKE FRAISE 12PCS", "", 0, "", ""),
    ("BLEU CAKE NATURE 6PCS", "", 0, "", ""),
    ("BLEU CAKE CREME 6PCS", "", 0, "", ""),
    ("BLEU CAKE FRAISE 6PCS", "", 2, "", ""),
    ("BLEU CAKE ANANAS 6PCS", "", 2, "", "")
]

# Insert into database
for name, category, quantity, prod_date, expiry in products:
    add_product(name=name, category=category, quantity=quantity, production_date=prod_date, expiration_date=expiry)

print("✅ All products added to the database!")

