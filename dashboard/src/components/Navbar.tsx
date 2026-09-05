// ============================================================
// VAANIRAKSHAK — Navbar / Command Center Header
// ============================================================
import React from 'react';

interface NavbarProps {
  isConnected: boolean;
  riskScore: number;
  status: string;
  onOpenSandbox?: () => void;
  engineMode?: 'live' | 'mock';
  onToggleEngineMode?: () => void;
  activeTab: 'live' | 'attack' | 'forensics';
  onTabChange: (tab: 'live' | 'attack' | 'forensics') => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  isConnected, riskScore, status, onOpenSandbox, engineMode = 'mock', onToggleEngineMode,
  activeTab, onTabChange,
}) => {
  const isAlert = riskScore >= 80;
  const isCritical = riskScore >= 90;

  return (
    <nav style={{
      position: 'sticky', top: 0, zIndex: 100,
      background: 'rgba(6, 11, 18, 0.95)',
      backdropFilter: 'blur(20px)',
      borderBottom: `1px solid ${isCritical ? 'rgba(239,68,68,0.4)' : isAlert ? 'rgba(245,158,11,0.3)' : 'rgba(26,45,74,0.8)'}`,
      padding: '0 24px',
      height: '64px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      transition: 'border-color 0.3s ease',
      boxShadow: isCritical ? '0 0 30px rgba(239,68,68,0.2)' : '0 4px 20px rgba(0,0,0,0.5)',
    }}>
      {/* Logo */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
        <div style={{
          width: '38px', height: '38px', borderRadius: '10px',
          background: 'linear-gradient(135deg, #06b6d4, #0284c7)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: '20px', boxShadow: '0 0 20px rgba(6,182,212,0.4)',
        }}>🛡️</div>
        <div>
          <div style={{
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: '16px', fontWeight: '700',
            background: 'linear-gradient(135deg, #f0f6ff, #06b6d4)',
            WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
            letterSpacing: '0.05em',
          }}>VAANI<span style={{ opacity: 0.7 }}>RAKSHAK</span></div>
          <div style={{ fontSize: '10px', color: 'var(--text-dim)', letterSpacing: '0.12em', textTransform: 'uppercase' }}>
            Live Security Command Center
          </div>
        </div>
      </div>

      {/* Main View Tabs (Clear separation of 3 primary modes) */}
      <div style={{
        display: 'flex', gap: '6px', background: 'rgba(0,0,0,0.4)',
        padding: '4px', borderRadius: '10px', border: '1px solid rgba(255,255,255,0.06)'
      }}>
        {[
          { id: 'live', label: '🛡️ Real-Time Call Protection', badge: isConnected ? 'LIVE' : null },
          { id: 'attack', label: '🧪 Attack Lab & Benchmarks' },
          { id: 'forensics', label: '📜 Forensics & Legal Exporter' },
        ].map(({ id, label, badge }) => {
          const isActive = activeTab === id;
          return (
            <button
              key={id}
              onClick={() => onTabChange(id as any)}
              style={{
                padding: '6px 14px', borderRadius: '7px', fontSize: '12px', fontWeight: '700',
                border: isActive ? '1px solid var(--cyan)' : '1px solid transparent',
                background: isActive ? 'rgba(6,182,212,0.15)' : 'transparent',
                color: isActive ? 'var(--cyan)' : 'var(--text-secondary)',
                cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '6px',
                transition: 'all 0.2s ease',
              }}
            >
              <span>{label}</span>
              {badge && (
                <span style={{
                  fontSize: '8px', padding: '1px 5px', borderRadius: '4px',
                  background: '#10b981', color: '#000', fontWeight: '800'
                }}>{badge}</span>
              )}
            </button>
          );
        })}
      </div>

      {/* Center Status & Sandbox Trigger */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
        {/* Engine Mode Toggle */}
        {onToggleEngineMode && (
          <button
            onClick={onToggleEngineMode}
            title="Toggle between Live Backend WebSocket and Simulation Mode"
            style={{
              padding: '5px 12px', borderRadius: '20px', fontSize: '11px', fontWeight: 800, cursor: 'pointer',
              border: engineMode === 'live' ? '1px solid #10b981' : '1px solid #64748b',
              background: engineMode === 'live' ? 'rgba(16,185,129,0.15)' : 'rgba(100,116,139,0.15)',
              color: engineMode === 'live' ? '#10b981' : '#94a3b8',
              display: 'flex', alignItems: 'center', gap: '5px',
            }}
          >
            <span>{engineMode === 'live' ? '⚡ LIVE WEBSOCKET' : '🧪 SIMULATION MODE'}</span>
          </button>
        )}

        <div style={{
          display: 'flex', alignItems: 'center', gap: '8px',
          padding: '6px 16px',
          background: isCritical ? 'rgba(239,68,68,0.12)' : isAlert ? 'rgba(245,158,11,0.1)' : 'rgba(16,185,129,0.08)',
          border: `1px solid ${isCritical ? 'rgba(239,68,68,0.3)' : isAlert ? 'rgba(245,158,11,0.25)' : 'rgba(16,185,129,0.2)'}`,
          borderRadius: '20px',
          transition: 'all 0.3s ease',
        }}>
          <span className="pulse-dot" style={{
            background: isCritical ? '#ef4444' : isAlert ? '#f59e0b' : '#10b981',
          }} />
          <span style={{
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: '12px', fontWeight: '700', letterSpacing: '0.08em',
            color: isCritical ? '#ef4444' : isAlert ? '#f59e0b' : '#10b981',
          }}>
            {isCritical ? '⚠ THREAT DETECTED' : isAlert ? '⚡ HIGH RISK' : status === 'ACTIVE' ? '● MONITORING ACTIVE' : '◎ STANDBY'}
          </span>
        </div>

        {/* Judge Sandbox Button */}
        {onOpenSandbox && (
          <button
            onClick={onOpenSandbox}
            style={{
              padding: '6px 14px', borderRadius: '20px', fontSize: '12px', fontWeight: 800,
              background: 'linear-gradient(135deg, rgba(0,240,255,0.15), rgba(99,102,241,0.2))',
              border: '1px solid #00f0ff80', color: '#00f0ff', cursor: 'pointer',
              display: 'flex', alignItems: 'center', gap: '6px',
              boxShadow: '0 0 15px rgba(0,240,255,0.2)',
            }}
          >
            <span>🎯</span> JURY SANDBOX
          </button>
        )}

        {/* SIH Badge */}
        <div className="badge badge--info">
          <span className="pulse-dot" />
          SIH 2026 · SIH26104
        </div>
      </div>

      {/* Right: System Stats */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '10px', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.1em' }}>Threat Engine</div>
          <div style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '12px', color: isConnected ? 'var(--green)' : 'var(--text-dim)' }}>
            {isConnected ? '▶ ONLINE' : '◼ OFFLINE'}
          </div>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '10px', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.1em' }}>Risk Score</div>
          <div style={{
            fontFamily: "'JetBrains Mono', monospace", fontSize: '22px', fontWeight: '800',
            color: isCritical ? '#ef4444' : isAlert ? '#f59e0b' : '#10b981',
            textShadow: isCritical ? '0 0 20px rgba(239,68,68,0.6)' : undefined,
          }}>
            {riskScore}<span style={{ fontSize: '13px', opacity: 0.6 }}>/100</span>
          </div>
        </div>
      </div>
    </nav>
  );
};
