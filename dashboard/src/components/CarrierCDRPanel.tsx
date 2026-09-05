// ============================================================
// VAANIRAKSHAK — Carrier CDR & Telecom Infrastructure Panel
// Phase 14: Cell Tower Triangulation · SIP 603 Teardown Telemetry
// ============================================================
import React, { useState, useEffect } from 'react';

interface TowerLocation {
  region_name: string;
  latitude: number;
  longitude: number;
  tower_vendor: string;
  signal_strength_dbm: number;
  is_known_fraud_corridor: boolean;
  hotspot_ref: string | null;
}

interface NetworkTelemetry {
  packet_loss_pct: number;
  jitter_ms: number;
  round_trip_time_ms: number;
  sip_session_alive: boolean;
}

interface CDRData {
  call_id: string;
  carrier_name: string;
  calling_party: string;
  called_party: string;
  codec: string;
  cell_tower_cgi: string;
  tower_location: TowerLocation;
  network_telemetry: NetworkTelemetry;
  fraud_hotspot_active: boolean;
  sip_circuit_state: string;
  sip_teardown_dispatched: boolean;
}

interface FraudHotspot {
  hotspot_id: string;
  region_name: string;
  latitude: number;
  longitude: number;
  risk_index: number;
  primary_modus_operandi: string;
  active_sim_farms: number;
  status: string;
}

interface CarrierCDRPanelProps {
  sessionId: string;
  isActive: boolean;
}

// SVG Radar pulse indicator
const TowerRadar: React.FC<{ isFraud: boolean }> = ({ isFraud }) => {
  const color = isFraud ? '#ef4444' : '#06b6d4';
  const glow = isFraud ? 'rgba(239,68,68,0.3)' : 'rgba(6,182,212,0.3)';

  return (
    <svg width="80" height="80" viewBox="0 0 80 80" style={{ flexShrink: 0 }}>
      {/* Outer ring */}
      <circle cx="40" cy="40" r="36" fill="none" stroke={color} strokeOpacity="0.15" strokeWidth="1" />
      <circle cx="40" cy="40" r="27" fill="none" stroke={color} strokeOpacity="0.2" strokeWidth="1" />
      <circle cx="40" cy="40" r="18" fill="none" stroke={color} strokeOpacity="0.3" strokeWidth="1" />
      {/* Cross-hairs */}
      <line x1="4" y1="40" x2="76" y2="40" stroke={color} strokeOpacity="0.2" strokeWidth="0.8" />
      <line x1="40" y1="4" x2="40" y2="76" stroke={color} strokeOpacity="0.2" strokeWidth="0.8" />
      {/* Sweep line with animation */}
      <line x1="40" y1="40" x2="76" y2="40" stroke={color} strokeWidth="1.5" strokeOpacity="0.7">
        <animateTransform attributeName="transform" type="rotate" from="0 40 40" to="360 40 40" dur="3s" repeatCount="indefinite" />
      </line>
      {/* Center dot */}
      <circle cx="40" cy="40" r="4" fill={color} style={{ filter: `drop-shadow(0 0 6px ${glow})` }} />
      {/* Blip */}
      {isFraud && (
        <circle cx="58" cy="26" r="3.5" fill="#ef4444">
          <animate attributeName="opacity" values="1;0.2;1" dur="1.2s" repeatCount="indefinite" />
          <animate attributeName="r" values="3.5;6;3.5" dur="1.2s" repeatCount="indefinite" />
        </circle>
      )}
    </svg>
  );
};

// SIP state badge
const SipStateBadge: React.FC<{ state: string }> = ({ state }) => {
  const configs: Record<string, { color: string; bg: string; label: string }> = {
    ESTABLISHED: { color: '#10b981', bg: 'rgba(16,185,129,0.12)', label: '🟢 ESTABLISHED' },
    TEARDOWN_DISPATCHED: { color: '#f59e0b', bg: 'rgba(245,158,11,0.12)', label: '⚡ TEARDOWN DISPATCHED' },
    TERMINATED_SIP_603: { color: '#ef4444', bg: 'rgba(239,68,68,0.12)', label: '🔴 TERMINATED · SIP 603' },
  };
  const cfg = configs[state] || { color: '#64748b', bg: 'rgba(100,116,139,0.1)', label: state };
  return (
    <span style={{
      padding: '3px 10px', borderRadius: '12px', fontSize: '10px', fontWeight: 800,
      fontFamily: "'JetBrains Mono', monospace", letterSpacing: '0.06em',
      background: cfg.bg, color: cfg.color, border: `1px solid ${cfg.color}40`,
    }}>
      {cfg.label}
    </span>
  );
};

