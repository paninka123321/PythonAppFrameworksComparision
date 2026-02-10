import { useEffect, useState } from 'react'

export default function BillsView(){
  const [bills,setBills]=useState([])

  useEffect(()=>{
    const load = async ()=>{
      try{
        const token = localStorage.getItem('token')
        const res = await fetch('http://127.0.0.1:8001/api/bills/', { headers: { Authorization: `Bearer ${token}` } })
        if(!res.ok){ setBills([]); return }
        const data = await res.json()
        setBills(data)
      }catch(e){ setBills([]) }
    }
    load()
  },[])

  if(!bills.length) return <div className="card">Brak rachunków.</div>

  return (
    <div>
      {bills.map(b => (
        <div key={b.id} className="card" style={{marginBottom:12}}>
          <div><strong>{b.category}</strong> — {b.amount} zł</div>
          <div className="muted">{b.date}</div>
        </div>
      ))}
    </div>
  )
}
