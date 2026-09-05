// ============================================================
// VAANIRAKSHAK — Attack Lab Control Center (System A)
// ============================================================
import React, { useState } from 'react';

interface AttackConfig {
  generator: 'MockResearch' | 'BarkCoqui' | 'OpenVoice';
  scenario: 1 | 2 | 3;
  degradation: 'None' | 'PSTN' | 'VoIP' | 'Cellular';
  language: string;
}

interface AttackLabProps {
  onLaunchScenario: (scenario: number) => void;
  isRunning: boolean;
  currentScenario?: number;
}

const GENERATORS = [
  { id: 'MockResearch', label: 'Mock Research Adapter', desc: 'Fast deterministic mock (SIH demo)', color: '#06b6d4' },
  { id: 'BarkCoqui', label: 'Bark/Coqui TTS', desc: 'Open-source neural voice synthesis', color: '#8b5cf6' },
  { id: 'OpenVoice', label: 'OpenVoice V2', desc: 'Voice cloning via speaker reference', color: '#f59e0b' },
];

const SCENARIOS = [
  {
    id: 1, label: 'Scenario 1', title: 'Banking Fraud (Hindi)',
    desc: 'KYC/OTP scam impersonating SBI officer • Escalating threat trajectory',
    threat: 'CRITICAL', icon: '🏦',
  },
  {
    id: 2, label: 'Scenario 2', title: 'Credit Card Scam (English)',
    desc: 'HDFC impersonation requesting OTP verification • Spike detection',
    threat: 'HIGH', icon: '💳',
  },
  {
    id: 3, label: 'Scenario 3', title: 'Legitimate Call (Baseline)',
    desc: 'Car service appointment • Verifying false positive rate = 0',
    threat: 'SAFE', icon: '✅',
  },
];

const DEGRADATIONS = [
  { id: 'None', label: 'Clean Audio', color: '#10b981' },
  { id: 'PSTN', label: 'PSTN (8kHz)', color: '#06b6d4' },
  { id: 'VoIP', label: 'VoIP + Packet Loss', color: '#f59e0b' },
  { id: 'Cellular', label: 'Cellular (16kHz)', color: '#8b5cf6' },
];

