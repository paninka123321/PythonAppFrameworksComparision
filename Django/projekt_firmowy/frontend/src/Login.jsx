import { useState } from "react";

function Login({ onLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);

  const submit = async () => {
    console.log("SUBMIT CLICKED");

    setError(null);

    try {
      const res = await fetch("http://localhost:8002/api/token/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      console.log("STATUS:", res.status);

      const data = await res.json();
      console.log("DATA:", data);

      if (!res.ok) {
        setError("Błędny login lub hasło");
        return;
      }

      localStorage.setItem("token", data.access);
      console.log("TOKEN SAVED");

      onLogin();
    } catch (err) {
      console.error(err);
      setError("Błąd sieci");
    }
  };

  return (
    <div>
      <h2>Logowanie</h2>

      {error && <p style={{ color: "red" }}>{error}</p>}

      <input
        placeholder="login"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
      />

      <input
        type="password"
        placeholder="hasło"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />

      <button onClick={submit}>Zaloguj</button>
    </div>
  );
}

export default Login;