export const CarrierCDRPanel: React.FC<CarrierCDRPanelProps> = ({ sessionId, isActive }) => {
  const [cdr, setCdr] = useState<CDRData | null>(null);
  const [hotspots, setHotspots] = useState<FraudHotspot[]>([]);
  const [activeHotspot, setActiveHotspot] = useState<number>(0);
  const [loading, setLoading] = useState(false);

  // Fetch CDR data from backend (with mock fallback)
  const fetchCDR = async () => {
    try {
      const res = await fetch(`http://localhost:8000/api/v1/carrier/cdr/${sessionId}`);
      if (res.ok) {
        const data = await res.json();
        setCdr(data);
        return;
      }
    } catch { /* fallback below */ }

    // Simulation fallback — always shows rich Jamtara scenario
    setCdr({
      call_id: sessionId,
      carrier_name: 'Bharat Telecom Carrier Gateway',
      calling_party: '+91-9876543210',
      called_party: '+91-9811122334',
      codec: 'AMR-WB/23850',
      cell_tower_cgi: '404-45-8192-3021',
      tower_location: {
        region_name: 'Jamtara Cyber Belt, Jharkhand',
        latitude: 23.9629,
        longitude: 86.8016,
        tower_vendor: 'Ericsson RBS 6000',
        signal_strength_dbm: -78,
        is_known_fraud_corridor: true,
        hotspot_ref: 'HOTSPOT-JAMTARA-01',
      },
      network_telemetry: {
        packet_loss_pct: 2.1,
        jitter_ms: 6.4,
        round_trip_time_ms: 38,
        sip_session_alive: true,
      },
      fraud_hotspot_active: true,
      sip_circuit_state: 'TEARDOWN_DISPATCHED',
      sip_teardown_dispatched: true,
    });
  };

  const fetchHotspots = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/v1/carrier/fraud-hotspots');
      if (res.ok) {
        setHotspots(await res.json());
        return;
      }
    } catch { /* fallback below */ }

    setHotspots([
      { hotspot_id: 'HOTSPOT-JAMTARA-01', region_name: 'Jamtara Cyber Belt (Jharkhand)', latitude: 23.9629, longitude: 86.8016, risk_index: 96, primary_modus_operandi: 'OTP Harvesting, SIM Swap', active_sim_farms: 142, status: 'CRITICAL_MONITORING' },
      { hotspot_id: 'HOTSPOT-MEWAT-02', region_name: 'Nuh / Mewat Tri-State Grid (Haryana)', latitude: 28.1091, longitude: 77.0094, risk_index: 92, primary_modus_operandi: 'CBI / Police Digital Arrest Impersonation', active_sim_farms: 118, status: 'HIGH_ALERT' },
      { hotspot_id: 'HOTSPOT-ALWAR-03', region_name: 'Alwar Regional Cluster (Rajasthan)', latitude: 27.5645, longitude: 76.6111, risk_index: 88, primary_modus_operandi: 'Fake Vehicle Sale & Military Impersonation', active_sim_farms: 76, status: 'ELEVATED_WATCH' },
      { hotspot_id: 'HOTSPOT-NCR-04', region_name: 'Delhi NCR Northern Hub (Noida/Rohini)', latitude: 28.6139, longitude: 77.209, risk_index: 84, primary_modus_operandi: 'Bogus Telecom Tech Support & Credit Card KYC', active_sim_farms: 94, status: 'ACTIVE_INVESTIGATION' },
    ]);
  };

  useEffect(() => {
    if (isActive) {
      setLoading(true);
      Promise.all([fetchCDR(), fetchHotspots()]).finally(() => setLoading(false));
    }
  }, [sessionId, isActive]);

  // Carousel through hotspots
  useEffect(() => {
    if (hotspots.length === 0) return;
    const timer = setInterval(() => {
      setActiveHotspot(prev => (prev + 1) % hotspots.length);
    }, 4000);
    return () => clearInterval(timer);
  }, [hotspots.length]);

  const statusColor = (s: string) => {
    if (s === 'CRITICAL_MONITORING') return '#ef4444';
    if (s === 'HIGH_ALERT') return '#f97316';
    if (s === 'ELEVATED_WATCH') return '#f59e0b';
    return '#06b6d4';
  };

  const isFraud = cdr?.fraud_hotspot_active ?? false;
  const tower = cdr?.tower_location;
  const net = cdr?.network_telemetry;

  return (
    <div className="card" style={{ padding: '18px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
      {/* Header */}
      <div className="section-header" style={{ marginBottom: 0 }}>
        <div className="section-header__icon">📡</div>
        <div style={{ flex: 1 }}>
          <div className="section-header__title">Carrier CDR &amp; Telecom Telemetry</div>
          <div style={{ fontSize: '10px', color: 'var(--text-dim)', marginTop: '1px' }}>
            Cell Tower Triangulation · SIP Circuit Monitoring
          </div>
        </div>
        {loading && (
          <div style={{ fontSize: '10px', color: 'var(--cyan)', fontFamily: "'JetBrains Mono', monospace" }}>
            ⟳ syncing...
          </div>
        )}
        {!isActive && (
          <div style={{ fontSize: '10px', color: 'var(--text-dim)', fontFamily: "'JetBrains Mono', monospace" }}>
            ◼ STANDBY
          </div>
        )}
      </div>

      {!cdr && !isActive && (
        <div style={{ textAlign: 'center', padding: '20px', color: 'var(--text-dim)', fontSize: '12px' }}>
          Start a session to stream carrier telemetry data
        </div>
      )}

      {cdr && (
        <>
          {/* === Cell Tower Geolocation Block === */}
          <div style={{
            background: isFraud ? 'rgba(239,68,68,0.06)' : 'rgba(6,182,212,0.05)',
            border: `1px solid ${isFraud ? 'rgba(239,68,68,0.25)' : 'rgba(6,182,212,0.2)'}`,
            borderRadius: '10px',
            padding: '14px',
            display: 'flex',
            gap: '14px',
            alignItems: 'flex-start',
          }}>
            <TowerRadar isFraud={isFraud} />

            <div style={{ flex: 1 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px', flexWrap: 'wrap' }}>
                <span style={{
                  fontFamily: "'JetBrains Mono', monospace", fontSize: '12px', fontWeight: 800,
                  color: isFraud ? '#ef4444' : 'var(--cyan)',
                }}>
                  {isFraud ? '⚠ FRAUD CORRIDOR DETECTED' : '✓ SAFE CORRIDOR'}
                </span>
                {isFraud && (
                  <span style={{
                    padding: '1px 7px', borderRadius: '6px', fontSize: '9px', fontWeight: 700,
                    background: 'rgba(239,68,68,0.15)', color: '#ef4444',
                    border: '1px solid rgba(239,68,68,0.3)', fontFamily: "'JetBrains Mono', monospace",
                  }}>
                    HOTSPOT: {tower?.hotspot_ref}
                  </span>
                )}
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '4px 16px' }}>
                {[
                  { label: 'CGI', val: cdr.cell_tower_cgi },
                  { label: 'Region', val: tower?.region_name ?? '—' },
                  { label: 'Vendor', val: tower?.tower_vendor ?? '—' },
                  { label: 'Signal', val: tower ? `${tower.signal_strength_dbm} dBm` : '—' },
                  { label: 'Lat / Lon', val: tower ? `${tower.latitude.toFixed(4)}° N, ${tower.longitude.toFixed(4)}° E` : '—' },
                  { label: 'Caller', val: cdr.calling_party },
                ].map(({ label, val }) => (
                  <div key={label}>
                    <div style={{ fontSize: '9px', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.1em' }}>{label}</div>
                    <div style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '10px', color: 'var(--text-primary)', fontWeight: 600, marginTop: '1px' }}>{val}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* === Codec & Channel Telemetry === */}
          <div>
            <div style={{ fontSize: '10px', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.12em', marginBottom: '8px' }}>
              Codec &amp; Channel Diagnostics
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '8px' }}>
              {[
                { label: 'Codec', val: cdr.codec, color: 'var(--cyan)' },
                { label: 'Jitter', val: `${net?.jitter_ms ?? '—'} ms`, color: net && net.jitter_ms > 5 ? '#f59e0b' : '#10b981' },
                { label: 'Pkt Loss', val: `${net?.packet_loss_pct ?? '—'}%`, color: net && net.packet_loss_pct > 1.5 ? '#f97316' : '#10b981' },
                { label: 'RTT', val: `${net?.round_trip_time_ms ?? '—'} ms`, color: '#06b6d4' },
              ].map(({ label, val, color }) => (
                <div key={label} style={{
                  background: 'rgba(255,255,255,0.03)', borderRadius: '8px', padding: '8px 10px',
                  border: '1px solid rgba(255,255,255,0.05)',
                }}>
                  <div style={{ fontSize: '9px', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.1em' }}>{label}</div>
                  <div style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '12px', fontWeight: 800, color, marginTop: '2px' }}>{val}</div>
                </div>
              ))}
            </div>
          </div>

          {/* === SIP Circuit State === */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '10px' }}>
            <div>
              <div style={{ fontSize: '9px', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.12em', marginBottom: '4px' }}>
                SIP Circuit State
              </div>
              <SipStateBadge state={cdr.sip_circuit_state} />
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '9px', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '2px' }}>Carrier</div>
              <div style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '10px', color: 'var(--text-primary)' }}>{cdr.carrier_name}</div>
            </div>
          </div>
        </>
      )}

      {/* === Fraud Hotspot Carousel === */}
      {hotspots.length > 0 && (
        <div>
          <div style={{ fontSize: '10px', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.12em', marginBottom: '8px' }}>
            🔴 Known Fraud Cluster Database
          </div>
          <div style={{ position: 'relative', overflow: 'hidden' }}>
            {hotspots.map((hs, i) => (
              <div
                key={hs.hotspot_id}
                style={{
                  display: i === activeHotspot ? 'flex' : 'none',
                  gap: '12px',
                  alignItems: 'flex-start',
                  background: 'rgba(239,68,68,0.05)',
                  border: '1px solid rgba(239,68,68,0.15)',
                  borderRadius: '8px',
                  padding: '10px 12px',
                }}
              >
                <div style={{ minWidth: '36px' }}>
                  <div style={{
                    width: '36px', height: '36px', borderRadius: '8px',
                    background: `rgba(239,68,68,${0.08 + (hs.risk_index / 1000)})`,
                    border: `1px solid ${statusColor(hs.status)}40`,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontFamily: "'JetBrains Mono', monospace", fontSize: '13px', fontWeight: 900,
                    color: statusColor(hs.status),
                  }}>
                    {hs.risk_index}
                  </div>
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '2px' }}>
                    {hs.region_name}
                  </div>
                  <div style={{ fontSize: '9px', color: 'var(--text-dim)', marginBottom: '4px' }}>
                    {hs.primary_modus_operandi}
                  </div>
                  <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                    <span style={{
                      fontSize: '9px', fontFamily: "'JetBrains Mono', monospace",
                      color: statusColor(hs.status),
                      background: `${statusColor(hs.status)}15`,
                      padding: '2px 6px', borderRadius: '4px',
                      border: `1px solid ${statusColor(hs.status)}30`,
                    }}>
                      {hs.status.replace(/_/g, ' ')}
                    </span>
                    <span style={{ fontSize: '9px', color: 'var(--text-dim)', fontFamily: "'JetBrains Mono', monospace" }}>
                      {hs.active_sim_farms} SIM farms
                    </span>
                    <span style={{ fontSize: '9px', color: 'var(--text-dim)', fontFamily: "'JetBrains Mono', monospace" }}>
                      {hs.latitude.toFixed(2)}°N {hs.longitude.toFixed(2)}°E
                    </span>
                  </div>
                </div>
              </div>
            ))}

            {/* Dot pagination */}
            <div style={{ display: 'flex', justifyContent: 'center', gap: '5px', marginTop: '8px' }}>
              {hotspots.map((_, i) => (
                <button
                  key={i}
                  onClick={() => setActiveHotspot(i)}
                  style={{
                    width: i === activeHotspot ? '18px' : '6px',
                    height: '6px',
                    borderRadius: '3px',
                    background: i === activeHotspot ? '#ef4444' : 'rgba(239,68,68,0.25)',
                    border: 'none',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    padding: 0,
                  }}
                />
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
