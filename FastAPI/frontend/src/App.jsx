import { useState } from 'react'
import Login from './Login'
import TasksBoard from './TasksBoard'
import BillsView from './BillsView'
import './App.css'

export default function App(){
  const [logged, setLogged] = useState(Boolean(localStorage.getItem('token')))
  const [view, setView] = useState('tasks')

  if(!logged) return <Login onLogin={()=>setLogged(true)} />

  return (
    <div className="dashboard-container">
      <nav className="navbar">
        <div className="brand">Projekt Firmowy (FastAPI)</div>
        <div className="nav-links">
          <button className={`nav-btn ${view==='tasks'?'active':''}`} onClick={()=>setView('tasks')}>✅ Zadania</button>
          <button className={`nav-btn ${view==='bills'?'active':''}`} onClick={()=>setView('bills')}>📋 Rachunki</button>
        </div>
        <button className="logout-btn" onClick={()=>{ localStorage.removeItem('token'); setLogged(false) }}>Wyloguj</button>
      </nav>

      <div className="content-wrapper">
        {view==='tasks' && <TasksBoard />}
        {view==='bills' && <BillsView />}
      </div>
    </div>
  )
}
