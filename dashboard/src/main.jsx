
import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  Radar, Plus, Bell, Search, Activity, RefreshCw
} from "lucide-react";
import "./style.css";

function App() {
  const [searches, setSearches] = useState([]);
  const [keyword, setKeyword] = useState("");
  const [price, setPrice] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  async function loadSearches() {
    setLoading(true);
    setError("");

    try {
      const response = await fetch("/api/searches");

      if (!response.ok) {
        throw new Error("Failed to load searches");
      }

      const data = await response.json();
      setSearches(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadSearches();
  }, []);

  async function addSearch(e) {
    e.preventDefault();

    if (!keyword.trim() || !price || Number(price) <= 0) {
      return;
    }

    setSaving(true);
    setError("");

    try {
      const response = await fetch("/api/searches", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          keyword: keyword.trim(),
          max_price: Number(price)
        })
      });

      if (!response.ok) {
        throw new Error("Failed to save search");
      }

      setKeyword("");
      setPrice("");

      await loadSearches();
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <Radar size={28} />
          <span>VintedCatcher</span>
        </div>

        <nav>
          <a className="selected">
            <Activity size={18} /> Dashboard
          </a>
          <a><Search size={18} /> Searches</a>
          <a><Bell size={18} /> Notifications</a>
        </nav>

        <div className="sidebar-footer">
          Version 0.2.0 Alpha
        </div>
      </aside>

      <main className="content">
        <header>
          <div>
            <h1>Dashboard</h1>
            <p>Manage your searches and catch bargains.</p>
          </div>
          <span className="status">
            ● Dashboard online
          </span>
        </header>

        <section className="stats">
          <div className="card">
            <p>Total Searches</p>
            <h2>{searches.length}</h2>
          </div>
          <div className="card">
            <p>Active Searches</p>
            <h2>
              {searches.filter(s => s.active).length}
            </h2>
          </div>
          <div className="card">
            <p>Listings Detected</p>
            <h2>0</h2>
          </div>
          <div className="card">
            <p>Notifications Sent</p>
            <h2>0</h2>
          </div>
        </section>

        <section className="panel">
          <h2><Plus size={20} /> Add New Search</h2>

          <form onSubmit={addSearch} className="search-form">
            <input
              placeholder="Keyword (e.g. PSP 3000)"
              value={keyword}
              onChange={e => setKeyword(e.target.value)}
              required
            />

            <input
              type="number"
              min="0.01"
              step="0.01"
              placeholder="Maximum price (£)"
              value={price}
              onChange={e => setPrice(e.target.value)}
              required
            />

            <button type="submit" disabled={saving}>
              <Plus size={18} />
              {saving ? "Saving..." : "Add Search"}
            </button>
          </form>
        </section>

        <section className="panel">
          <h2><Search size={20} /> Your Searches</h2>

          {error && (
            <p style={{ color: "#fb7185" }}>{error}</p>
          )}

          {loading ? (
            <p>Loading searches...</p>
          ) : searches.length === 0 ? (
            <p>No saved searches yet.</p>
          ) : (
            searches.map(s => (
              <div className="search-row" key={s.id}>
                <div>
                  <strong>{s.keyword}</strong>
                  <p>
                    Maximum: £{Number(s.max_price).toFixed(2)}
                  </p>
                </div>

                <div className="actions">
                  <span className={s.active ? "active" : "paused"}>
                    {s.active ? "Active" : "Paused"}
                  </span>
                </div>
              </div>
            ))
          )}

          <button
            className="icon-button"
            onClick={loadSearches}
            disabled={loading}
            style={{ marginTop: 20 }}
          >
            <RefreshCw size={18} /> Refresh
          </button>
        </section>

        <p className="disclaimer">
          VintedCatcher Alpha. Searches are saved in Cloudflare D1.
          Live monitoring and notifications are not yet connected.
        </p>
      </main>
    </div>
  );
}

createRoot(document.getElementById("root")).render(<App />);
