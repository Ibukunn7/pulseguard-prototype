import { useEffect, useState } from "react";

function App() {
  const [vitals, setVitals] = useState([]);

  useEffect(() => {
    const loadVitals = async () => {
      const response = await fetch(
        "http://127.0.0.1:8000/vitals"
      );

      const data = await response.json();

      setVitals(data);
    };

    loadVitals();

    const interval = setInterval(
      loadVitals,
      3000
    );

    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ padding: "20px" }}>
      <h1>PulseGuard Dashboard</h1>

      {vitals.map((entry, index) => (
        <div
          key={index}
          style={{
            border: "1px solid #ddd",
            padding: "10px",
            marginBottom: "10px",
            borderRadius: "8px"
          }}
        >
          <h3>{entry.reading.patient_name}</h3>

          <p>
            Heart Rate: {entry.reading.heart_rate}
          </p>

          <p>
            Sleep Hours: {entry.reading.sleep_hours}
          </p>

          <p>
            Status:
            {" "}
            <strong>
              {entry.alert || "Normal"}
            </strong>
          </p>
        </div>
      ))}
    </div>
  );
}

export default App;