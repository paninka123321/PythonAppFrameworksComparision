import { useEffect, useState } from "react";

function BillsView() {
  const [bills, setBills] = useState([]);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/bills/")
      .then(res => res.json())
      .then(data => setBills(data));
  }, []);

  return (
    <div>
      <h2>Rachunki</h2>

      <table>
        <thead>
          <tr>
            <th>Rok</th>
            <th>Miesiąc</th>
            <th>Kategoria</th>
            <th>Kwota</th>
          </tr>
        </thead>
        <tbody>
          {bills.map(bill => (
            <tr key={bill.id}>
              <td>{bill.year}</td>
              <td>{bill.month}</td>
              <td>{bill.category}</td>
              <td>{bill.amount} zł</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default BillsView;
