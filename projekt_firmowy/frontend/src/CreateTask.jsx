import { useState } from "react";

function CreateTask() {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [dueDate, setDueDate] = useState("");

  const submitTask = async () => {
    await fetch("http://127.0.0.1:8000/api/tasks/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${localStorage.getItem("token")}`,
      },
      body: JSON.stringify({
        title: title,
        description: description,
        due_date: dueDate,
        assigned_to_ids: [1, 2], // na razie na sztywno
      }),
    });

    alert("Zadanie utworzone!");
  };

  return (
    <div>
      <h2>Dodaj zadanie</h2>

      <input
        placeholder="Tytuł"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
      />

      <textarea
        placeholder="Opis"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
      />

      <input
        type="date"
        value={dueDate}
        onChange={(e) => setDueDate(e.target.value)}
      />

      <button onClick={submitTask}>Zapisz zadanie</button>
    </div>
  );
}

export default CreateTask;
