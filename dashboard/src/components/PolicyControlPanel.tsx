// ============================================================
// VAANIRAKSHAK — Live Policy Control Panel
// Phase 15: Real-time Defense Threshold Tuning for SIH Evaluators
// ============================================================
import React, { useState, useEffect } from 'react';

interface Policy {
  intervention_window_sec: number;
  critical_threshold: number;
  high_threshold: number;
  medium_threshold: number;
  low_threshold: number;
  auto_block_enabled: boolean;
  operational_tier: string;
  screening_unknown_numbers_only: boolean;
}

const DEFAULT_POLICY: Policy = {
  intervention_window_sec: 10,
  critical_threshold: 90,
  high_threshold: 80,
  medium_threshold: 60,
  low_threshold: 30,
  auto_block_enabled: true,
  operational_tier: 'TIER_2_RESEARCH_DEMO',
  screening_unknown_numbers_only: true,
};

const TIER_LABELS: Record<string, string> = {
  TIER_1_CONSUMER: '👤 Tier 1 — Consumer',
  TIER_2_RESEARCH_DEMO: '🔬 Tier 2 — Research Demo',
  TIER_3_CARRIER: '📡 Tier 3 — Carrier Grade',
};

type Toast = { msg: string; type: 'success' | 'error' } | null;

// A single labeled slider row
const SliderRow: React.FC<{
  label: string;
  value: number;
  min: number;
  max: number;
  color: string;
  unit?: string;
  onChange: (v: number) => void;
}> = ({ label, value, min, max, color, unit = '', onChange }) => (
  <div style={{ marginBottom: '10px' }}>
    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
      <span style={{ fontSize: '10px', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.1em' }}>
        {label}
      </span>
      <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '12px', fontWeight: 800, color }}>
        {value}{unit}
      </span>
    </div>
    <input
      type="range"
      min={min}
      max={max}
      value={value}
      onChange={e => onChange(Number(e.target.value))}
      style={{
        width: '100%',
        height: '4px',
        borderRadius: '2px',
        appearance: 'none',
        background: `linear-gradient(to right, ${color} ${((value - min) / (max - min)) * 100}%, rgba(255,255,255,0.08) ${((value - min) / (max - min)) * 100}%)`,
        cursor: 'pointer',
        outline: 'none',
      }}
    />
  </div>
);

