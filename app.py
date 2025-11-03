import sys
from datetime import datetime

import pandas as pd
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QHeaderView,
    QPushButton, QDialog, QLabel, QLineEdit, QFormLayout, QMessageBox
)

from backend.database import migrate_db

class InventoryApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🍎 Food Inventory Management")
        self.setGeometry(200, 200, 800, 500)
        self.setStyleSheet("background-color: #f0f2f5;")
        self.setWindowIcon(QIcon("icon.jpg"))

        # Central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Layout
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search by Name or Category...")
        self.search_input.textChanged.connect(self.filter_products)
        self.layout.addWidget(self.search_input)

        # Table to display products
        self.table = QTableWidget()
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.table)
        self.table.setFont(QFont("Segoe UI", 10))
        self.table.setSortingEnabled(True)
        self.table.cellDoubleClicked.connect(self.edit_product_from_table)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setDefaultSectionSize(28)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet("""
            QTableWidget {background-color: #f9f9f9; alternate-background-color: #e6f2ff; gridline-color: #d0d0d0;}
            QHeaderView::section {background-color: #0078d7; color: white; font-weight: bold; padding: 4px; border: 1px solid #d0d0d0;}
        """)
        self.total_label = QLabel("✅ Total Quantity: 0")
        self.total_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.total_label.setAlignment(Qt.AlignRight)
        self.layout.addWidget(self.total_label)

        # Buttons
        self.add_button = QPushButton("➕ Add Product")
        self.edit_button = QPushButton("✏️ Edit Selected Product")
        self.delete_button = QPushButton("🗑️ Delete Selected Product")
        self.refresh_button = QPushButton("🔄 Refresh Products")
        self.alerts_button = QPushButton("⚠️ Check Alerts")
        self.export_button = QPushButton("💾 Export Inventory")

        self.add_button.clicked.connect(self.open_add_dialog)
        self.edit_button.clicked.connect(self.edit_selected_product)
        self.delete_button.clicked.connect(self.delete_selected_product)
        self.refresh_button.clicked.connect(self.load_products)
        self.alerts_button.clicked.connect(self.show_alerts)
        self.export_button.clicked.connect(self.export_inventory)

        # Button layout
        self.button_layout = QHBoxLayout()
        self.button_layout.setSpacing(10)
        self.button_layout.addWidget(self.add_button)
        self.button_layout.addWidget(self.edit_button)
        self.button_layout.addWidget(self.delete_button)
        self.button_layout.addWidget(self.refresh_button)
        self.button_layout.addWidget(self.alerts_button)
        self.button_layout.addWidget(self.export_button)
        self.layout.addLayout(self.button_layout)

        # Load products
        self.load_products()

    def load_products(self):
        from datetime import datetime
        from backend.database import get_products
        from PyQt5.QtCore import Qt
        from PyQt5.QtWidgets import QTableWidgetItem

        products = get_products()
        self.table.setRowCount(len(products))
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["No.", "Name", "Category", "Quantity", "Production Date", "Expiration Date"])

        today = datetime.today()
        low_stock_threshold = 5
        expiry_threshold_days = 7
        total_quantity = 0

        for row_idx, product in enumerate(products):
            product_id, name, category, quantity, prod_date, expiry, created_at = product
            total_quantity += quantity

            # No. column (numeric)
            item_no = QTableWidgetItem()
            item_no.setData(Qt.EditRole, row_idx + 1)
            self.table.setItem(row_idx, 0, item_no)

            # Name
            self.table.setItem(row_idx, 1, QTableWidgetItem(name))
            # Category
            self.table.setItem(row_idx, 2, QTableWidgetItem(category))
            # Quantity (numeric)
            item_qty = QTableWidgetItem()
            item_qty.setData(Qt.EditRole, quantity)
            self.table.setItem(row_idx, 3, item_qty)
            # Production Date
            self.table.setItem(row_idx, 4, QTableWidgetItem(prod_date or ""))
            # Expiration Date
            self.table.setItem(row_idx, 5, QTableWidgetItem(expiry or ""))

            # Highlight low stock
            if quantity <= low_stock_threshold:
                for col in range(self.table.columnCount()):
                    self.table.item(row_idx, col).setBackground(Qt.yellow)

            # Highlight expiring soon
            if expiry:
                try:
                    expiry_date = datetime.strptime(expiry, "%Y-%m-%d")
                    if 0 <= (expiry_date - today).days <= expiry_threshold_days:
                        for col in range(self.table.columnCount()):
                            self.table.item(row_idx, col).setBackground(Qt.red)
                except ValueError:
                    pass

        # Update total label
        self.total_label.setText(f"✅ Total Quantity: {total_quantity}")


    def open_add_dialog(self):
        dialog = AddProductDialog()
        if dialog.exec_():
            self.load_products()

    def edit_product_from_table(self, row, column):
        # Ignore total row (No. column is empty)
        if not self.table.item(row, 0).text().strip():
            return

        from backend.database import get_products
        products = get_products()
        product = products[row]  # get actual product from DB
        dialog = EditProductDialog(product)
        if dialog.exec_():
            self.load_products()

    def edit_selected_product(self):
        selected_row = self.table.currentRow()
        if selected_row < 0 or not self.table.item(selected_row, 0).text().strip():
            return  # nothing selected or total row

        from backend.database import get_products
        products = get_products()
        product = products[selected_row]  # get actual product from DB
        dialog = EditProductDialog(product)
        if dialog.exec_():
            self.load_products()

    def delete_selected_product(self):
        selected_row = self.table.currentRow()
        if selected_row < 0 or not self.table.item(selected_row, 0).text().strip():
            return  # nothing selected or total row

        from backend.database import delete_product, get_products
        products = get_products()
        product_id = products[selected_row][0]  # actual ID from DB
        delete_product(product_id)
        self.load_products()

    def filter_products(self):
        filter_text = self.search_input.text().lower()
        from backend.database import get_products
        from PyQt5.QtCore import Qt
        from PyQt5.QtWidgets import QTableWidgetItem

        products = get_products()
        filtered = []

        # Filter by Name or Category
        for p in products:
            if filter_text in str(p[1]).lower() or filter_text in str(p[2]).lower():
                filtered.append(p)

        self.table.setRowCount(len(filtered))
        total_quantity = 0

        for row_idx, product in enumerate(filtered):
            product_id, name, category, quantity, prod_date, expiry, created_at = product
            total_quantity += quantity

            # No. column
            item_no = QTableWidgetItem()
            item_no.setData(Qt.EditRole, row_idx + 1)
            self.table.setItem(row_idx, 0, item_no)

            # Name
            self.table.setItem(row_idx, 1, QTableWidgetItem(name))
            # Category
            self.table.setItem(row_idx, 2, QTableWidgetItem(category))
            # Quantity
            item_qty = QTableWidgetItem()
            item_qty.setData(Qt.EditRole, quantity)
            self.table.setItem(row_idx, 3, item_qty)
            # Production Date
            self.table.setItem(row_idx, 4, QTableWidgetItem(prod_date or ""))
            # Expiration Date
            self.table.setItem(row_idx, 5, QTableWidgetItem(expiry or ""))

        # Update total label
        self.total_label.setText(f"✅ Total Quantity: {total_quantity}")


    def show_alerts(self):
        from datetime import datetime
        from backend.database import get_products

        products = get_products()
        low_stock_threshold = 5
        expiry_threshold_days = 7

        low_stock = []
        expiring_soon = []
        today = datetime.today()

        for p in products:
            product_id, name, category, quantity, prod_date, expiry, created_at = p
            if quantity <= low_stock_threshold:
                low_stock.append(f"{name} (Qty: {quantity})")
            if expiry:
                try:
                    expiry_date = datetime.strptime(expiry, "%Y-%m-%d")
                    if 0 <= (expiry_date - today).days <= expiry_threshold_days:
                        expiring_soon.append(f"{name} (Expires: {expiry})")
                except ValueError:
                    pass

        message = ""
        if low_stock:
            message += "🔹 Low Stock Products:\n" + "\n".join(low_stock) + "\n\n"
        if expiring_soon:
            message += "🔹 Expiring Soon:\n" + "\n".join(expiring_soon)
        if not message:
            message = "✅ No alerts!"

        QMessageBox.information(self, "Alerts", message)

    def export_inventory(self):
        

        # Gather products from the table (filtered view)
        products = []
        for row in range(self.table.rowCount()):
            # Skip total row (No. column empty)
            if not self.table.item(row, 0) or not self.table.item(row, 0).text().strip():
                continue
            product = [
                self.table.item(row, 0).text(),  # No.
                self.table.item(row, 1).text(),  # Name
                self.table.item(row, 2).text(),  # Category
                int(self.table.item(row, 3).text()),  # Quantity
                self.table.item(row, 4).text(),  # Production Date
                self.table.item(row, 5).text()   # Expiration Date
            ]
            products.append(product)

        if not products:
            QMessageBox.information(self, "Export", "No products to export!")
            return

        # Convert to pandas DataFrame
        df = pd.DataFrame(products, columns=["No.", "Name", "Category", "Quantity", "Production Date", "Expiration Date"])

        # Calculate total quantity
        total_quantity = sum(p[3] for p in products)

        # Append total row
        total_row = {
            "No.": "",
            "Name": "✅ Total",
            "Category": "",
            "Quantity": total_quantity,
            "Production Date": "",
            "Expiration Date": ""
        }
        df = pd.concat([df, pd.DataFrame([total_row])], ignore_index=True)

        # Export to CSV with timestamp to avoid PermissionError
        filename = f"inventory_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(filename, index=False)

        QMessageBox.information(self, "Export", f"Inventory exported successfully to {filename}!")

class AddProductDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("➕ Add New Product")
        self.setGeometry(300, 300, 300, 250)

        self.layout = QFormLayout()
        self.setLayout(self.layout)

        self.name_input = QLineEdit()
        self.category_input = QLineEdit()
        self.quantity_input = QLineEdit()
        self.production_input = QLineEdit()  # YYYY-MM-DD
        self.expiry_input = QLineEdit()      # YYYY-MM-DD

        self.layout.addRow("Name:", self.name_input)
        self.layout.addRow("Category:", self.category_input)
        self.layout.addRow("Quantity:", self.quantity_input)
        self.layout.addRow("Production Date (YYYY-MM-DD):", self.production_input)
        self.layout.addRow("Expiry Date (YYYY-MM-DD):", self.expiry_input)

        self.button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self.add_product)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.close)
        self.button_layout.addWidget(self.add_button)
        self.button_layout.addWidget(self.cancel_button)
        self.layout.addRow(self.button_layout)

    def add_product(self):
        from backend.database import add_product
        try:
            name = self.name_input.text()
            category = self.category_input.text()
            quantity = int(self.quantity_input.text())
            prod_date = self.production_input.text()
            expiry = self.expiry_input.text()

            if not name:
                QMessageBox.warning(self, "Error", "Name cannot be empty!")
                return

            add_product(name, category, quantity, prod_date, expiry)
            QMessageBox.information(self, "Success", f"Product '{name}' added!")
            self.accept()
        except ValueError:
            QMessageBox.warning(self, "Error", "Quantity must be a number!")

