import { useEffect, useState } from "react";
import "./App.css"; 

function TasksBoard() {
  const [tasks, setTasks] = useState([]);
  const [allUsers, setAllUsers] = useState([]); // List of all employees
  const [currentUser, setCurrentUser] = useState({ username: "", is_admin: false });

  // Fetch Data
  useEffect(() => {
    const token = localStorage.getItem("token");
    const headers = { Authorization: `Bearer ${token}` };

    // 1. Get Tasks
    fetch("http://127.0.0.1:8000/api/tasks/", { headers })
      .then((res) => res.json())
      .then((data) => setTasks(data));

    // 2. Get Users (NEW)
    fetch("http://127.0.0.1:8000/api/users/", { headers })
      .then((res) => res.json())
      .then((data) => setAllUsers(data));
    
    // 3. Get Current User info
    fetch("http://127.0.0.1:8000/api/me/", { headers })
      .then((res) => res.json())
      .then((data) => setCurrentUser(data));
  }, []);

  const updateStatus = async (id, newStatus) => {
    // Optimistic UI update
    setTasks(tasks.map(t => t.id === id ? { ...t, status: newStatus } : t));

    await fetch(`http://127.0.0.1:8000/api/tasks/${id}/`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${localStorage.getItem("token")}`,
      },
      body: JSON.stringify({ status: newStatus }),
    });
  };

  // NEW: Function to toggle user assignment
  const toggleUserAssignment = async (task, userId) => {
    // 1. Calculate new list of IDs
    const currentIds = task.assigned_to.map(u => u.id);
    let newIds;
    
    if (currentIds.includes(userId)) {
        // Remove user
        newIds = currentIds.filter(id => id !== userId);
    } else {
        // Add user
        newIds = [...currentIds, userId];
    }

    // 2. Backend Call
    const response = await fetch(`http://127.0.0.1:8000/api/tasks/${task.id}/`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
        body: JSON.stringify({ assigned_to_ids: newIds }),
      });

    // 3. Update Frontend State (Refetching is safest to get full user objects back)
    if (response.ok) {
        const updatedTask = await response.json();
        setTasks(tasks.map(t => t.id === task.id ? updatedTask : t));
    }
  };

  const renderColumn = (status, title) => {
    const columnTasks = tasks.filter((t) => t.status === status);

    return (
      <div className="board-column">
        <h3 className="column-header">{title} ({columnTasks.length})</h3>
        
        {columnTasks.map((task) => (
          <div key={task.id} className="task-card">
            <h4 className="task-title">{task.title}</h4>
            <p className="task-desc">{task.description}</p>
            
            <div className="task-meta">
                Assigned: {task.assigned_to.map(u => u.username).join(", ") || "No one"}
            </div>

            {/* Status Controls */}
            <div style={{ marginTop: "10px", marginBottom: "10px" }}>
                {status !== 'not_started' && 
                  <button className="btn-sm" onClick={() => updateStatus(task.id, 'not_started')}>&lt; Back</button>
                }
                {status !== 'done' && 
                  <button className="btn-sm" onClick={() => updateStatus(task.id, status === 'not_started' ? 'in_process' : 'done')}>Next &gt;</button>
                }
            </div>

             {/* Admin Only Zone - Checklist */}
             {currentUser.is_admin && (
                <div style={{ marginTop: "10px", borderTop: "1px solid #555", paddingTop: "10px" }}>
                    <div style={{fontSize: "0.75rem", color: "#888", marginBottom: "5px"}}>Manage Team:</div>
                    <div style={{display: "flex", flexWrap: "wrap", gap: "5px"}}>
                        {allUsers.map(user => {
                            const isAssigned = task.assigned_to.some(u => u.id === user.id);
                            return (
                                <label key={user.id} style={{
                                    fontSize: "0.8rem", 
                                    background: isAssigned ? "#4caf50" : "#333", 
                                    color: "white",
                                    padding: "2px 6px", 
                                    borderRadius: "4px",
                                    cursor: "pointer",
                                    border: "1px solid #555"
                                }}>
                                    <input 
                                        type="checkbox" 
                                        checked={isAssigned}
                                        onChange={() => toggleUserAssignment(task, user.id)}
                                        style={{display: "none"}} // Hide ugly checkbox, use label styling
                                    />
                                    {user.username} {isAssigned ? "✓" : "+"}
                                </label>
                            )
                        })}
                    </div>
                </div>
            )}
          </div>
        ))}
      </div>
    );
  };

  return (
    <div>
      <h2 style={{ marginTop: 0 }}>Task Board</h2>
      
      {currentUser.is_admin && (
        <p style={{ color: "#4caf50", marginBottom: "20px" }}>
          ✓ Admin Mode: Click names to assign/remove users.
        </p>
      )}
      
      <div className="board-container">
        {renderColumn("not_started", "To Do")}
        {renderColumn("in_process", "In Progress")}
        {renderColumn("done", "Done")}
      </div>
    </div>
  );
}

export default TasksBoard;