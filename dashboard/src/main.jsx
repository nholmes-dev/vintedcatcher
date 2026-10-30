
import React, { useState } from "react";
import { createRoot } from "react-dom/client";
import {
  Radar, Plus, Bell, Search, Pause, Play,
  Trash2, Activity
} from "lucide-react";
import "./style.css";

function App() {
  const [searches, setSearches] = useState([
    { id: 1, keyword: "PSP 3000", price: 60, active: true },
    { id: 2, keyword: "Tag Heuer", price: 350, active: true }
  ]);

  const [keyword, setKeyword] = useState("");
  const [price, setPrice] = useState("");

  function addSearch(e) {
    e.preventDefault();
    if (!keyword.trim() || !price || Number(price) <= 0) return;

    setSearches([
      ...searches,
      {
        id: crypto.randomUUID(),
        keyword: keyword.trim(),
        price: Number(price),
        active: true
      }
    ]);

    setKeyword("");
    setPrice("");
  }

  function toggleSearch(id) {
    setSearches(searches.map(s =>
      s.id === id ? { ...s, active: !s.active } : s
    ));
  }

  function deleteSearch(id) {
    setSearches(searches.filter(s => s.id !== id));
  }

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <Radar size={28} />
          <span>VintedCatcher</span>
        </div>

        <nav>
          <a className="selected"><Activity size={18} /> Dashboard</a>
          <a><Search size={18} /> Searches</a>
          <a><Bell size={18} /> Notifications</a>
        </nav>

        <div className="sidebar-footer">Version 0.1.0 Alpha</div>
      </aside>

      <main className="content">
        <header>
          <div>
            <h1>Dashboard</h1>
            <p>Manage your searches and catch bargains.</p>
          </div>
          <span className="status">● Dashboard online</span>
        </header>

        <section className="stats">
          <div className="card">
            <p>Total Searches</p>
            <h2>{searches.length}</h2>
          </div>
          <div className="card">
            <p>Active Searches</p>
            <h2>{searches.filter(s => s.active).length}</h2>
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
            <button type="submit"><Plus size={18} /> Add Search</button>
          </form>
        </section>

        <section className="panel">
          <h2><Search size={20} /> Your Searches</h2>

          {searches.length === 0 && (
            <p>No searches yet. Add your first one above.</p>
          )}

          {searches.map(s => (
            <div className="search-row" key={s.id}>
              <div>
                <strong>{s.keyword}</strong>
                <p>Maximum: £{s.price.toFixed(2)}</p>
              </div>
              <div className="actions">
                <span className={s.active ? "active" : "paused"}>
                  {s.active ? "Active" : "Paused"}
                </span>
                <button
                  className="icon-button"
                  onClick={() => toggleSearch(s.id)}
                  title={s.active ? "Pause" : "Resume"}
                >
                  {s.active ? <Pause size={18} /> : <Play size={18} />}
                </button>
                <button
                  className="icon-button danger"
                  onClick={() => deleteSearch(s.id)}
                  title="Delete"
                >
                  <Trash2 size={18} />
                </button>
              </div>
            </div>
          ))}
        </section>

        <p className="disclaimer">
          Dashboard prototype. Monitoring and notifications are not yet connected.
          Searches are stored only in this browser session.
        </p>
      </main>
    </div>
  );
}

createRoot(document.getElementById("root")).render(<App />);