export const PolicyControlPanel: React.FC = () => {
  const [policy, setPolicy] = useState<Policy>(DEFAULT_POLICY);
  const [toast, setToast] = useState<Toast>(null);
  const [loading, setLoading] = useState(false);

  // Fetch current policy from backend
  useEffect(() => {
    fetch('http://localhost:8000/api/v1/policy')
      .then(r => r.ok ? r.json() : null)
      .then(data => {
        if (data?.policy) setPolicy(data.policy);
      })
      .catch(() => { /* Use defaults */ });
  }, []);

  const showToast = (msg: string, type: 'success' | 'error') => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 3000);
  };

  const applyPolicy = async () => {
    // Validate ordering before sending
    if (!(policy.low_threshold < policy.medium_threshold &&
          policy.medium_threshold < policy.high_threshold &&
          policy.high_threshold < policy.critical_threshold)) {
      showToast('⚠ Thresholds must satisfy: LOW < MEDIUM < HIGH < CRITICAL', 'error');
      return;
    }
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/api/v1/policy/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(policy),
      });
      if (res.ok) {
        const data = await res.json();
        setPolicy(data.policy);
        showToast('✓ Policy applied — thresholds updated live', 'success');
      } else {
        const err = await res.json();
        showToast(`✗ ${err.detail || 'Update failed'}`, 'error');
      }
    } catch {
      // Offline mode — show success anyway for demo
      showToast('✓ Policy applied (offline simulation mode)', 'success');
    } finally {
      setLoading(false);
    }
  };

  const resetPolicy = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/api/v1/policy/reset', { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        setPolicy(data.policy);
        showToast('↺ Reset to SIH 2026 baseline defaults', 'success');
        return;
      }
    } catch { /* offline fallback */ }
    setPolicy(DEFAULT_POLICY);
    showToast('↺ Reset to SIH 2026 baseline defaults', 'success');
    setLoading(false);
  };

  const update = (key: keyof Policy, val: number | boolean | string) =>
    setPolicy(prev => ({ ...prev, [key]: val }));

  // Threshold zone bar
  const thresholdBar = [
    { label: 'LOW', from: policy.low_threshold, to: policy.medium_threshold, color: '#10b981' },
    { label: 'MED', from: policy.medium_threshold, to: policy.high_threshold, color: '#f59e0b' },
    { label: 'HIGH', from: policy.high_threshold, to: policy.critical_threshold, color: '#f97316' },
    { label: 'CRIT', from: policy.critical_threshold, to: 100, color: '#ef4444' },
  ];

  return (
    <div className="card" style={{ padding: '18px' }}>
      {/* Header */}
      <div className="section-header" style={{ marginBottom: '14px' }}>
        <div className="section-header__icon">⚙️</div>
        <div style={{ flex: 1 }}>
          <div className="section-header__title">Live Policy Control</div>
          <div style={{ fontSize: '10px', color: 'var(--text-dim)', marginTop: '1px' }}>
            Real-time Defense Threshold Tuning
          </div>
        </div>
        {/* Tier badge */}
        <span style={{
          fontSize: '9px', padding: '2px 8px', borderRadius: '8px',
          background: 'rgba(6,182,212,0.1)', color: 'var(--cyan)',
          border: '1px solid rgba(6,182,212,0.2)', fontFamily: "'JetBrains Mono', monospace",
          fontWeight: 700,
        }}>
          {policy.operational_tier.replace(/_/g, ' ')}
        </span>
      </div>

      {/* Threshold Zone Visualization */}
      <div style={{ marginBottom: '14px' }}>
        <div style={{ fontSize: '9px', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.12em', marginBottom: '5px' }}>
          Risk Zone Map
        </div>
        <div style={{ display: 'flex', height: '12px', borderRadius: '6px', overflow: 'hidden', gap: '1px' }}>
          {thresholdBar.map(({ label, from, to, color }) => (
            <div
              key={label}
              title={`${label}: ${from}–${to}`}
              style={{
                flex: to - from,
                background: `${color}30`,
                border: `1px solid ${color}50`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '7px',
                color,
                fontFamily: "'JetBrains Mono', monospace",
                fontWeight: 700,
                minWidth: '20px',
              }}
            >
              {label}
            </div>
          ))}
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '2px' }}>
          <span style={{ fontSize: '8px', color: 'var(--text-dim)', fontFamily: "'JetBrains Mono', monospace" }}>0</span>
          <span style={{ fontSize: '8px', color: 'var(--text-dim)', fontFamily: "'JetBrains Mono', monospace" }}>100</span>
        </div>
      </div>

      {/* Sliders */}
      <SliderRow label="🔴 Critical Threshold" value={policy.critical_threshold} min={70} max={98} color="#ef4444" onChange={v => update('critical_threshold', v)} />
      <SliderRow label="🟠 High Threshold" value={policy.high_threshold} min={50} max={policy.critical_threshold - 1} color="#f97316" onChange={v => update('high_threshold', v)} />
      <SliderRow label="🟡 Medium Threshold" value={policy.medium_threshold} min={20} max={policy.high_threshold - 1} color="#f59e0b" onChange={v => update('medium_threshold', v)} />
      <SliderRow label="🟢 Low Threshold" value={policy.low_threshold} min={5} max={policy.medium_threshold - 1} color="#10b981" onChange={v => update('low_threshold', v)} />
      <SliderRow label="⏱ Intervention Window" value={policy.intervention_window_sec} min={3} max={30} color="var(--cyan)" unit="s" onChange={v => update('intervention_window_sec', v)} />

      {/* Toggles */}
      <div style={{ display: 'flex', gap: '8px', marginTop: '12px', marginBottom: '12px' }}>
        {/* Auto-block toggle */}
        <button
          onClick={() => update('auto_block_enabled', !policy.auto_block_enabled)}
          style={{
            flex: 1, padding: '6px 10px', borderRadius: '8px', fontSize: '10px', fontWeight: 700, cursor: 'pointer',
            background: policy.auto_block_enabled ? 'rgba(239,68,68,0.12)' : 'rgba(100,116,139,0.1)',
            border: `1px solid ${policy.auto_block_enabled ? 'rgba(239,68,68,0.3)' : 'rgba(100,116,139,0.2)'}`,
            color: policy.auto_block_enabled ? '#ef4444' : '#94a3b8',
            display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '4px',
          }}
        >
          {policy.auto_block_enabled ? '🚫 AUTO-BLOCK ON' : '○ AUTO-BLOCK OFF'}
        </button>

        {/* Unknown numbers toggle */}
        <button
          onClick={() => update('screening_unknown_numbers_only', !policy.screening_unknown_numbers_only)}
          style={{
            flex: 1, padding: '6px 10px', borderRadius: '8px', fontSize: '10px', fontWeight: 700, cursor: 'pointer',
            background: policy.screening_unknown_numbers_only ? 'rgba(6,182,212,0.1)' : 'rgba(100,116,139,0.1)',
            border: `1px solid ${policy.screening_unknown_numbers_only ? 'rgba(6,182,212,0.25)' : 'rgba(100,116,139,0.2)'}`,
            color: policy.screening_unknown_numbers_only ? 'var(--cyan)' : '#94a3b8',
            display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '4px',
          }}
        >
          {policy.screening_unknown_numbers_only ? '🔍 UNKNOWN ONLY' : '🌐 SCREEN ALL'}
        </button>
      </div>

      {/* Tier Selector */}
      <div style={{ marginBottom: '14px' }}>
        <div style={{ fontSize: '9px', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.12em', marginBottom: '5px' }}>
          Operational Tier
        </div>
        <div style={{ display: 'flex', gap: '5px' }}>
          {Object.entries(TIER_LABELS).map(([tier, label]) => (
            <button
              key={tier}
              onClick={() => update('operational_tier', tier)}
              style={{
                flex: 1, padding: '5px 4px', borderRadius: '6px', fontSize: '9px', fontWeight: 700, cursor: 'pointer',
                background: policy.operational_tier === tier ? 'rgba(6,182,212,0.15)' : 'rgba(255,255,255,0.03)',
                border: `1px solid ${policy.operational_tier === tier ? 'rgba(6,182,212,0.4)' : 'rgba(255,255,255,0.06)'}`,
                color: policy.operational_tier === tier ? 'var(--cyan)' : 'var(--text-dim)',
                textAlign: 'center',
              }}
            >
              {label.split(' — ')[1] || label}
            </button>
          ))}
        </div>
      </div>

      {/* Action Buttons */}
      <div style={{ display: 'flex', gap: '8px' }}>
        <button
          onClick={applyPolicy}
          disabled={loading}
          style={{
            flex: 2, padding: '8px 16px', borderRadius: '8px', fontSize: '11px', fontWeight: 800, cursor: 'pointer',
            background: 'linear-gradient(135deg, rgba(6,182,212,0.2), rgba(2,132,199,0.3))',
            border: '1px solid rgba(6,182,212,0.4)', color: 'var(--cyan)',
            display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px',
            boxShadow: '0 0 15px rgba(6,182,212,0.1)',
          }}
        >
          {loading ? '⟳ Applying…' : '⚡ Apply Policy'}
        </button>
        <button
          onClick={resetPolicy}
          disabled={loading}
          style={{
            flex: 1, padding: '8px 12px', borderRadius: '8px', fontSize: '11px', fontWeight: 700, cursor: 'pointer',
            background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)', color: 'var(--text-dim)',
          }}
        >
          ↺ Reset
        </button>
      </div>

      {/* Toast notification */}
      {toast && (
        <div style={{
          marginTop: '10px', padding: '8px 12px', borderRadius: '8px', fontSize: '11px', fontWeight: 600,
          background: toast.type === 'success' ? 'rgba(16,185,129,0.12)' : 'rgba(239,68,68,0.12)',
          border: `1px solid ${toast.type === 'success' ? 'rgba(16,185,129,0.3)' : 'rgba(239,68,68,0.3)'}`,
          color: toast.type === 'success' ? '#10b981' : '#ef4444',
          textAlign: 'center',
          animation: 'fadeIn 0.2s ease',
        }}>
          {toast.msg}
        </div>
      )}
    </div>
  );
};
