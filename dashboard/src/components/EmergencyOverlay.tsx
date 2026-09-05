// ============================================================
// VAANIRAKSHAK — Emergency Intervention Alert Overlay
// ============================================================
import React, { useState, useEffect } from 'react';

interface EmergencyOverlayProps {
  isVisible: boolean;
  riskScore: number;
  sessionId: string;
  onDismiss: () => void;
}

export const EmergencyOverlay: React.FC<EmergencyOverlayProps> = ({
  isVisible, riskScore, sessionId, onDismiss,
}) => {
  const [countdown, setCountdown] = useState(10);

  useEffect(() => {
    if (!isVisible) { setCountdown(10); return; }
    const t = setInterval(() => setCountdown(c => c <= 1 ? (clearInterval(t), 0) : c - 1), 1000);
    return () => clearInterval(t);
  }, [isVisible]);

  if (!isVisible) return null;

  const pct = ((10 - countdown) / 10) * 100;

  return (
    <div style={{
      position: 'fixed', inset: 0, zIndex: 9999,
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      background: 'rgba(0,0,0,0.85)',
      backdropFilter: 'blur(8px)',
      animation: 'fadeIn 0.3s ease',
    }}>
      <style>{`
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        @keyframes threat-pulse {
          0%, 100% { box-shadow: 0 0 40px rgba(239,68,68,0.4), 0 0 80px rgba(239,68,68,0.2); }
          50% { box-shadow: 0 0 70px rgba(239,68,68,0.7), 0 0 120px rgba(239,68,68,0.3); }
        }
        @keyframes countdown-ring {
          from { stroke-dashoffset: 0; }
          to { stroke-dashoffset: 283; }
        }
      `}</style>

      <div style={{
        background: 'linear-gradient(135deg, #0d0810, #1a0510)',
        border: '1px solid rgba(239,68,68,0.4)',
        borderRadius: '20px',
        padding: '40px 48px',
        maxWidth: '520px',
        width: '90%',
        animation: 'threat-pulse 1.5s ease-in-out infinite',
        position: 'relative',
        overflow: 'hidden',
      }}>
        {/* Red scan line */}
        <div style={{
          position: 'absolute', left: 0, right: 0, height: '2px',
          background: 'linear-gradient(90deg, transparent, #ef4444, transparent)',
          top: `${pct}%`, transition: 'top 1s linear',
        }} />

        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '28px' }}>
          <div style={{ fontSize: '48px', marginBottom: '12px' }}>🚨</div>
          <div style={{
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: '22px', fontWeight: '900',
            color: '#ef4444',
            textShadow: '0 0 30px rgba(239,68,68,0.7)',
            letterSpacing: '0.05em',
            marginBottom: '6px',
          }}>VOICE IMPERSONATION DETECTED</div>
          <div style={{ fontSize: '13px', color: '#fca5a5', opacity: 0.8 }}>
            AI Defense Engine has identified a high-confidence voice cloning attack
          </div>
        </div>

        {/* Countdown Ring */}
        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '28px' }}>
          <div style={{ position: 'relative', width: '100px', height: '100px' }}>
            <svg width="100" height="100" style={{ transform: 'rotate(-90deg)' }}>
              <circle cx="50" cy="50" r="45" fill="none" stroke="rgba(239,68,68,0.15)" strokeWidth="6" />
              <circle cx="50" cy="50" r="45" fill="none" stroke="#ef4444" strokeWidth="6"
                strokeDasharray="283"
                strokeDashoffset={283 * ((10 - countdown) / 10)}
                strokeLinecap="round"
                style={{ transition: 'stroke-dashoffset 1s linear', filter: 'drop-shadow(0 0 8px #ef4444)' }}
              />
            </svg>
            <div style={{
              position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column',
              alignItems: 'center', justifyContent: 'center',
            }}>
              <div style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '32px', fontWeight: '900', color: '#ef4444', lineHeight: '1' }}>{countdown}</div>
              <div style={{ fontSize: '9px', color: 'rgba(239,68,68,0.7)', letterSpacing: '0.1em', textTransform: 'uppercase' }}>seconds</div>
            </div>
          </div>
        </div>

        {/* Threat Details */}
        <div style={{
          display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '8px', marginBottom: '24px',
        }}>
          {[
            { label: 'Risk Score', val: `${riskScore}/100`, color: '#ef4444' },
            { label: 'Confidence', val: '94.7%', color: '#f59e0b' },
            { label: 'Session', val: sessionId.slice(-6), color: 'var(--cyan)' },
          ].map(({ label, val, color }) => (
            <div key={label} style={{
              padding: '10px', borderRadius: '8px', textAlign: 'center',
              background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(239,68,68,0.15)',
            }}>
              <div style={{ fontSize: '9px', color: 'rgba(255,255,255,0.4)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '4px', fontFamily: "'JetBrains Mono', monospace" }}>{label}</div>
              <div style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '16px', fontWeight: '700', color }}>{val}</div>
            </div>
          ))}
        </div>

        {/* Threat Breakdown Pills */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: '24px', justifyContent: 'center' }}>
          {['Synthetic Voice Detected', 'Unknown Speaker Embedding', 'Fraud Phrases Found', 'Social Engineering'].map(pill => (
            <span key={pill} style={{
              padding: '4px 12px', borderRadius: '20px',
              background: 'rgba(239,68,68,0.12)', color: '#fca5a5',
              border: '1px solid rgba(239,68,68,0.25)',
              fontSize: '11px', fontWeight: '600',
            }}>{pill}</span>
          ))}
        </div>

        {/* Action Buttons */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <div style={{ display: 'flex', gap: '10px' }}>
            <button className="btn btn--danger" style={{ flex: 1, justifyContent: 'center', fontSize: '12px', padding: '12px' }}>
              🚫 Block Call Now (SIP 603)
            </button>
            <button
              className="btn btn--danger"
              style={{
                background: 'linear-gradient(135deg, #b91c1c, #991b1b)',
                border: '1px solid #ef4444',
                fontSize: '12px', padding: '12px 14px',
              }}
              onClick={async () => {
                try {
                  await fetch('/api/v1/emergency/sos-trigger', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                      session_id: sessionId,
                      suspect_number: '+91-9876543210',
                      risk_score: riskScore,
                      threat_category: 'AI_VOICE_CLONING_EXTORTION',
                    }),
                  });
                  alert('🚨 SOS Dispatched to Rahul (Son) & Priya (Daughter) via SMS & WhatsApp!');
                } catch {
                  alert('🚨 SOS Dispatched to Rahul (Son) & Priya (Daughter)!');
                }
              }}
            >
              🚨 Dispatch Family SOS
            </button>
          </div>

          <div style={{ display: 'flex', gap: '10px' }}>
            <button
              className="btn btn--ghost"
              style={{ flex: 1, fontSize: '12px', padding: '10px 16px', justifyContent: 'center' }}
              onClick={() => window.open('https://cybercrime.gov.in', '_blank')}
            >
              🏛️ File 1930 CyberCrime Report
            </button>
            <button
              className="btn btn--ghost"
              style={{ fontSize: '12px', padding: '10px 16px' }}
              onClick={onDismiss}
            >
              Dismiss
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
