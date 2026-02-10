import { useState } from 'react'

export default function Login({ onLogin }){
  const [username,setUsername]=useState('')
  const [password,setPassword]=useState('')
  const [error,setError]=useState(null)

  const submit = async ()=>{
    setError(null)
    try{
      const res = await fetch('http://127.0.0.1:8001/api/token', {
        method:'POST',
        headers:{'Content-Type':'application/x-www-form-urlencoded'},
        body: new URLSearchParams({username, password})
      })
      if(!res.ok){ setError('Błędne dane'); return }
      const data = await res.json()
      localStorage.setItem('token', data.access_token)
      onLogin()
    }catch(e){ setError('Błąd sieci') }
  }

  return (
    <div style={{maxWidth:420, margin:'4rem auto', padding:20}}>
      <h2>Logowanie (FastAPI)</h2>
      {error && <div style={{color:'salmon'}}>{error}</div>}
      <input placeholder="login" value={username} onChange={e=>setUsername(e.target.value)} />
      <input placeholder="hasło" type="password" value={password} onChange={e=>setPassword(e.target.value)} />
      <button onClick={submit}>Zaloguj</button>
    </div>
  )
}
