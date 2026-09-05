// ============================================================
// VAANIRAKSHAK — Voice Authenticity Spectrogram Gauge Panel
// ============================================================
import React from 'react';
import { RadialBarChart, RadialBar, PolarAngleAxis } from 'recharts';
import type { LiveFrame } from '../hooks/useVaaniWebSocket';

interface AuthenticityPanelProps {
  frame?: LiveFrame;
}

const GaugeMeter: React.FC<{ value: number; label: string; color: string }> = ({ value, label, color }) => {
  const data = [{ name: label, value, fill: color }];
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px' }}>
      <div style={{ position: 'relative' }}>
        <RadialBarChart
          width={110} height={110}
          cx={55} cy={55}
          innerRadius={35} outerRadius={50}
          barSize={9} data={data}
          startAngle={210} endAngle={-30}
        >
          <PolarAngleAxis type="number" domain={[0, 100]} tick={false} />
          <RadialBar dataKey="value" cornerRadius={5} background={{ fill: 'rgba(26,45,74,0.5)' }} />
        </RadialBarChart>
        {/* Center text */}
        <div style={{
          position: 'absolute', inset: 0,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          flexDirection: 'column',
        }}>
          <div style={{
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: '18px', fontWeight: '800', color,
            textShadow: `0 0 12px ${color}80`,
          }}>{value}</div>
        </div>
      </div>
      <div style={{
        fontSize: '10px', color: 'var(--text-dim)', textTransform: 'uppercase',
        letterSpacing: '0.08em', textAlign: 'center', fontWeight: '600',
      }}>{label}</div>
    </div>
  );
};

// Animated waveform bars
const WaveformViz: React.FC<{ active: boolean; isFraud: boolean }> = ({ active, isFraud }) => {
  const bars = Array.from({ length: 32 });
  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: '3px',
      height: '56px', padding: '0 4px',
    }}>
      {bars.map((_, i) => {
        const heightPercent = active
          ? (Math.sin(i * 0.8) * 40 + 50)
          : 20;
        const delay = `${(i * 0.04).toFixed(2)}s`;
        const color = isFraud
          ? `hsl(${0 + i * 2}, 80%, 60%)`
          : `hsl(${180 + i * 2}, 70%, 55%)`;
        return (
          <div key={i} className="waveform-bar" style={{
            height: `${heightPercent}%`,
            background: color,
            animationDuration: active ? `${0.4 + (i % 5) * 0.1}s` : '2s',
            animationDelay: delay,
            opacity: active ? 0.85 : 0.25,
          }} />
        );
      })}
    </div>
  );
};

export const VoiceAuthenticityPanel: React.FC<AuthenticityPanelProps> = ({ frame }) => {
  const antispoof = frame?.antispoof ?? 0;
  const speakerAnomaly = frame?.speakerAnomaly ?? 0;
  const intent = frame?.intentScore ?? 0;
  const isFraud = frame?.isFraud ?? false;
  const isActive = !!frame;

  const antiColor = antispoof >= 80 ? '#ef4444' : antispoof >= 60 ? '#f59e0b' : '#10b981';
  const speakerColor = speakerAnomaly >= 80 ? '#ef4444' : speakerAnomaly >= 60 ? '#f59e0b' : '#10b981';
  const intentColor = intent >= 80 ? '#ef4444' : intent >= 60 ? '#f59e0b' : '#10b981';

  return (
    <div className="card" style={{ padding: '20px' }}>
      <div className="section-header">
        <div className="section-header__icon">🔊</div>
        <div>
          <div className="section-header__title">Voice Authenticity Engine</div>
          <div style={{ fontSize: '11px', color: 'var(--text-dim)', marginTop: '2px' }}>
            Anti-spoof · Speaker Verification · Intent NLP
          </div>
        </div>
        {isFraud && (
          <div className="section-header__label">
            <span className="badge badge--alert">⚠ CLONE DETECTED</span>
          </div>
        )}
      </div>

      {/* Waveform */}
      <div style={{
        background: 'var(--bg-deep)', borderRadius: '8px',
        border: `1px solid ${isFraud ? 'rgba(239,68,68,0.2)' : 'var(--bg-border)'}`,
        marginBottom: '16px', overflow: 'hidden', position: 'relative',
      }}>
        {isActive && <div className="scan-line" />}
        <WaveformViz active={isActive} isFraud={isFraud} />
        <div style={{
          display: 'flex', justifyContent: 'space-between',
          padding: '4px 12px 8px', fontSize: '10px', color: 'var(--text-dim)',
          fontFamily: "'JetBrains Mono', monospace",
        }}>
          <span>STT: {frame?.language?.toUpperCase() ?? '—'}</span>
          <span>{frame ? `Frame #${frame.frameIndex + 1}` : 'Awaiting...'}</span>
          <span style={{ color: isFraud ? '#ef4444' : '#10b981' }}>
            {isFraud ? '⚠ SYNTHETIC' : isActive ? '✓ NATURAL' : '—'}
          </span>
        </div>
      </div>

      {/* Gauge Trio */}
      <div style={{ display: 'flex', justifyContent: 'space-around' }}>
        <GaugeMeter value={antispoof} label="Anti-Spoof" color={antiColor} />
        <GaugeMeter value={speakerAnomaly} label="Speaker Δ" color={speakerColor} />
        <GaugeMeter value={intent} label="Intent Risk" color={intentColor} />
      </div>

      {/* Sub-model labels */}
      <div style={{
        marginTop: '12px', display: 'flex', flexDirection: 'column', gap: '6px',
      }}>
        {[
          { label: 'RawNet3 Anti-Spoof', val: antispoof, color: antiColor },
          { label: 'ECAPA-TDNN Speaker', val: speakerAnomaly, color: speakerColor },
          { label: 'XLM-RoBERTa NLP', val: intent, color: intentColor },
        ].map(({ label, val, color }) => (
          <div key={label} style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{
              fontSize: '11px', color: 'var(--text-dim)', fontFamily: "'JetBrains Mono', monospace",
              width: '160px', flexShrink: 0,
            }}>{label}</div>
            <div className="progress-bar" style={{ flex: 1 }}>
              <div className="progress-bar__fill" style={{
                width: `${val}%`,
                background: `linear-gradient(90deg, ${color}80, ${color})`,
              }} />
            </div>
            <div style={{
              fontSize: '11px', fontWeight: '700', color, fontFamily: "'JetBrains Mono', monospace",
              width: '28px', textAlign: 'right',
            }}>{val}</div>
          </div>
        ))}
      </div>
    </div>
  );
};
