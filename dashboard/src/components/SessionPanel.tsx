// ============================================================
// VAANIRAKSHAK — Session Status Panel (Left Sidebar)
// ============================================================
import React from 'react';
import type { SessionState, LiveFrame } from '../hooks/useVaaniWebSocket';

interface SessionPanelProps {
  session: SessionState;
  latestFrame?: LiveFrame;
  isConnected: boolean;
}

const RISK_LEVEL_CONFIG = {
  SAFE:     { color: '#10b981', bg: 'rgba(16,185,129,0.12)', label: '✓ SAFE',     bar: 10 },
  LOW:      { color: '#06b6d4', bg: 'rgba(6,182,212,0.12)',  label: '▲ LOW RISK', bar: 30 },
  MEDIUM:   { color: '#f97316', bg: 'rgba(249,115,22,0.12)', label: '⚡ MEDIUM',  bar: 60 },
  HIGH:     { color: '#f59e0b', bg: 'rgba(245,158,11,0.12)', label: '⚠ HIGH',    bar: 80 },
  CRITICAL: { color: '#ef4444', bg: 'rgba(239,68,68,0.12)',  label: '🚨 CRITICAL', bar: 95 },
};

export const SessionPanel: React.FC<SessionPanelProps> = ({ session, latestFrame, isConnected }) => {
  const risk = latestFrame?.riskScore ?? 0;
  const riskLevel = latestFrame?.riskLevel ?? 'SAFE';
  const cfg = RISK_LEVEL_CONFIG[riskLevel];

  const elapsedSec = Math.floor((Date.now() - session.startTime.getTime()) / 1000);
  const elapsedStr = session.status === 'IDLE' ? '—'
    : `${Math.floor(elapsedSec / 60).toString().padStart(2, '0')}:${(elapsedSec % 60).toString().padStart(2, '0')}`;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>

      {/* Main Threat Score Card */}
      <div className="card" style={{
        padding: '20px',
        background: `linear-gradient(135deg, ${cfg.bg}, var(--bg-card))`,
        border: `1px solid ${cfg.color}30`,
        boxShadow: `0 0 30px ${cfg.color}15`,
        transition: 'all 0.4s ease',
      }}>
        <div style={{
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          marginBottom: '16px',
        }}>
          <div style={{ fontSize: '11px', color: 'var(--text-dim)', fontFamily: "'JetBrains Mono', monospace", letterSpacing: '0.1em', textTransform: 'uppercase' }}>
            Threat Score
          </div>
          <span style={{
            fontSize: '11px', fontWeight: '700', padding: '3px 10px', borderRadius: '20px',
            background: `${cfg.color}20`, color: cfg.color,
            fontFamily: "'JetBrains Mono', monospace", letterSpacing: '0.06em',
            border: `1px solid ${cfg.color}40`,
          }}>{cfg.label}</span>
        </div>

        {/* Big Score Number */}
        <div style={{
          fontFamily: "'JetBrains Mono', monospace",
          fontSize: '72px', fontWeight: '900',
          lineHeight: '1',
          color: cfg.color,
          textShadow: `0 0 40px ${cfg.color}60`,
          transition: 'all 0.3s ease',
          textAlign: 'center',
          marginBottom: '8px',
        }}>
          {risk}
          <span style={{ fontSize: '22px', opacity: 0.5, fontWeight: '400' }}>/100</span>
        </div>

        {/* Progress Bar */}
        <div style={{
          height: '8px', borderRadius: '4px',
          background: 'rgba(255,255,255,0.06)',
          overflow: 'hidden', marginBottom: '12px',
        }}>
          <div style={{
            height: '100%', borderRadius: '4px',
            width: `${risk}%`,
            background: `linear-gradient(90deg, ${cfg.color}60, ${cfg.color})`,
            transition: 'width 0.5s ease, background 0.3s ease',
            boxShadow: `0 0 10px ${cfg.color}80`,
          }} />
        </div>

        {/* Threshold Markers */}
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '9px', color: 'var(--text-dim)', fontFamily: "'JetBrains Mono', monospace" }}>
          <span style={{ color: '#10b981' }}>0</span>
          <span style={{ color: '#06b6d4' }}>30</span>
          <span style={{ color: '#f97316' }}>60</span>
          <span style={{ color: '#f59e0b' }}>80</span>
          <span style={{ color: '#ef4444' }}>90+</span>
        </div>
      </div>

      {/* Session Info Card */}
      <div className="card" style={{ padding: '16px' }}>
        <div style={{ fontSize: '11px', color: 'var(--text-dim)', fontFamily: "'JetBrains Mono', monospace", letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: '12px' }}>
          Call Session
        </div>
        {[
          { label: 'Status', val: session.status, color: session.status === 'THREAT' ? '#ef4444' : session.status === 'ACTIVE' ? '#10b981' : 'var(--text-dim)' },
          { label: 'Caller', val: session.callerNumber, color: 'var(--text-primary)' },
          { label: 'Duration', val: elapsedStr, color: 'var(--cyan)' },
          { label: 'Frames', val: `${session.frames.length}`, color: 'var(--text-secondary)' },
          { label: 'Session', val: session.sessionId.slice(-8), color: 'var(--text-dim)' },
        ].map(({ label, val, color }) => (
          <div key={label} style={{
            display: 'flex', justifyContent: 'space-between', alignItems: 'center',
            padding: '6px 0', borderBottom: '1px solid rgba(26,45,74,0.4)',
          }}>
            <span style={{ fontSize: '11px', color: 'var(--text-dim)', fontFamily: "'JetBrains Mono', monospace" }}>{label}</span>
            <span style={{ fontSize: '12px', fontWeight: '600', color, fontFamily: "'JetBrains Mono', monospace" }}>{val}</span>
          </div>
        ))}
      </div>

      {/* Decision Engine Output */}
      <div className="card" style={{ padding: '16px' }}>
        <div style={{ fontSize: '11px', color: 'var(--text-dim)', fontFamily: "'JetBrains Mono', monospace", letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: '12px' }}>
          Decision Engine
        </div>
        <div style={{
          display: 'flex', alignItems: 'center', gap: '10px',
          padding: '12px', borderRadius: '8px',
          background: latestFrame?.action === 'BLOCK' ? 'rgba(239,68,68,0.1)'
            : latestFrame?.action === 'ALERT' ? 'rgba(245,158,11,0.1)'
            : latestFrame?.action === 'WARN' ? 'rgba(249,115,22,0.1)'
            : 'rgba(16,185,129,0.08)',
          border: `1px solid ${
            latestFrame?.action === 'BLOCK' ? 'rgba(239,68,68,0.25)'
            : latestFrame?.action === 'ALERT' ? 'rgba(245,158,11,0.2)'
            : latestFrame?.action === 'WARN' ? 'rgba(249,115,22,0.2)'
            : 'rgba(16,185,129,0.15)'}`,
          transition: 'all 0.3s ease',
        }}>
          <span style={{ fontSize: '22px' }}>
            {latestFrame?.action === 'BLOCK' ? '🚫' : latestFrame?.action === 'ALERT' ? '⚠️' : latestFrame?.action === 'WARN' ? '⚡' : '✅'}
          </span>
          <div>
            <div style={{
              fontFamily: "'JetBrains Mono', monospace", fontSize: '14px', fontWeight: '800',
              color: latestFrame?.action === 'BLOCK' ? '#ef4444' : latestFrame?.action === 'ALERT' ? '#f59e0b' : latestFrame?.action === 'WARN' ? '#f97316' : '#10b981',
            }}>
              {latestFrame?.action ?? 'MONITOR'}
            </div>
            <div style={{ fontSize: '10px', color: 'var(--text-dim)', marginTop: '2px' }}>
              {latestFrame?.action === 'BLOCK' ? '10s intervention countdown'
                : latestFrame?.action === 'ALERT' ? 'User alert dispatched'
                : latestFrame?.action === 'WARN' ? 'Elevated monitoring'
                : 'Normal monitoring active'}
            </div>
          </div>
        </div>

        {/* Policy Parameters */}
        <div style={{ marginTop: '10px', display: 'flex', flexDirection: 'column', gap: '5px' }}>
          {[
            { label: 'Intervention Window', val: '10 sec (Adaptive)' },
            { label: 'Critical Threshold', val: '≥ 85 (Block)' },
            { label: 'Biometric Vault', val: 'ECAPA-TDNN 192d' },
            { label: 'Carrier Integration', val: 'SIP 603 Webhook' },
          ].map(({ label, val }) => (
            <div key={label} style={{
              display: 'flex', justifyContent: 'space-between',
              fontSize: '10px', fontFamily: "'JetBrains Mono', monospace",
            }}>
              <span style={{ color: 'var(--text-dim)' }}>{label}</span>
              <span style={{ color: 'var(--cyan)' }}>{val}</span>
            </div>
          ))}
        </div>
      </div>

      {/* System Health */}
      <div className="card" style={{ padding: '16px' }}>
        <div style={{ fontSize: '11px', color: 'var(--text-dim)', fontFamily: "'JetBrains Mono', monospace", letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: '10px' }}>
          System Defense Status
        </div>
        {[
          { label: 'FastAPI WebSocket', online: isConnected },
          { label: 'Indic NLP (8 Languages)', online: true },
          { label: 'Biometric Profile Vault', online: true },
          { label: 'Forensic SHA-256 Sealer', online: true },
          { label: 'CyberCrime 1930 Gateway', online: true },
        ].map(({ label, online }) => (
          <div key={label} style={{
            display: 'flex', justifyContent: 'space-between', alignItems: 'center',
            marginBottom: '7px',
          }}>
            <span style={{ fontSize: '11px', color: 'var(--text-secondary)', fontFamily: "'JetBrains Mono', monospace" }}>{label}</span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '5px', fontSize: '10px', color: online ? '#10b981' : 'var(--text-dim)', fontFamily: "'JetBrains Mono', monospace", fontWeight: '600' }}>
              <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: online ? '#10b981' : 'var(--text-dim)', display: 'inline-block' }} />
              {online ? 'ONLINE' : 'OFFLINE'}
            </span>
          </div>
        ))}
      </div>

    </div>
  );
};
