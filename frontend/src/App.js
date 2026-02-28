import React, { useEffect, useState } from "react";
import axios from "axios";

function App() {
  // ==========================================
  // EXACT ORIGINAL LOGIC - UNTOUCHED
  // ==========================================
  const [alerts, setAlerts] = useState([]);
  const [logs, setLogs] = useState([]);
  const [status, setStatus] = useState("PROTECTED");

  useEffect(() => {
    fetchLogs();
    const interval = setInterval(fetchLogs, 5000);

    const socket = new WebSocket("ws://127.0.0.1:8000/ws");

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setAlerts(prev => [data, ...prev]);
      setStatus("UNDER ATTACK");
    };

    return () => {
      socket.close();
      clearInterval(interval);
    };
  }, []);

  const fetchLogs = async () => {
    const res = await axios.get("http://127.0.0.1:8000/logs");
    setLogs(res.data);
  };

  const totalLogs = logs.length;
  const criticalCount = logs.filter(log => log[9] === "Critical").length;
  const highCount = logs.filter(log => log[9] === "High").length;
  const mediumCount = logs.filter(log => log[9] === "Medium").length;
  const lowCount = logs.filter(log => log[9] === "Low").length;
  // ==========================================

  // UI Upgrade Variables
  const isProtected = status === "PROTECTED";
  const neonGreen = "#00ff88";
  const neonRed = "#ff003c";

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');
        
        body { margin: 0; background-color: #050b14; color: #ffffff; font-family: 'Inter', sans-serif; }
        
        @keyframes pulse-red {
          0% { box-shadow: 0 0 0 0 rgba(255, 0, 60, 0.7); }
          70% { box-shadow: 0 0 0 20px rgba(255, 0, 60, 0); }
          100% { box-shadow: 0 0 0 0 rgba(255, 0, 60, 0); }
        }

        .glass-panel {
          background: rgba(17, 25, 40, 0.75);
          backdrop-filter: blur(12px);
          -webkit-backdrop-filter: blur(12px);
          border: 1px solid rgba(255, 255, 255, 0.125);
          border-radius: 12px;
        }

        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: #050b14; }
        ::-webkit-scrollbar-thumb { background: #1f2937; border-radius: 10px; }
        ::-webkit-scrollbar-thumb:hover { background: #374151; }
      `}</style>

      <div style={{ padding: "30px", maxWidth: "1600px", margin: "0 auto", display: "flex", flexDirection: "column", gap: "24px", minHeight: "100vh" }}>
        
        {/* Header & Global Status */}
        <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <h1 style={{ fontSize: "32px", margin: 0, fontWeight: "800", letterSpacing: "-1px", background: "linear-gradient(90deg, #ffffff, #8892b0)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>
            AI-SIEM Dashboard
          </h1>
          
          <div style={{
            backgroundColor: isProtected ? "rgba(0, 255, 136, 0.1)" : "rgba(255, 0, 60, 0.1)",
            color: isProtected ? neonGreen : neonRed,
            border: `1px solid ${isProtected ? neonGreen : neonRed}`,
            padding: "12px 30px",
            borderRadius: "50px",
            fontSize: "16px",
            fontWeight: "800",
            letterSpacing: "2px",
            animation: isProtected ? "none" : "pulse-red 1.5s infinite",
            textTransform: "uppercase"
          }}>
            {status}
          </div>
        </header>

        {/* Metrics Row */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: "20px" }}>
          <Card title="Total Logs" value={totalLogs} glowColor="#4facfe" />
          <Card title="Critical" value={criticalCount} glowColor={neonRed} />
          <Card title="High" value={highCount} glowColor="#ff9a44" />
          <Card title="Medium" value={mediumCount} glowColor="#f6d365" />
          <Card title="Low" value={lowCount} glowColor="#2af598" />
        </div>

        {/* Main Content Grid */}
        <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: "24px", alignItems: "start" }}>
          
          {/* Logs Table */}
          <div className="glass-panel" style={{ padding: "24px", overflowX: "auto" }}>
            <h2 style={{ marginTop: 0, fontSize: "20px", color: "#e2e8f0", borderBottom: "1px solid rgba(255,255,255,0.1)", paddingBottom: "12px", marginBottom: "16px" }}>
              Network Activity Log
            </h2>
            <table style={{ width: "100%", borderCollapse: "collapse", textAlign: "left", fontSize: "14px" }}>
              <thead>
                <tr style={{ color: "#94a3b8", textTransform: "uppercase", letterSpacing: "1px", fontSize: "12px" }}>
                  <th style={{ padding: "12px" }}>ID</th>
                  <th style={{ padding: "12px" }}>IP Address</th>
                  <th style={{ padding: "12px" }}>Event</th>
                  <th style={{ padding: "12px" }}>Threat</th>
                </tr>
              </thead>
              <tbody>
                {logs.slice(0, 10).map((log, index) => (
                  <tr key={index} style={{ borderBottom: "1px solid rgba(255,255,255,0.05)", transition: "background 0.2s" }} onMouseOver={e => e.currentTarget.style.backgroundColor = "rgba(255,255,255,0.02)"} onMouseOut={e => e.currentTarget.style.backgroundColor = "transparent"}>
                    <td style={{ padding: "14px 12px", color: "#64748b" }}>{log[0]}</td>
                    <td style={{ padding: "14px 12px", fontFamily: "'JetBrains Mono', monospace", color: "#e2e8f0" }}>{log[2]}</td>
                    <td style={{ padding: "14px 12px", color: "#cbd5e1" }}>{log[3]}</td>
                    <td style={{ padding: "14px 12px" }}>
                      <span style={{
                        color: log[9] === "Critical" ? neonRed : log[9] === "High" ? "#ff9a44" : log[9] === "Medium" ? "#f6d365" : "#2af598",
                        fontWeight: "600",
                        textShadow: `0 0 10px ${log[9] === "Critical" ? "rgba(255,0,60,0.5)" : "transparent"}`
                      }}>
                        {log[9]}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Live Alerts Feed */}
          <div className="glass-panel" style={{ padding: "24px", display: "flex", flexDirection: "column", height: "500px" }}>
            <h2 style={{ marginTop: 0, fontSize: "20px", color: neonRed, borderBottom: "1px solid rgba(255,255,255,0.1)", paddingBottom: "12px", marginBottom: "16px", display: "flex", alignItems: "center", gap: "10px" }}>
              <span style={{ width: "10px", height: "10px", backgroundColor: neonRed, borderRadius: "50%", display: "inline-block", boxShadow: `0 0 10px ${neonRed}` }}></span>
              Live Interventions
            </h2>
            
            <div style={{ overflowY: "auto", display: "flex", flexDirection: "column", gap: "12px", flexGrow: 1, paddingRight: "5px" }}>
              {alerts.length === 0 ? (
                <div style={{ margin: "auto", color: "#64748b", fontStyle: "italic", fontSize: "14px" }}>
                  System operating normally. No live threats.
                </div>
              ) : (
                alerts.map((alert, index) => (
                  <div key={index} style={{
                    backgroundColor: "rgba(255, 0, 60, 0.05)",
                    borderLeft: `3px solid ${neonRed}`,
                    padding: "16px",
                    borderRadius: "0 6px 6px 0",
                    position: "relative",
                    overflow: "hidden"
                  }}>
                    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "8px" }}>
                      <span style={{ fontFamily: "'JetBrains Mono', monospace", color: "#fff", fontWeight: "700" }}>{alert.source_ip}</span>
                      <span style={{ color: neonRed, fontWeight: "800", fontSize: "12px", textTransform: "uppercase" }}>{alert.threat_level}</span>
                    </div>
                    <div style={{ color: "#94a3b8", fontSize: "13px" }}>{alert.event_type}</div>
                  </div>
                ))
              )}
            </div>
          </div>
          
        </div>
      </div>
    </>
  );
}

function Card({ title, value, glowColor }) {
  return (
    <div className="glass-panel" style={{
      padding: "20px",
      display: "flex",
      flexDirection: "column",
      justifyContent: "space-between",
      borderTop: `2px solid ${glowColor}`
    }}>
      <h3 style={{ margin: 0, color: "#94a3b8", fontSize: "13px", fontWeight: "600", textTransform: "uppercase", letterSpacing: "1px" }}>
        {title}
      </h3>
      <h2 style={{ margin: "10px 0 0 0", fontSize: "36px", color: "#ffffff", fontWeight: "800", textShadow: `0 0 15px ${glowColor}80` }}>
        {value}
      </h2>
    </div>
  );
}

export default App;