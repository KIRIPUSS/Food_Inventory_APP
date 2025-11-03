import { useEffect, useState, useMemo } from "react";
import axios from "axios";
import "./index.css";

const API = "http://127.0.0.1:8000";

export default function App() {
  // ---------- States ----------
  const [section, setSection] = useState("products"); // dashboard section
  const [products, setProducts] = useState([]);
  const [sales, setSales] = useState([]);
  const [ingredients, setIngredients] = useState([]);
  const [q, setQ] = useState("");
  const [theme, setTheme] = useState("light");


  // Forms
  const [productForm, setProductForm] = useState({
    name: "",
    category: "",
    quantity: 0,
    production_date: "",
    expiration_date: "",
  });

  const [saleForm, setSaleForm] = useState({
    product_id: 0,
    quantity: 0,
    seller: "",
    date: "",
  });

  const [ingredientForm, setIngredientForm] = useState({
    name: "",
    quantity: 0,
    unit: "",
    expiration_date: "",
  });

  // ---------- Load Data ----------
  const load = async () => {
    try {
      const [pRes, sRes, iRes] = await Promise.all([
        axios.get(`${API}/products`),
        axios.get(`${API}/sales`),
        axios.get(`${API}/ingredients`),
      ]);
      setProducts(pRes.data);
      setSales(sRes.data);
      setIngredients(iRes.data);
    } catch (err) {
      console.error("❌ Failed to fetch data:", err);
    }
  };

  useEffect(() => { load(); }, []);

  // ---------- Theme ----------
  useEffect(() => {
    async function fetchTheme() {
      if (window.electronAPI?.getSystemTheme) {
        const sysTheme = await window.electronAPI.getSystemTheme();
        setTheme(sysTheme);
        document.documentElement.setAttribute("data-theme", sysTheme);
      }
    }
    fetchTheme();
    if (window.electronAPI?.onThemeChanged) {
      window.electronAPI.onThemeChanged((newTheme) => {
        setTheme(newTheme);
        document.documentElement.setAttribute("data-theme", newTheme);
      });
    }
  }, []);

  // ---------- Filtering & totals ----------
  const filteredProducts = useMemo(() => {
    const s = q.toLowerCase();
    return products.filter(
      (p) =>
        p.name.toLowerCase().includes(s) ||
        (p.category || "").toLowerCase().includes(s)
    );
  }, [products, q]);

  const totalQty = useMemo(
    () => filteredProducts.reduce((a, p) => a + (Number(p.quantity) || 0), 0),
    [filteredProducts]
  );

  // ---------- CRUD ----------
  const addProduct = async () => {
    if (!productForm.name.trim()) return;
    await axios.post(`${API}/products`, { ...productForm, quantity: Number(productForm.quantity) });
    setProductForm({ name: "", category: "", quantity: 0, production_date: "", expiration_date: "" });
    load();
  };

  const updateProduct = async (p) => {
    await axios.put(`${API}/products/${p.id}`, { ...p, quantity: Number(p.quantity) });
    load();
  };

  const deleteProduct = async (id) => { await axios.delete(`${API}/products/${id}`); load(); };

  const addSale = async () => {
  if (!saleForm.product_id || !saleForm.seller || !saleForm.quantity) return;

  try {
    await axios.post(`${API}/sales`, {
      product_id: Number(saleForm.product_id),
      quantity: Number(saleForm.quantity),
      seller: saleForm.seller,
      date: saleForm.date || new Date().toISOString().slice(0, 10)
    });

    setSaleForm({ product_id: 0, quantity: 0, seller: "", date: "" });
    load(); // reload products to update stock
  } catch (err) {
    console.error("❌ Failed to add sale:", err.response?.data || err.message);
    alert(err.response?.data?.detail || "Failed to add sale");
  }
};

  const addIngredient = async () => {
    if (!ingredientForm.name || !ingredientForm.quantity) return;
    await axios.post(`${API}/ingredients`, { ...ingredientForm, quantity: Number(ingredientForm.quantity) });
    setIngredientForm({ name: "", quantity: 0, unit: "", expiration_date: "" });
    load();
  };
  const deleteIngredient = async (id) => { await axios.delete(`${API}/ingredients/${id}`); load(); };

  const [editingIngredient, setEditingIngredient] = useState(null);
  const startEdit = (ingredient) => {
  setEditingIngredient({ ...ingredient }); // copy to avoid direct mutation
};
  const cancelEdit = () => {
  setEditingIngredient(null);
};
  const updateIngredient = async (id, updatedData) => {
  try {
    await axios.put(`${API}/ingredients/${id}`, updatedData);
    load(); // reload updated list
    setEditingIngredient(null); // exit edit mode
  } catch (err) {
    console.error("Error updating ingredient:", err);
  }
};


const exportSalesCSV = () => {
  if (!filteredSales.length) return alert("No sales to export");

  const headers = ["No.", "Product", "Qty", "Seller", "Date"];
  const rows = filteredSales.map((s, idx) => [
    idx + 1,
    products.find(p => p.id === s.product_id)?.name || "Deleted",
    s.quantity,
    s.seller,
    s.date || "—"
  ]);

  const csvContent =
    "data:text/csv;charset=utf-8," +
    [headers, ...rows].map(e => e.join(",")).join("\n");

  const encodedUri = encodeURI(csvContent);
  const link = document.createElement("a");
  link.setAttribute("href", encodedUri);
  link.setAttribute("download", `sales_${new Date().toISOString().slice(0,10)}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};


const [salesFilterDate, setSalesFilterDate] = useState({ from: "", to: "" });

const filteredSales = sales.filter(s => {
  if (!salesFilterDate.from && !salesFilterDate.to) return true;

  // Take only the date part in case s.date includes time
  const saleDateStr = s.date ? s.date.split("T")[0] : "";

  if (salesFilterDate.from && saleDateStr < salesFilterDate.from) return false;
  if (salesFilterDate.to && saleDateStr > salesFilterDate.to) return false;

  return true;
});

const clearSalesFilter = () => {
  setSalesFilterDate({ from: "", to: "" });
};



// ---------- Render ----------
return (
  <div
    className={`min-h-screen p-6 ${
      theme === "dark" ? "bg-slate-800 text-gray-100" : "bg-slate-100 text-black"
    }`}
  >
    <div className="max-w-6xl mx-auto space-y-6">

      {/* Header */}
      <header className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">🍎 Food Dashboard</h1>
        <div className="flex gap-2 items-center">
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="🔍 Search..."
            className={`px-3 py-2 rounded-lg border w-64 ${
              theme === "dark"
                ? "bg-gray-700 text-gray-100 border-gray-600"
                : "bg-white text-black border-gray-300"
            }`}
          />
          <span className="italic opacity-80">Theme: {theme}</span>

          {/* Theme Toggle Button */}
          <button
            onClick={() => {
              const newTheme = theme === "dark" ? "light" : "dark";
              setTheme(newTheme);
              document.documentElement.setAttribute("data-theme", newTheme);
            }}
            className={`px-3 py-2 rounded ${
              theme === "dark"
                ? "bg-gray-600 text-white hover:bg-gray-500"
                : "bg-gray-200 text-black hover:bg-gray-300"
            }`}
          >
            Change Theme
          </button>
        </div>
      </header>

      {/* Navigation */}
      <nav className="flex gap-4 mb-4">
        {["products", "sales", "ingredients"].map((sec) => (
          <button
            key={sec}
            onClick={() => setSection(sec)}
            className={`px-4 py-2 rounded ${
              section === sec
                ? "bg-blue-600 text-white"
                : theme === "dark"
                ? "bg-gray-700 text-gray-100"
                : "bg-gray-200 text-black"
            }`}
          >
            {sec}
          </button>
        ))}
      </nav>

      {/* ---------- PRODUCTS ---------- */}
      {section === "products" && (
        <div className="space-y-4">
          {/* Form */}
          <div
            className={`shadow p-4 rounded-lg border ${
              theme === "dark" ? "bg-gray-700 border-gray-600" : "bg-white border-gray-300"
            }`}
          >
            <h3 className="font-semibold mb-3">Add Product</h3>
            <div className="grid grid-cols-6 gap-2">
              {["name", "category", "quantity", "production_date", "expiration_date"].map(
                (f) => (
                  <input
                    key={f}
                    type={f === "quantity" ? "number" : "text"}
                    placeholder={f}
                    value={productForm[f]}
                    onChange={(e) =>
                      setProductForm({
                        ...productForm,
                        [f]: f === "quantity" ? parseInt(e.target.value) || 0 : e.target.value,
                      })
                    }
                    className={`border px-2 py-1 rounded w-full ${
                      theme === "dark"
                        ? "bg-gray-600 text-gray-100 border-gray-500"
                        : "bg-white text-black"
                    }`}
                  />
                )
              )}
              <button
                onClick={addProduct}
                className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
              >
                ➕ Add
              </button>
            </div>
          </div>

          {/* Table */}
          <div className="overflow-x-auto border rounded-lg shadow-sm">
            <table
              className={`min-w-full text-left border-collapse ${
                theme === "dark" ? "bg-gray-700 text-gray-100" : "bg-white text-black"
              }`}
            >
              <thead className={`${theme === "dark" ? "bg-gray-600" : "bg-slate-200"}`}>
                <tr>
                  <th className="px-4 py-2 w-12">No.</th>
                  <th className="px-4 py-2">Name</th>
                  <th className="px-4 py-2">Category</th>
                  <th className="px-4 py-2 w-24 text-right">Qty</th>
                  <th className="px-4 py-2">Production</th>
                  <th className="px-4 py-2">Expiration</th>
                  <th className="px-4 py-2">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredProducts.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="text-center py-4 text-gray-400">
                      No products yet
                    </td>
                  </tr>
                ) : (
                  filteredProducts.map((p, idx) => (
                    <tr
                     key={p.id}
                      className={`border-t ${
                      theme === "dark" ? "hover:bg-gray-500" : "hover:bg-gray-50"
                        }`}
                    >
                      <td className="px-4 py-2 text-center">{idx + 1}</td>
                      {["name", "category", "quantity", "production_date", "expiration_date"].map(
                        (f) => (
                          <td key={f} className="px-2 py-1">
                            <input
                              value={p[f] || ""}
                              onChange={(e) =>
                                updateProduct({
                                  ...p,
                                  [f]: f === "quantity" ? Number(e.target.value) : e.target.value,
                                })
                              }
                              className={`border px-1 py-1 w-full rounded ${
                                theme === "dark"
                                  ? "bg-gray-600 text-gray-100 border-gray-500"
                                  : "bg-white text-black"
                              }`}
                            />
                          </td>
                        )
                      )}
                      <td className="px-2 py-1 flex gap-2">
                        <button
  onClick={() => deleteProduct(p.id)}
  className={`px-2 py-1 rounded ${
  theme === "dark"
    ? "bg-red-700 text-red-200 hover:bg-red-600"
    : "bg-red-100 text-red-700 hover:bg-red-200"
}`}

>
  🗑 Delete
</button>

                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
          <div className="text-right font-semibold mt-2">✅ Total Quantity: {totalQty}</div>
        </div>
      )}

      {/* ---------- SALES ---------- */}
      {section === "sales" && (
        <div className="space-y-4">
          {/* Form */}
          <div
            className={`shadow p-4 rounded-lg border flex flex-wrap gap-2 items-center ${
              theme === "dark" ? "bg-gray-700 border-gray-600" : "bg-white border-gray-300"
            }`}
          >
            <select
              value={saleForm.product_id}
              onChange={(e) => setSaleForm({ ...saleForm, product_id: Number(e.target.value) })}
              className={`border rounded px-3 py-2 ${
                theme === "dark" ? "bg-gray-600 text-gray-100 border-gray-500" : "bg-white text-black"
              }`}
            >
              <option value={0}>Select Product</option>
              {products.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
            <input
              type="number"
              placeholder="Qty"
              value={saleForm.quantity}
              onChange={(e) => setSaleForm({ ...saleForm, quantity: Number(e.target.value) })}
              className={`border rounded px-3 py-2 w-24 ${
                theme === "dark" ? "bg-gray-600 text-gray-100 border-gray-500" : "bg-white text-black"
              }`}
            />
            <input
              placeholder="Seller"
              value={saleForm.seller}
              onChange={(e) => setSaleForm({ ...saleForm, seller: e.target.value })}
              className={`border rounded px-3 py-2 ${
                theme === "dark" ? "bg-gray-600 text-gray-100 border-gray-500" : "bg-white text-black"
              }`}
            />
            <input
              type="date"
              value={saleForm.date}
              onChange={(e) => setSaleForm({ ...saleForm, date: e.target.value })}
              className={`border rounded px-3 py-2 ${
                theme === "dark" ? "bg-gray-600 text-gray-100 border-gray-500" : "bg-white text-black"
              }`}
            />
            <button
              onClick={addSale}
              className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition"
            >
              Record Sale
            </button>
            <button
              onClick={exportSalesCSV}
              className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded"
            >
              ⬇ Export CSV
            </button>
          </div>

          {/* Date Filter */}
          <div className="flex gap-2 items-center mb-2">
            <label className="text-sm">From:</label>
            <input
              type="date"
              value={salesFilterDate.from}
              onChange={(e) =>
                setSalesFilterDate({ ...salesFilterDate, from: e.target.value })
              }
              className={`border rounded px-3 py-2 ${
                theme === "dark" ? "bg-gray-600 text-gray-100 border-gray-500" : "bg-white text-black"
              }`}
            />
            <label className="text-sm">To:</label>
            <input
              type="date"
              value={salesFilterDate.to}
              onChange={(e) =>
                setSalesFilterDate({ ...salesFilterDate, to: e.target.value })
              }
              className={`border rounded px-3 py-2 ${
                theme === "dark" ? "bg-gray-600 text-gray-100 border-gray-500" : "bg-white text-black"
              }`}
            />
            <button
              onClick={clearSalesFilter}
className={`px-2 py-1 rounded ${
  theme === "dark"
    ? "bg-red-700 text-red-200 hover:bg-red-600"
    : "bg-red-100 text-red-700 hover:bg-red-200"
}`}
            >
              ❌ Clear
            </button>
          </div>

          {/* Table */}
          <div className="overflow-x-auto border rounded-lg shadow-sm">
            <table
              className={`min-w-full text-left border-collapse ${
                theme === "dark" ? "bg-gray-700 text-gray-100" : "bg-white text-black"
              }`}
            >
              <thead className={`${theme === "dark" ? "bg-gray-600" : "bg-slate-200"}`}>
                <tr>
                  <th className="px-4 py-2 w-12">No.</th>
                  <th className="px-4 py-2">Product</th>
                  <th className="px-4 py-2 w-24 text-right">Qty</th>
                  <th className="px-4 py-2">Seller</th>
                  <th className="px-4 py-2 w-36">Date</th>
                </tr>
              </thead>
              <tbody>
                {filteredSales.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="text-center py-4 text-gray-400">
                      No sales recorded
                    </td>
                  </tr>
                ) : (
                  filteredSales.map((s, idx) => (
                    <tr
                      key={s.id}
                      className={`border-t ${theme === "dark" ? "hover:bg-gray-600" : "hover:bg-slate-50"}`}
                    >
                      <td className="px-4 py-2 text-center">{idx + 1}</td>
                      <td className="px-4 py-2">
                        {products.find((p) => p.id === s.product_id)?.name || "Deleted"}
                      </td>
                      <td className="px-4 py-2 text-right">{s.quantity}</td>
                      <td className="px-4 py-2">{s.seller}</td>
                      <td className="px-4 py-2">{s.date || "—"}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ---------- INGREDIENTS ---------- */}
      {section === "ingredients" && (
        <div className="space-y-4">
          {/* Form */}
          <div
            className={`shadow p-4 rounded-lg border ${
              theme === "dark" ? "bg-gray-700 border-gray-600" : "bg-white border-gray-300"
            }`}
          >
            <h3 className="font-semibold mb-3">Add Ingredient</h3>
            <div className="grid grid-cols-5 gap-2">
              <input
                className={`border rounded p-2 ${
                  theme === "dark" ? "bg-gray-600 text-gray-100 border-gray-500" : "bg-white text-black"
                }`}
                placeholder="Name"
                value={ingredientForm.name}
                onChange={(e) => setIngredientForm({ ...ingredientForm, name: e.target.value })}
              />
              <input
                className={`border rounded p-2 ${
                  theme === "dark" ? "bg-gray-600 text-gray-100 border-gray-500" : "bg-white text-black"
                }`}
                placeholder="Qty"
                type="number"
                value={ingredientForm.quantity}
                onChange={(e) => setIngredientForm({ ...ingredientForm, quantity: Number(e.target.value) })}
              />
              <input
                className={`border rounded p-2 ${
                  theme === "dark" ? "bg-gray-600 text-gray-100 border-gray-500" : "bg-white text-black"
                }`}
                placeholder="Unit"
                value={ingredientForm.unit}
                onChange={(e) => setIngredientForm({ ...ingredientForm, unit: e.target.value })}
              />
              <input
                className={`border rounded p-2 ${
                  theme === "dark" ? "bg-gray-600 text-gray-100 border-gray-500" : "bg-white text-black"
                }`}
                type="date"
                value={ingredientForm.expiration_date}
                onChange={(e) => setIngredientForm({ ...ingredientForm, expiration_date: e.target.value })}
              />
              <button
                onClick={addIngredient}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 rounded"
              >
                ➕ Add
              </button>
            </div>
          </div>

          {/* Table */}
          <div className="overflow-x-auto border rounded-lg shadow-sm">
            <table
              className={`min-w-full text-left border-collapse ${
                theme === "dark" ? "bg-gray-700 text-gray-100" : "bg-white text-black"
              }`}
            >
              <thead className={`${theme === "dark" ? "bg-gray-600" : "bg-slate-200"}`}>
                <tr>
                  <th className="px-4 py-2 w-12">No.</th>
                  <th className="px-4 py-2">Name</th>
                  <th className="px-4 py-2 w-24">Qty</th>
                  <th className="px-4 py-2 w-24">Unit</th>
                  <th className="px-4 py-2 w-36">Expiration</th>
                  <th className="px-4 py-2">Actions</th>
                </tr>
              </thead>
              <tbody>
                {ingredients.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="text-center py-4 text-gray-400">
                      No ingredients yet
                    </td>
                  </tr>
                ) : (
                  ingredients.map((i, idx) => (
                    <tr
                      key={i.id}
                      className={`border-t ${theme === "dark" ? "hover:bg-gray-600" : "hover:bg-slate-50"}`}
                    >
                      <td className="px-4 py-2 text-center">{idx + 1}</td>

                      {editingIngredient && editingIngredient.id === i.id ? (
                        <>
                          <td className={`px-2 py-1`}>
                            <input
                              className={`border px-1 py-1 w-full rounded ${
                                theme === "dark"
                                  ? "bg-gray-600 text-gray-100 border-gray-500"
                                  : "bg-white text-black"
                              }`}
                              value={editingIngredient.name}
                              onChange={(e) =>
                                setEditingIngredient({ ...editingIngredient, name: e.target.value })
                              }
                            />
                          </td>
                          <td className="px-2 py-1">
                            <input
                              className={`border px-1 py-1 w-20 rounded ${
                                theme === "dark"
                                  ? "bg-gray-600 text-gray-100 border-gray-500"
                                  : "bg-white text-black"
                              }`}
                              type="number"
                              value={editingIngredient.quantity}
                              onChange={(e) =>
                                setEditingIngredient({ ...editingIngredient, quantity: Number(e.target.value) })
                              }
                            />
                          </td>
                          <td className="px-2 py-1">
                            <input
                              className={`border px-1 py-1 w-24 rounded ${
                                theme === "dark"
                                  ? "bg-gray-600 text-gray-100 border-gray-500"
                                  : "bg-white text-black"
                              }`}
                              value={editingIngredient.unit}
                              onChange={(e) =>
                                setEditingIngredient({ ...editingIngredient, unit: e.target.value })
                              }
                            />
                          </td>
                          <td className="px-2 py-1">
                            <input
                              className={`border px-1 py-1 rounded ${
                                theme === "dark"
                                  ? "bg-gray-600 text-gray-100 border-gray-500"
                                  : "bg-white text-black"
                              }`}
                              type="date"
                              value={editingIngredient.expiration_date}
                              onChange={(e) =>
                                setEditingIngredient({ ...editingIngredient, expiration_date: e.target.value })
                              }
                            />
                          </td>
                          <td className="px-2 py-1 flex gap-2">
                            <button
                              onClick={() => updateIngredient(editingIngredient.id, editingIngredient)}
                              className="bg-green-600 text-white px-2 py-1 rounded hover:bg-green-700"
                            >
                              💾 Save
                            </button>
                            <button
                              onClick={cancelEdit}
                              className="bg-gray-400 text-white px-2 py-1 rounded hover:bg-gray-500"
                            >
                              ❌ Cancel
                            </button>
                          </td>
                        </>
                      ) : (
                        <>
                          <td className="px-4 py-2">{i.name}</td>
                          <td className="px-4 py-2 text-right">{i.quantity}</td>
                          <td className="px-4 py-2">{i.unit}</td>
                          <td className="px-4 py-2">{i.expiration_date}</td>
                          <td className="px-4 py-2 flex gap-2">
                            <button
  onClick={() => startEdit(i)}
  className={`px-2 py-1 rounded ${
  theme === "dark"
    ? "bg-blue-700 text-blue-200 hover:bg-blue-600"
    : "bg-blue-100 text-blue-700 hover:bg-blue-200"
}`}

>
  ✏ Edit
</button>
                            <button
                              onClick={() => deleteIngredient(i.id)}
                            className={`px-2 py-1 rounded ${
  theme === "dark"
    ? "bg-red-700 text-red-200 hover:bg-red-600"
    : "bg-red-100 text-red-700 hover:bg-red-200"
}`}
                          >
                            🗑 Delete
                            </button>
                          </td>
                        </>
                      )}
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  </div>
);



}
