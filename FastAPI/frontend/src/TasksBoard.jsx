import { useEffect, useState } from 'react'

export default function TasksBoard(){
  const [tasks,setTasks]=useState([])
  const [loading,setLoading]=useState(true)

  useEffect(()=>{
    const load = async ()=>{
      try{
        const token = localStorage.getItem('token')
        const res = await fetch('http://127.0.0.1:8001/api/tasks/', { headers: { Authorization: `Bearer ${token}` } })
        if(!res.ok){ setTasks([]); setLoading(false); return }
        const data = await res.json()
        setTasks(data)
      }catch(e){ setTasks([]) }
      setLoading(false)
    }
    load()
  },[])

  if(loading) return <div>Ładowanie...</div>
  if(!tasks.length) return <div className="card">Brak zadań.</div>

  return (
    <div className="board-container">
      <div style={{flex:1}}>
        {tasks.map(t=> (
          <div key={t.id} className="task-card">
            <div className="task-title">{t.title}</div>
            <div className="task-meta">{t.due_date || '—'}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