export const AttackLabPanel: React.FC<AttackLabProps> = ({ onLaunchScenario, isRunning, currentScenario }) => {
  const [config, setConfig] = useState<AttackConfig>({
    generator: 'MockResearch',
    scenario: 1,
    degradation: 'PSTN',
    language: 'hi',
  });

  const selectedScenario = SCENARIOS.find(s => s.id === config.scenario);

  return (
    <div className="card attack-card" style={{ padding: '20px' }}>
      <div className="section-header">
        <div className="section-header__icon" style={{ background: 'rgba(239,68,68,0.1)', borderColor: 'rgba(239,68,68,0.2)' }}>⚗️</div>
        <div>
          <div className="section-header__title" style={{ color: 'var(--red)' }}>System A — Attack Lab</div>
          <div style={{ fontSize: '11px', color: 'var(--text-dim)', marginTop: '2px' }}>
            Controlled voice cloning generator · SIH Scenarios 1–3
          </div>
        </div>
        <div className="section-header__label">
          <span className="badge badge--alert">RESTRICTED</span>
        </div>
      </div>

      {/* Scenario Selector */}
      <div style={{ marginBottom: '16px' }}>
        <div style={{ fontSize: '11px', color: 'var(--text-dim)', marginBottom: '8px', fontFamily: "'JetBrains Mono', monospace", letterSpacing: '0.08em', textTransform: 'uppercase' }}>
          SIH Demo Scenario
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
          {SCENARIOS.map(sc => {
            const isSelected = config.scenario === sc.id;
            const scColor = sc.threat === 'CRITICAL' ? '#ef4444' : sc.threat === 'HIGH' ? '#f59e0b' : '#10b981';
            return (
              <button key={sc.id} onClick={() => setConfig(p => ({ ...p, scenario: sc.id as 1|2|3 }))}
                style={{
                  display: 'flex', alignItems: 'flex-start', gap: '12px',
                  padding: '10px 12px', borderRadius: '8px', border: 'none',
                  background: isSelected ? `rgba(${sc.threat === 'CRITICAL' ? '239,68,68' : sc.threat === 'HIGH' ? '245,158,11' : '16,185,129'},0.1)` : 'rgba(255,255,255,0.02)',
                  borderColor: isSelected ? scColor : 'transparent',
                  outline: isSelected ? `1px solid ${scColor}40` : '1px solid transparent',
                  cursor: 'pointer', textAlign: 'left', transition: 'all 0.15s ease',
                }}>
                <span style={{ fontSize: '20px', lineHeight: '1' }}>{sc.icon}</span>
                <div style={{ flex: 1 }}>
                  <div style={{
                    display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '2px',
                  }}>
                    <span style={{
                      fontSize: '12px', fontWeight: '700', color: isSelected ? scColor : 'var(--text-primary)',
                      fontFamily: "'JetBrains Mono', monospace",
                    }}>{sc.title}</span>
                    <span style={{
                      fontSize: '9px', fontWeight: '700', padding: '1px 6px', borderRadius: '4px',
                      background: `${scColor}20`, color: scColor,
                      fontFamily: "'JetBrains Mono', monospace", letterSpacing: '0.1em',
                    }}>{sc.threat}</span>
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--text-dim)', lineHeight: '1.4' }}>{sc.desc}</div>
                </div>
                {isSelected && (
                  <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: scColor, marginTop: '4px', flexShrink: 0 }} />
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* Generator Selector */}
      <div style={{ marginBottom: '14px' }}>
        <div style={{ fontSize: '11px', color: 'var(--text-dim)', marginBottom: '8px', fontFamily: "'JetBrains Mono', monospace", letterSpacing: '0.08em', textTransform: 'uppercase' }}>
          Voice Generator Adapter
        </div>
        <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
          {GENERATORS.map(g => {
            const isSel = config.generator === g.id;
            return (
              <button key={g.id}
                onClick={() => setConfig(p => ({ ...p, generator: g.id as AttackConfig['generator'] }))}
                title={g.desc}
                style={{
                  padding: '6px 12px', borderRadius: '6px', cursor: 'pointer',
                  background: isSel ? `${g.color}18` : 'transparent',
                  border: `1px solid ${isSel ? g.color + '50' : 'var(--bg-border)'}`,
                  color: isSel ? g.color : 'var(--text-secondary)',
                  fontSize: '11px', fontWeight: '600', fontFamily: "'JetBrains Mono', monospace",
                  transition: 'all 0.15s ease',
                }}>
                {g.id}
              </button>
            );
          })}
        </div>
      </div>

      {/* Degradation Selector */}
      <div style={{ marginBottom: '20px' }}>
        <div style={{ fontSize: '11px', color: 'var(--text-dim)', marginBottom: '8px', fontFamily: "'JetBrains Mono', monospace", letterSpacing: '0.08em', textTransform: 'uppercase' }}>
          Channel Degradation
        </div>
        <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
          {DEGRADATIONS.map(d => {
            const isSel = config.degradation === d.id;
            return (
              <button key={d.id}
                onClick={() => setConfig(p => ({ ...p, degradation: d.id as AttackConfig['degradation'] }))}
                style={{
                  padding: '5px 10px', borderRadius: '6px', cursor: 'pointer',
                  background: isSel ? `${d.color}15` : 'transparent',
                  border: `1px solid ${isSel ? d.color + '40' : 'var(--bg-border)'}`,
                  color: isSel ? d.color : 'var(--text-secondary)',
                  fontSize: '10px', fontWeight: '600', fontFamily: "'JetBrains Mono', monospace",
                  transition: 'all 0.15s ease',
                }}>
                {d.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Launch Button */}
      <button
        className={`btn ${config.scenario === 3 ? 'btn--primary' : 'btn--danger'}`}
        style={{ width: '100%', justifyContent: 'center', fontSize: '13px', padding: '12px' }}
        onClick={() => onLaunchScenario(config.scenario)}
        disabled={isRunning}
      >
        {isRunning ? (
          <>
            <span className="pulse-dot" style={{ background: currentScenario === 3 ? '#06b6d4' : '#ef4444' }} />
            Scenario {currentScenario} Running...
          </>
        ) : (
          <>⚡ Launch {selectedScenario?.title}</>
        )}
      </button>

      {/* Config Summary */}
      {!isRunning && (
        <div style={{
          marginTop: '12px', padding: '8px 12px', borderRadius: '6px',
          background: 'rgba(6,182,212,0.05)', border: '1px solid rgba(6,182,212,0.1)',
          fontFamily: "'JetBrains Mono', monospace", fontSize: '10px',
          color: 'var(--text-dim)', display: 'flex', flexWrap: 'wrap', gap: '8px',
        }}>
          <span>GEN: <span style={{ color: 'var(--cyan)' }}>{config.generator}</span></span>
          <span>CH: <span style={{ color: 'var(--cyan)' }}>{config.degradation}</span></span>
          <span>LANG: <span style={{ color: 'var(--cyan)' }}>HI/EN</span></span>
        </div>
      )}
    </div>
  );
};
