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

// --- WAŻNE: Rejestracja komponentów ---
// Bez tego Chart.js nie wie jak rysować osie i słupki
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

function BillsChart() {
  const [chartData, setChartData] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem("token");
    fetch("http://127.0.0.1:8002/api/bills/", {
        headers: { Authorization: `Bearer ${token}` }
    })
      .then((res) => res.json())
      .then((data) => {
        if (!data || data.length === 0) {
            console.log("Brak danych rachunków");
            return;
        }

        // Unikalne kategorie (np. Prąd, Woda)
        const categories = [...new Set(data.map((b) => b.category))];
        
        // Sumowanie kwot dla 2025
        const data2025 = categories.map(cat => 
            data.filter(b => b.category === cat && b.year === 2025)
                .reduce((sum, b) => sum + parseFloat(b.amount), 0)
        );

        // Sumowanie kwot dla 2026
        const data2026 = categories.map(cat => 
            data.filter(b => b.category === cat && b.year === 2026)
                .reduce((sum, b) => sum + parseFloat(b.amount), 0)
        );

        setChartData({
          labels: categories,
          datasets: [
            {
              label: "Koszty 2025",
              data: data2025,
              backgroundColor: "rgba(53, 162, 235, 0.7)",
            },
            {
              label: "Koszty 2026",
              data: data2026,
              backgroundColor: "rgba(255, 99, 132, 0.7)",
            },
          ],
        });
      })
      .catch(err => console.error("Błąd pobierania danych:", err));
  }, []);

  if (!chartData) return <p style={{color: "white", textAlign:"center"}}>Ładowanie wykresu...</p>;

  // Opcje wyglądu wykresu (żeby napisy były białe na ciemnym tle)
  const options = {
    responsive: true,
    plugins: {
      legend: {
        labels: { color: 'white' }
      },
      title: {
        display: true,
        text: 'Porównanie Wydatków',
        color: 'white'
      },
    },
    scales: {
      x: {
        ticks: { color: 'white' },
        grid: { color: '#444' }
      },
      y: {
        ticks: { color: 'white' },
        grid: { color: '#444' }
      }
    }
  };

  return (
    <div style={{ maxWidth: "800px", margin: "0 auto" }}>
      <h2 style={{color: "white", textAlign: "center"}}>Analiza Finansowa</h2>
      <Bar options={options} data={chartData} />
    </div>
  );
}

export default BillsChart;