import { useState } from "react";
import Login from "./Login";
import BillsView from "./BillsView";
import CreateTask from "./CreateTask";
import TasksBoard from "./TasksBoard";
import BillsChart from "./BillsChart";
import "./App.css"; // <--- Import the CSS file

function App() {
  const [loggedIn, setLoggedIn] = useState(
    Boolean(localStorage.getItem("token"))
  );
  const [view, setView] = useState("bills");

  if (!loggedIn) {
    return <Login onLogin={() => setLoggedIn(true)} />;
  }

  return (
    <div className="dashboard-container">
      {/* Navbar Section */}
      <nav className="navbar">
        <h1 style={{ margin: 0, fontSize: "1.5rem" }}>Projekt Firmowy</h1>
        
        <div className="nav-links">
          <button 
            className={`nav-btn ${view === "bills" ? "active" : ""}`} 
            onClick={() => setView("bills")}
          >
            📋 Tabela
          </button>
          <button 
            className={`nav-btn ${view === "charts" ? "active" : ""}`} 
            onClick={() => setView("charts")}
          >
            📊 Wykresy
          </button>
          <button 
            className={`nav-btn ${view === "tasks" ? "active" : ""}`} 
            onClick={() => setView("tasks")}
          >
            ✅ Tablica
          </button>
          <button 
            className={`nav-btn ${view === "create_task" ? "active" : ""}`} 
            onClick={() => setView("create_task")}
          >
            ➕ Dodaj
          </button>
        </div>

        <button
          className="logout-btn"
          onClick={() => {
            localStorage.removeItem("token");
            setLoggedIn(false);
          }}
        >
          Wyloguj
        </button>
      </nav>

      {/* Main Content Area */}
      <div className="content-wrapper">
        {view === "bills" && <BillsView />}
        {view === "charts" && <BillsChart />}
        {view === "tasks" && <TasksBoard />}
        {view === "create_task" && <CreateTask />}
      </div>
    </div>
  );
}

export default App;