import { useState } from "react";
import Login from "./Login";
import BillsView from "./BillsView";
import CreateTask from "./CreateTask";

function App() {
  const [loggedIn, setLoggedIn] = useState(
    Boolean(localStorage.getItem("token"))
  );
  const [view, setView] = useState("bills");

  if (!loggedIn) {
    return <Login onLogin={() => setLoggedIn(true)} />;
  }

  return (
    <div style={{ padding: "2rem" }}>
      <h1>Panel firmowy</h1>

      <nav style={{ marginBottom: "1rem" }}>
        <button onClick={() => setView("bills")}>Rachunki</button>
        <button onClick={() => setView("tasks")}>BBB – Zadania</button>
        <button
          onClick={() => {
            localStorage.removeItem("token");
            setLoggedIn(false);
          }}
        >
          Wyloguj
        </button>
      </nav>

      {view === "bills" && <BillsView />}
      {view === "tasks" && <CreateTask />}
    </div>
  );
}

export default App;
