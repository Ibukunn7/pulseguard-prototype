import { useEffect, useState } from "react";

function App() {
  const [vitals, setVitals] = useState([]);

  useEffect(() => {
    const loadVitals = async () => {
      try {
        const response = await fetch(
          "http://127.0.0.1:8000/vitals"
        );

        const data = await response.json();

        setVitals(data);
      } catch (error) {
        console.error(
          "Error fetching vitals:",
          error
        );
      }
    };

    loadVitals();

    const interval = setInterval(
      loadVitals,
      3000
    );

    return () => clearInterval(interval);
  }, []);

  // Latest reading per patient
  const latestVitals = Object.values(
    vitals.reduce((acc, current) => {
      acc[current.reading.patient_id] = current;
      return acc;
    }, {})
  );

  // Dashboard Statistics
  const totalPatients = latestVitals.length;

  const highRiskPatients = latestVitals.filter(
    (entry) => entry.alert === "HIGH RISK"
  ).length;

  const moderateRiskPatients = latestVitals.filter(
    (entry) => entry.alert === "MODERATE RISK"
  ).length;

  const normalPatients = latestVitals.filter(
    (entry) =>
      entry.alert === null ||
      entry.alert === "NORMAL"
  ).length;

  const getStatusColour = (status) => {
    if (status === "HIGH RISK") {
      return "#ef4444";
    }

    if (status === "MODERATE RISK") {
      return "#f59e0b";
    }

    return "#22c55e";
  };

  return (
    <div
      style={{
        padding: "20px",
        maxWidth: "1200px",
        margin: "0 auto",
        fontFamily: "Arial, sans-serif",
      }}
    >
      <h1
        style={{
          textAlign: "center",
          marginBottom: "30px",
        }}
      >
        PulseGuard Dashboard
      </h1>

      {/* Dashboard Statistics */}

      <div
        style={{
          display: "flex",
          gap: "20px",
          flexWrap: "wrap",
          marginBottom: "30px",
        }}
      >
        <div
          style={{
            flex: "1",
            minWidth: "200px",
            backgroundColor: "#1f2937",
            padding: "20px",
            borderRadius: "12px",
            textAlign: "center",
          }}
        >
          <h3>Patients Monitored</h3>
          <h1>{totalPatients}</h1>
        </div>

        <div
          style={{
            flex: "1",
            minWidth: "200px",
            backgroundColor: "#14532d",
            padding: "20px",
            borderRadius: "12px",
            textAlign: "center",
          }}
        >
          <h3>Normal Patients</h3>
          <h1>{normalPatients}</h1>
        </div>

        <div
          style={{
            flex: "1",
            minWidth: "200px",
            backgroundColor: "#78350f",
            padding: "20px",
            borderRadius: "12px",
            textAlign: "center",
          }}
        >
          <h3>Moderate Risk</h3>
          <h1>{moderateRiskPatients}</h1>
        </div>

        <div
          style={{
            flex: "1",
            minWidth: "200px",
            backgroundColor: "#7f1d1d",
            padding: "20px",
            borderRadius: "12px",
            textAlign: "center",
          }}
        >
          <h3>High Risk</h3>
          <h1>{highRiskPatients}</h1>
        </div>
      </div>

      {/* Patient Cards */}

      {latestVitals.map((entry, index) => (
        <div
          key={index}
          style={{
            border: `3px solid ${
              entry.alert === "HIGH RISK"
                ? "#ef4444"
                : entry.alert === "MODERATE RISK"
                ? "#f59e0b"
                : "#22c55e"
            }`,
            borderRadius: "12px",
            padding: "20px",
            marginBottom: "20px",
            backgroundColor: "#111827",
          }}
        >
          <h2>{entry.reading.patient_name}</h2>

          <p>
            <strong>Heart Rate:</strong>{" "}
            {entry.reading.heart_rate} BPM
          </p>

          <p>
            <strong>Sleep Hours:</strong>{" "}
            {entry.reading.sleep_hours}
          </p>

          <p>
            <strong>Last Updated:</strong>{" "}
            {new Date(
              entry.reading.timestamp
            ).toLocaleString()}
          </p>

          <p>
            <strong>Status:</strong>{" "}
            <span
              style={{
                color: getStatusColour(
                  entry.alert
                ),
                fontWeight: "bold",
              }}
            >
              {entry.alert || "NORMAL"}
            </span>
          </p>
        </div>
      ))}
    </div>
  );
}

export default App;