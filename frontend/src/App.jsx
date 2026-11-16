import { useEffect, useState } from "react";
import "./App.css";
import TrendChart from "./components/TrendChart.jsx";

const API = "http://127.0.0.1:8000";
const POLL_MS = 2000;

function FlagPill({ flag }) {
  return <span className={`pill ${flag.status}`}>{flag.name}</span>;
}

function PatientCard({ summary, selected, onSelect }) {
  const { patient, latest, flags, flag_count, day, week, baseline_hr } = summary;
  return (
    <button
      className={`card ${flag_count ? "flagged" : ""} ${selected ? "selected" : ""}`}
      onClick={() => onSelect(patient.id)}
    >
      <div className="row">
        <h3>{patient.name}</h3>
        <span className="meta">{day ? `Day ${day} · Week ${week}` : "No data yet"}</span>
      </div>
      <div className="meta">
        {patient.age} yrs · walked {patient.walking_ability} pre-op
      </div>
      <div className="pills">
        {flags.map((f) => (
          <FlagPill key={f.name} flag={f} />
        ))}
      </div>
      {latest && (
        <div className="metrics">
          <div><span>Steps</span>{latest.steps.toLocaleString()}</div>
          <div><span>Resting HR</span>{latest.resting_hr}{baseline_hr ? ` / ${Math.round(baseline_hr)}` : ""}</div>
          <div><span>Sleep</span>{latest.sleep_hours} h</div>
          <div><span>Pain</span>{latest.pain}/10</div>
        </div>
      )}
    </button>
  );
}

function PatientDetail({ detail }) {
  if (!detail) {
    return (
      <div className="detail">
        <div className="empty">Select a patient to see their recovery trend against the expected band.</div>
      </div>
    );
  }

  const { patient, readings, band, flags, day, week, baseline_hr } = detail;
  const steps = readings.map((r) => ({ x: r.day, y: r.steps }));
  const hr = readings.map((r) => ({ x: r.day, y: r.resting_hr }));
  const pain = readings.map((r) => ({ x: r.day, y: r.pain }));
  const sleep = readings.map((r) => ({ x: r.day, y: r.sleep_hours }));
  const lastDay = Math.max(1, day);

  const hrSeries = [{ key: "hr", label: "Resting HR", color: "#f87171", points: hr }];
  if (baseline_hr) {
    hrSeries.push({
      key: "base", label: "Baseline", color: "#9ca3af", dashed: true,
      points: [{ x: 1, y: baseline_hr }, { x: lastDay, y: baseline_hr }],
    });
    hrSeries.push({
      key: "thr", label: "+10 threshold", color: "#f59e0b", dashed: true,
      points: [{ x: 1, y: baseline_hr + 10 }, { x: lastDay, y: baseline_hr + 10 }],
    });
  }

  return (
    <div className="detail">
      <div className="title">
        <h2>{patient.name}</h2>
        <span className="meta">
          Day {day} of recovery · Week {week} · Surgery {patient.surgery_date} · {patient.age} yrs · walked {patient.walking_ability} pre-op
        </span>
      </div>

      <div className="flags">
        {flags.map((f) => (
          <div key={f.name} className={`flag ${f.status}`}>
            <div className="name">{f.name} · {f.status}</div>
            <div className="reason">{f.reason}</div>
          </div>
        ))}
      </div>

      <div className="chart-block">
        <h3>Daily steps against expected recovery band</h3>
        <div className="legend">Shaded area is the expected range for this patient's week and pre-op walking ability.</div>
        <TrendChart
          series={[{ key: "steps", color: "#60a5fa", points: steps }]}
          band={band.map((b) => ({ x: b.day, low: b.low, high: b.high }))}
          yMin={0}
        />
      </div>

      <div className="chart-block">
        <h3>Resting heart rate against personal baseline</h3>
        <div className="legend">Baseline is the mean of the first three days at home. Three days at or above the amber line raises the complication flag.</div>
        <TrendChart series={hrSeries} height={150} />
      </div>

      <div className="chart-block">
        <h3>Pain score and sleep hours</h3>
        <div className="legend">Pain (red, 0 to 10) and sleep (blue, hours). Three days of pain 7+ or short sleep with pain 5+ raises the pain flag.</div>
        <TrendChart
          series={[
            { key: "pain", color: "#f87171", points: pain },
            { key: "sleep", color: "#60a5fa", points: sleep },
          ]}
          yMin={0}
          yMax={10}
          height={150}
        />
      </div>
    </div>
  );
}

export default function App() {
  const [patients, setPatients] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [detail, setDetail] = useState(null);
  const [error, setError] = useState(null);
  const [simulation, setSimulation] = useState(null);

  useEffect(() => {
    let active = true;
    const load = async () => {
      try {
        const [res, health] = await Promise.all([
          fetch(`${API}/patients`),
          fetch(`${API}/health`),
        ]);
        const data = await res.json();
        const status = await health.json();
        if (active) {
          setPatients(data);
          setSimulation(status.simulation);
          setError(null);
        }
      } catch (e) {
        if (active) setError("Backend not reachable");
      }
    };
    load();
    const id = setInterval(load, POLL_MS);
    return () => {
      active = false;
      clearInterval(id);
    };
  }, []);

  useEffect(() => {
    if (selectedId == null) {
      setDetail(null);
      return undefined;
    }
    let active = true;
    const load = async () => {
      try {
        const res = await fetch(`${API}/patients/${selectedId}`);
        const data = await res.json();
        if (active) setDetail(data);
      } catch (e) {
        /* list poll reports the error */
      }
    };
    load();
    const id = setInterval(load, POLL_MS);
    return () => {
      active = false;
      clearInterval(id);
    };
  }, [selectedId]);

  const monitored = patients.length;
  const flagged = patients.filter((p) => p.flag_count > 0).length;
  const onTrack = patients.filter((p) => p.flag_count === 0 && p.day > 0).length;
  const currentDay = Math.max(0, ...patients.map((p) => p.day));
  const demoNote = simulation?.seconds_per_day
    ? `Demo clock: 1 recovery day every ${simulation.seconds_per_day}s, replaying ${simulation.total_days} days. Real readings arrive once a day.`
    : "No simulator attached. Readings arrive once a day from the patient's device.";

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>PulseGuard</h1>
          <div className="sub">Remote recovery monitoring after total knee replacement · GP view</div>
        </div>
        <div className="status">
          <div className="sub">{error ? error : `Recovery day ${currentDay} · dashboard refreshes every ${POLL_MS / 1000}s`}</div>
          <div className="demo-note">{demoNote}</div>
        </div>
      </header>

      <section className="stats">
        <div className="stat blue"><div className="label">Patients monitored</div><div className="value">{monitored}</div></div>
        <div className="stat green"><div className="label">On track</div><div className="value">{onTrack}</div></div>
        <div className="stat red"><div className="label">Flagged for review</div><div className="value">{flagged}</div></div>
        <div className="stat"><div className="label">Recovery week</div><div className="value">{currentDay ? Math.ceil(currentDay / 7) : "–"}</div></div>
      </section>

      <div className="layout">
        <div className="list">
          {patients.map((p) => (
            <PatientCard
              key={p.patient.id}
              summary={p}
              selected={p.patient.id === selectedId}
              onSelect={setSelectedId}
            />
          ))}
        </div>
        <PatientDetail detail={detail} />
      </div>
    </div>
  );
}