class EditProductDialog(QDialog):
    def __init__(self, product):
        super().__init__()
        self.setWindowTitle("✏️ Edit Product")
        self.setGeometry(300, 300, 300, 250)
        self.product_id = int(product[0])

        self.layout = QFormLayout()
        self.setLayout(self.layout)

        self.name_input = QLineEdit(product[1])
        self.category_input = QLineEdit(product[2])
        self.quantity_input = QLineEdit(str(product[3]))
        self.production_input = QLineEdit(product[4])
        self.expiry_input = QLineEdit(product[5])

        self.layout.addRow("Name:", self.name_input)
        self.layout.addRow("Category:", self.category_input)
        self.layout.addRow("Quantity:", self.quantity_input)
        self.layout.addRow("Production Date (YYYY-MM-DD):", self.production_input)
        self.layout.addRow("Expiry Date (YYYY-MM-DD):", self.expiry_input)

        self.button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_changes)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.close)
        self.button_layout.addWidget(self.save_button)
        self.button_layout.addWidget(self.cancel_button)
        self.layout.addRow(self.button_layout)

    def save_changes(self):
        from backend.database import update_product
        try:
            name = self.name_input.text()
            category = self.category_input.text()
            quantity = int(self.quantity_input.text())
            prod_date = self.production_input.text()
            expiry = self.expiry_input.text()

            if not name:
                QMessageBox.warning(self, "Error", "Name cannot be empty!")
                return

            update_product(self.product_id, name, category, quantity, prod_date, expiry)
            QMessageBox.information(self, "Success", f"Product '{name}' updated!")
            self.accept()
        except ValueError:
            QMessageBox.warning(self, "Error", "Quantity must be a number!")
    
# --- Run the app ---
if __name__ == "__main__":
    # init_db() # make sure DB exists
    migrate_db 
    app = QApplication(sys.argv)
    window = InventoryApp()
    window.show()
    sys.exit(app.exec_())
