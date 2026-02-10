import { useEffect, useState } from "react";
import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

function BillsChart() {
  const [chartData, setChartData] = useState(null);

  useEffect(() => {
    // 1. Pobieramy dane z Twojego Flaska
    // UWAGA: Tutaj na sztywno wpisałem pobieranie bez tokena dla testu.
    // Jeśli Twoje API wymaga logowania, musisz dodać nagłówek Authorization.
    fetch("http://127.0.0.1:8000/api/bills/", {
        method: "GET",
        headers: {
            // "Authorization": "Bearer TU_WPISZ_TOKEN_JESLI_MASZ",
            "Content-Type": "application/json"
        }
    })
      .then((res) => res.json())
      .then((data) => {
        if (!Array.isArray(data)) return;

        // 2. Grupujemy dane (Prosta logika)
        const categories = [...new Set(data.map((b) => b.category))];
        
        // Sumujemy dla 2025
        const data2025 = categories.map(cat => 
            data.filter(b => b.category === cat && b.year === 2025)
                .reduce((sum, b) => sum + b.amount, 0)
        );

        // Sumujemy dla 2026
        const data2026 = categories.map(cat => 
            data.filter(b => b.category === cat && b.year === 2026)
                .reduce((sum, b) => sum + b.amount, 0)
        );

        // 3. Ustawiamy dane do wykresu
        setChartData({
          labels: categories,
          datasets: [
            {
              label: "2025",
              data: data2025,
              backgroundColor: "rgba(53, 162, 235, 0.6)",
            },
            {
              label: "2026",
              data: data2026,
              backgroundColor: "rgba(255, 99, 132, 0.6)",
            },
          ],
        });
      })
      .catch(err => console.error("Błąd:", err));
  }, []);

  if (!chartData) return <p>Ładowanie danych z Flaska...</p>;

  return (
    <div style={{ maxWidth: "800px", margin: "50px auto", textAlign: "center" }}>
      <h2>Wydatki Firmowe</h2>
      <Bar data={chartData} />
    </div>
  );
}

export default BillsChart;