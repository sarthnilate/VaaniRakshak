// ============================================================
// VAANIRAKSHAK — Enterprise Admin & SIEM Integration Panel
// Phase 17: Audit Logs, SIEM Syslog Feeds & CSV Batch Exporter
// ============================================================
import React, { useState, useEffect } from 'react';

interface AuditLog {
  id: string;
  timestamp: string;
  actor: string;
  action: string;
  details: string;
  severity: string;
}

export const AdminPanel: React.FC = () => {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [siemStatus, setSiemStatus] = useState<string>('IDLE');
  const [siemSample, setSiemSample] = useState<string>('');
  const [activeTab, setActiveTab] = useState<'audit' | 'siem' | 'batch'>('audit');

  useEffect(() => {
    fetch('http://localhost:8000/api/v1/admin/audit-logs')
      .then(res => res.json())
      .then(data => setLogs(data.logs || []))
      .catch(() => {
        setLogs([
          { id: 'AUD-1001', timestamp: '2026-09-05T11:00:15Z', actor: 'admin_sys', action: 'POLICY_UPDATE', details: 'Adjusted RISK_THRESHOLD_CRITICAL to 90', severity: 'INFO' },
          { id: 'AUD-1002', timestamp: '2026-09-05T11:05:42Z', actor: 'vaani_engine', action: 'CARRIER_TEARDOWN', details: 'Issued SIP 603 Decline for session SESS-BANKING-01', severity: 'CRITICAL' },
          { id: 'AUD-1003', timestamp: '2026-09-05T11:12:00Z', actor: 'vaani_engine', action: 'SOS_DISPATCH', details: 'Transmitted incident report to 1930 Cybercrime Portal', severity: 'WARNING' },
        ]);
      });
  }, []);

  const handleTestSiem = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/v1/admin/siem-export', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ format: 'CEF', destination_ip: '192.168.1.100', port: 514 }),
      });
      if (res.ok) {
        const data = await res.json();
        setSiemStatus(data.status);
        setSiemSample(data.sample_payload);
      }
    } catch {
      setSiemStatus('STREAMING_ACTIVE (Simulated)');
      setSiemSample('CEF:0|VaaniRakshak|AIThreatEngine|1.0|1001|Voice Cloning Scam Intercepted|9|src=198.51.100.42 spt=5060 dst=10.0.0.1 dpt=5060 act=SIP_603_TEARDOWN msg=Synthetic voice probability 0.94 on Hindi banking session');
    }
  };

  const handleDownloadCsv = () => {
    window.open('http://localhost:8000/api/v1/admin/batch-export?format=csv', '_blank');
  };

  return (
    <div className="card" style={{ padding: '16px' }}>
      <div className="section-header">
        <div className="section-header__icon">🛡️</div>
        <div className="section-header__title">Enterprise Security Admin & SIEM</div>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '6px', marginBottom: '12px', borderBottom: '1px solid rgba(255,255,255,0.06)', paddingBottom: '8px' }}>
        {[
          { key: 'audit', label: '📋 Audit Logs' },
          { key: 'siem', label: '📡 SIEM Syslog (CEF)' },
          { key: 'batch', label: '📊 CSV Batch Exporter' },
        ].map(({ key, label }) => (
          <button
            key={key}
            onClick={() => setActiveTab(key as any)}
            className="btn btn--ghost"
            style={{
              flex: 1, fontSize: '10px', padding: '6px 8px', justifyContent: 'center',
              borderColor: activeTab === key ? 'var(--cyan)' : 'transparent',
              background: activeTab === key ? 'rgba(6,182,212,0.1)' : 'transparent',
              color: activeTab === key ? 'var(--cyan)' : 'var(--text-dim)',
            }}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Audit Logs Tab */}
      {activeTab === 'audit' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
          {logs.map(l => (
            <div key={l.id} style={{
              background: 'rgba(0,0,0,0.3)', padding: '8px 10px', borderRadius: '6px',
              border: '1px solid rgba(255,255,255,0.04)', fontSize: '10px',
              fontFamily: "'JetBrains Mono', monospace",
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '3px' }}>
                <span style={{ color: 'var(--cyan)', fontWeight: '700' }}>[{l.id}] {l.action}</span>
                <span style={{
                  color: l.severity === 'CRITICAL' ? '#ef4444' : l.severity === 'WARNING' ? '#f59e0b' : '#10b981',
                  fontWeight: '700',
                }}>{l.severity}</span>
              </div>
              <div style={{ color: 'var(--text-secondary)' }}>{l.details}</div>
              <div style={{ fontSize: '9px', color: 'var(--text-dim)', marginTop: '4px' }}>
                Actor: {l.actor} · Timestamp: {new Date(l.timestamp).toLocaleTimeString()}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* SIEM Syslog Tab */}
      {activeTab === 'siem' && (
        <div>
          <div style={{ fontSize: '11px', color: 'var(--text-dim)', marginBottom: '8px' }}>
            Streams real-time threat events into Enterprise SIEM tools (Splunk, Elastic, QRadar) via Common Event Format (CEF).
          </div>
          <button
            onClick={handleTestSiem}
            className="btn btn--primary"
            style={{ width: '100%', justifyContent: 'center', fontSize: '11px', padding: '8px', marginBottom: '10px' }}
          >
            📡 Test SIEM Syslog Stream Connection
          </button>

          {siemStatus !== 'IDLE' && (
            <div style={{
              background: 'rgba(0,0,0,0.4)', padding: '10px', borderRadius: '6px',
              border: '1px solid rgba(6,182,212,0.3)', fontSize: '10px',
              fontFamily: "'JetBrains Mono', monospace",
            }}>
              <div style={{ color: '#10b981', fontWeight: '700', marginBottom: '4px' }}>STATUS: {siemStatus}</div>
              <div style={{ color: 'var(--text-dim)', fontSize: '9px', marginBottom: '4px' }}>SAMPLE CEF PAYLOAD:</div>
              <div style={{ wordBreak: 'break-all', color: 'var(--text-primary)', background: 'rgba(255,255,255,0.03)', padding: '6px', borderRadius: '4px' }}>
                {siemSample}
              </div>
            </div>
          )}
        </div>
      )}

      {/* CSV Batch Exporter Tab */}
      {activeTab === 'batch' && (
        <div style={{ textAlign: 'center', padding: '10px 0' }}>
          <div style={{ fontSize: '11px', color: 'var(--text-dim)', marginBottom: '12px' }}>
            Export comprehensive incident datasets formatted for offline legal compliance and law enforcement archives.
          </div>
          <button
            onClick={handleDownloadCsv}
            className="btn btn--ghost"
            style={{ width: '100%', justifyContent: 'center', fontSize: '11px', padding: '10px', color: '#10b981', borderColor: 'rgba(16,185,129,0.3)', background: 'rgba(16,185,129,0.08)' }}
          >
            📥 Download Historical Incidents (.CSV)
          </button>
        </div>
      )}
    </div>
  );
};
