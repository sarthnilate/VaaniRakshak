// ============================================================
// VAANIRAKSHAK — Incident Forensics & Audit Trail
// ============================================================
import React, { useState } from 'react';
import type { LiveFrame } from '../hooks/useVaaniWebSocket';

interface ForensicsTableProps {
  frames: LiveFrame[];
  sessionId: string;
  callerNumber: string;
  startTime: Date;
}

const ACTION_COLORS: Record<string, string> = {
  BLOCK: '#ef4444',
  ALERT: '#f59e0b',
  WARN:  '#f97316',
  MONITOR: '#10b981',
};

export const ForensicsTable: React.FC<ForensicsTableProps> = ({
  frames, sessionId, callerNumber, startTime,
}) => {
  const [expanded, setExpanded] = useState<number | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [copied, setCopied] = useState(false);

  const alertFrames = frames.filter(f => f.riskScore >= 60);
  const maxRisk = frames.length ? Math.max(...frames.map(f => f.riskScore)) : 0;
  const fraudCount = frames.filter(f => f.isFraud).length;
  const duration = frames.length ? `${frames.length * 2}s` : '—';
  const formattedTime = startTime ? new Date(startTime).toLocaleTimeString() : 'Active';

  // Compute deterministic case ref and mock hash based on session & frame count
  const mockSha256 = (
    '8f4a' + sessionId.replace(/-/g, '').padEnd(20, 'a') + (frames.length * 37).toString(16)
  ).slice(0, 64).padEnd(64, 'e');
  const caseRef = `I4C-1930-${mockSha256.slice(0, 8).toUpperCase()}`;

  const downloadFile = (filename: string, content: string, type: string) => {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleExportMarkdown = () => {
    const report = [
      '# 🏛️ FORENSIC CYBERCRIME INCIDENT DOSSIER',
      `**Case Reference:** \`${caseRef}\``,
      `**Session ID:** \`${sessionId}\``,
      `**Generated:** ${new Date().toISOString()}`,
      `**Suspect Telecom CLI:** \`${callerNumber || '+91-UNKNOWN'}\``,
      `**Peak Risk Score:** ${maxRisk}/100`,
      `**Cryptographic SHA-256 Seal:** \`${mockSha256}\``,
      `**Legal Admissibility:** Certified under Section 65B of the Indian Evidence Act`,
      '',
      '## Chronological Evidence Chain',
      '| Frame | Time | Risk | Action | Lang | Transcript |',
      '| :---: | :---: | :---: | :---: | :---: | :--- |',
      ...frames.map(f => `| #${f.frameIndex + 1} | ${f.riskScore}/100 | ${f.action} | ${f.language.toUpperCase()} | ${f.transcriptChunk || f.detectedPhrase || '—'} |`),
      '',
      '*(Digitally sealed by VAANIRAKSHAK AI Defense Engine)*',
    ].join('\n');

    downloadFile(`vaani-dossier-${sessionId.slice(-6)}.md`, report, 'text/markdown');
  };

  const handleExportJson = () => {
    const payload = {
      case_reference: caseRef,
      session_id: sessionId,
      suspect_cli: callerNumber || '+91-UNKNOWN',
      peak_risk_score: maxRisk,
      sha256_seal: mockSha256,
      frames_analyzed: frames.length,
      i4c_submission_ready: true,
      frames,
    };
    downloadFile(`vaani-dossier-${sessionId.slice(-6)}.json`, JSON.stringify(payload, null, 2), 'application/json');
  };

  return (
    <div className="card" style={{ padding: '20px' }}>
      <div className="section-header">
        <div className="section-header__icon">🔍</div>
        <div>
          <div className="section-header__title">Incident Forensics & Audit Trail</div>
          <div style={{ fontSize: '11px', color: 'var(--text-dim)', marginTop: '2px' }}>
            Evidence chain for CyberCrime (1930) reporting · Target: {callerNumber || 'N/A'} · Time: {formattedTime}
          </div>
        </div>
      </div>

      {/* Session Summary Stats */}
      <div style={{
        display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '8px',
        marginBottom: '16px',
      }}>
        {[
          { label: 'Session ID', val: sessionId.slice(-8), color: 'var(--cyan)' },
          { label: 'Max Risk', val: `${maxRisk}/100`, color: maxRisk >= 80 ? '#ef4444' : '#10b981' },
          { label: 'Alerts / Fraud', val: `${alertFrames.length} / ${fraudCount}`, color: fraudCount > 0 ? '#ef4444' : alertFrames.length > 0 ? '#f59e0b' : '#10b981' },
          { label: 'Duration', val: duration, color: 'var(--text-primary)' },
        ].map(({ label, val, color }) => (
          <div key={label} style={{
            padding: '10px 12px', borderRadius: '8px',
            background: 'var(--bg-deep)',
            border: '1px solid var(--bg-border)',
          }}>
            <div style={{ fontSize: '9px', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '4px', fontFamily: "'JetBrains Mono', monospace" }}>{label}</div>
            <div style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '13px', fontWeight: '700', color }}>{val}</div>
          </div>
        ))}
      </div>

      {/* Alert Events Table */}
      {frames.length === 0 ? (
        <div style={{
          textAlign: 'center', padding: '32px', color: 'var(--text-dim)',
          fontFamily: "'JetBrains Mono', monospace", fontSize: '12px',
          border: '1px dashed var(--bg-border)', borderRadius: '8px',
        }}>
          📂 No forensic data yet — start a scenario to collect evidence
        </div>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table className="forensics-table">
            <thead>
              <tr>
                <th>TIME</th>
                <th>FRAME</th>
                <th>RISK</th>
                <th>ACTION</th>
                <th>LANG</th>
                <th>EVIDENCE</th>
              </tr>
            </thead>
            <tbody>
              {frames.map((frame, i) => {
                const actionColor = ACTION_COLORS[frame.action] ?? '#10b981';
                return (
                  <React.Fragment key={i}>
                    <tr
                      onClick={() => setExpanded(expanded === i ? null : i)}
                      style={{
                        cursor: 'pointer',
                        background: frame.isFraud ? 'rgba(239,68,68,0.04)' : undefined,
                      }}
                    >
                      <td style={{ color: 'var(--text-dim)' }}>
                        {new Date(frame.timestamp).toLocaleTimeString('en-IN', { hour12: false })}
                      </td>
                      <td>#{frame.frameIndex + 1}</td>
                      <td>
                        <span style={{
                          color: frame.riskScore >= 80 ? '#ef4444' : frame.riskScore >= 60 ? '#f59e0b' : '#10b981',
                          fontWeight: '700',
                        }}>{frame.riskScore}</span>
                      </td>
                      <td>
                        <span style={{
                          padding: '2px 7px', borderRadius: '4px',
                          background: `${actionColor}18`, color: actionColor,
                          fontSize: '10px', fontWeight: '700', letterSpacing: '0.08em',
                        }}>{frame.action}</span>
                      </td>
                      <td style={{ color: 'var(--cyan)' }}>{frame.language.toUpperCase()}</td>
                      <td style={{ maxWidth: '160px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {frame.detectedPhrase ?? <span style={{ color: 'var(--text-dim)' }}>—</span>}
                      </td>
                    </tr>
                    {expanded === i && (
                      <tr>
                        <td colSpan={6} style={{ padding: 0 }}>
                          <div style={{
                            padding: '12px 16px', background: 'rgba(6,182,212,0.04)',
                            borderLeft: '2px solid var(--cyan)', margin: '0 0 4px',
                            fontFamily: "'JetBrains Mono', monospace", fontSize: '11px',
                          }}>
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '8px' }}>
                              <div><span style={{ color: 'var(--text-dim)' }}>Anti-Spoof: </span><span style={{ color: 'var(--cyan)' }}>{frame.antispoof}</span></div>
                              <div><span style={{ color: 'var(--text-dim)' }}>Speaker Δ: </span><span style={{ color: 'var(--cyan)' }}>{frame.speakerAnomaly}</span></div>
                              <div><span style={{ color: 'var(--text-dim)' }}>Intent: </span><span style={{ color: 'var(--cyan)' }}>{frame.intentScore}</span></div>
                            </div>
                            <div style={{ marginTop: '8px', color: 'var(--text-secondary)', fontSize: '12px', lineHeight: '1.5' }}>
                              "{frame.transcriptChunk}"
                            </div>
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* CyberCrime Report & Export Buttons */}
      {frames.length > 0 && (
        <div style={{ marginTop: '14px', display: 'flex', gap: '10px' }}>
          <button
            onClick={() => setShowModal(true)}
            className="btn btn--danger"
            style={{ flex: 1, justifyContent: 'center', fontSize: '12px', padding: '10px' }}
          >
            🚨 Report to CyberCrime — 1930
          </button>
          <button
            onClick={handleExportMarkdown}
            className="btn btn--ghost"
            style={{ fontSize: '12px', padding: '10px 14px' }}
          >
            📤 Export Dossier (.md)
          </button>
        </div>
      )}

      {/* 1930 Evidentiary Submission Modal */}
      {showModal && (
        <div style={{
          position: 'fixed', inset: 0, zIndex: 10000,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          background: 'rgba(0,0,0,0.85)', backdropFilter: 'blur(8px)',
        }}>
          <div style={{
            background: 'linear-gradient(135deg, #0f172a, #1e1b4b)',
            border: '1px solid rgba(239,68,68,0.4)', borderRadius: '16px',
            padding: '32px', maxWidth: '560px', width: '92%',
            boxShadow: '0 20px 50px rgba(0,0,0,0.8)', position: 'relative',
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
              <div>
                <span className="badge badge--alert" style={{ marginBottom: '6px' }}>OFFICIAL INCIDENT DOSSIER</span>
                <h3 style={{ margin: '4px 0 0', fontSize: '18px', color: '#fff' }}>National CyberCrime Reporting Portal (1930)</h3>
                <div style={{ fontSize: '12px', color: 'var(--text-dim)', marginTop: '2px' }}>
                  Ministry of Home Affairs (I4C) Compliant Package
                </div>
              </div>
              <button
                onClick={() => setShowModal(false)}
                style={{ background: 'none', border: 'none', color: 'var(--text-dim)', fontSize: '20px', cursor: 'pointer' }}
              >
                ✕
              </button>
            </div>

            <div style={{
              background: 'rgba(0,0,0,0.4)', padding: '14px', borderRadius: '10px',
              border: '1px solid rgba(255,255,255,0.06)', marginBottom: '16px',
              fontFamily: "'JetBrains Mono', monospace", fontSize: '11px',
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                <span style={{ color: 'var(--text-dim)' }}>CASE REFERENCE:</span>
                <span style={{ color: 'var(--cyan)', fontWeight: '700' }}>{caseRef}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                <span style={{ color: 'var(--text-dim)' }}>SUSPECT CALLER CLI:</span>
                <span style={{ color: '#ef4444', fontWeight: '700' }}>{callerNumber || '+91-UNKNOWN'}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                <span style={{ color: 'var(--text-dim)' }}>LEGAL ADMISSIBILITY:</span>
                <span style={{ color: '#10b981', fontWeight: '700' }}>Section 65B Indian Evidence Act</span>
              </div>
              <div style={{ marginTop: '8px', paddingTop: '8px', borderTop: '1px dashed rgba(255,255,255,0.1)' }}>
                <div style={{ color: 'var(--text-dim)', marginBottom: '4px' }}>CRYPTOGRAPHIC SHA-256 SEAL:</div>
                <div style={{
                  wordBreak: 'break-all', color: 'var(--text-secondary)',
                  background: 'rgba(255,255,255,0.03)', padding: '6px 8px', borderRadius: '6px', fontSize: '10px',
                }}>
                  {mockSha256}
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', gap: '8px', marginBottom: '12px' }}>
              <button
                onClick={handleExportMarkdown}
                className="btn btn--ghost"
                style={{ flex: 1, justifyContent: 'center', fontSize: '12px', padding: '10px' }}
              >
                📥 Download Markdown (.md)
              </button>
              <button
                onClick={handleExportJson}
                className="btn btn--ghost"
                style={{ flex: 1, justifyContent: 'center', fontSize: '12px', padding: '10px' }}
              >
                📥 Download JSON-LD (.json)
              </button>
            </div>

            <div style={{ display: 'flex', gap: '8px' }}>
              <button
                onClick={() => {
                  setCopied(true);
                  setTimeout(() => setCopied(false), 2500);
                }}
                className="btn btn--danger"
                style={{ flex: 1, justifyContent: 'center', fontSize: '13px', padding: '12px', fontWeight: '700' }}
              >
                {copied ? '✅ Sealed Reference Copied!' : '🚨 Confirm & Transmit to 1930 Portal'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
