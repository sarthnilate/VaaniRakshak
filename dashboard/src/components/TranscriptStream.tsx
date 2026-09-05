// ============================================================
// VAANIRAKSHAK — Live Multilingual Transcript Stream
// ============================================================
import React, { useEffect, useRef } from 'react';
import type { LiveFrame } from '../hooks/useVaaniWebSocket';

const LANG_LABELS: Record<string, string> = {
  hi: 'हिन्दी', en: 'English', ta: 'தமிழ்',
  bn: 'বাংলা', mr: 'मराठी', te: 'తెలుగు',
};

const FRAUD_KEYWORDS = [
  'OTP', 'खाता', 'account', 'suspended', 'blocked', 'आधार',
  'RBI', 'SBI', 'HDFC', 'verify', 'compliance', 'urgent', 'URGENT',
  'बंद', 'frozen', '₹', 'share', 'नंबर', 'password',
];

function highlightFraud(text: string): React.ReactNode[] {
  const parts: React.ReactNode[] = [];
  let lastIdx = 0;
  const upper = text.toUpperCase();

  FRAUD_KEYWORDS.forEach(kw => {
    const idx = upper.indexOf(kw.toUpperCase());
    if (idx !== -1) {
      parts.push(text.slice(lastIdx, idx));
      parts.push(
        <mark key={idx} style={{
          background: 'rgba(239,68,68,0.25)', color: '#fca5a5',
          borderRadius: '3px', padding: '0 3px',
          border: '1px solid rgba(239,68,68,0.3)',
        }}>
          {text.slice(idx, idx + kw.length)}
        </mark>
      );
      lastIdx = idx + kw.length;
    }
  });
  parts.push(text.slice(lastIdx));
  return parts;
}

interface TranscriptStreamProps {
  frames: LiveFrame[];
  isActive: boolean;
}

export const TranscriptStream: React.FC<TranscriptStreamProps> = ({ frames, isActive }) => {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [frames.length]);

  return (
    <div className="card" style={{ padding: '20px', height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div className="section-header">
        <div className="section-header__icon">🗣️</div>
        <div>
          <div className="section-header__title">Live Multilingual Transcript</div>
          <div style={{ fontSize: '11px', color: 'var(--text-dim)', marginTop: '2px' }}>
            Real-time STT · 16 Indian languages · Fraud highlighted
          </div>
        </div>
        {isActive && (
          <div className="section-header__label">
            <span className="badge badge--live">
              <span className="pulse-dot" />REC
            </span>
          </div>
        )}
      </div>

      <div style={{
        flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '6px',
        minHeight: '200px',
      }}>
        {frames.length === 0 ? (
          <div style={{
            display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
            height: '160px', gap: '10px', color: 'var(--text-dim)',
            fontFamily: "'JetBrains Mono', monospace", fontSize: '12px',
          }}>
            <span style={{ fontSize: '28px', opacity: 0.3 }}>💬</span>
            No call in session — Start a scenario below
          </div>
        ) : (
          frames.map((frame, i) => (
            <div key={i} className={`transcript-entry transcript-entry--${
              frame.isFraud ? 'fraud' : frame.riskScore >= 60 ? 'warn' : 'normal'
            }`}>
              <div style={{
                display: 'flex', alignItems: 'center', gap: '8px',
                marginBottom: '3px',
              }}>
                <span style={{
                  fontSize: '9px', color: 'var(--text-dim)', fontFamily: "'JetBrains Mono', monospace",
                  fontWeight: '600', letterSpacing: '0.1em',
                }}>
                  {new Date(frame.timestamp).toLocaleTimeString('en-IN', { hour12: false })}
                </span>
                <span style={{
                  fontSize: '9px', padding: '1px 6px', borderRadius: '4px',
                  background: frame.isFraud ? 'rgba(239,68,68,0.15)' : 'rgba(6,182,212,0.1)',
                  color: frame.isFraud ? '#fca5a5' : 'var(--cyan)',
                  fontFamily: "'JetBrains Mono', monospace", fontWeight: '700',
                }}>
                  {LANG_LABELS[frame.language] ?? frame.language.toUpperCase()}
                </span>
                <span style={{
                  fontSize: '9px', color: frame.isFraud ? '#ef4444' : 'var(--text-dim)',
                  fontFamily: "'JetBrains Mono', monospace", fontWeight: '600',
                }}>
                  RISK: {frame.riskScore}
                </span>
                {frame.isFraud && (
                  <span style={{
                    fontSize: '9px', fontWeight: '700', color: '#ef4444',
                    background: 'rgba(239,68,68,0.15)', padding: '1px 6px',
                    borderRadius: '4px', border: '1px solid rgba(239,68,68,0.3)',
                    fontFamily: "'JetBrains Mono', monospace",
                  }}>⚠ FRAUD PHRASE</span>
                )}
              </div>
              <div style={{ fontSize: '13px', lineHeight: '1.5' }}>
                {frame.isFraud ? highlightFraud(frame.transcriptChunk) : frame.transcriptChunk}
              </div>
              {frame.detectedPhrase && (
                <div style={{
                  marginTop: '4px', fontSize: '11px',
                  color: '#ef4444', fontFamily: "'JetBrains Mono', monospace",
                  display: 'flex', alignItems: 'center', gap: '4px',
                }}>
                  <span>🎯 Flagged:</span>
                  <span style={{
                    background: 'rgba(239,68,68,0.15)', padding: '1px 8px', borderRadius: '4px',
                    border: '1px solid rgba(239,68,68,0.25)',
                  }}>{frame.detectedPhrase}</span>
                </div>
              )}
            </div>
          ))
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  );
};
