// ============================================================
// VAANIRAKSHAK — Live Security Command Center
// Main Dashboard Assembly
// ============================================================
import { useState, useEffect } from 'react';
import './index.css';

import { useVaaniWebSocket } from './hooks/useVaaniWebSocket';
import { Navbar } from './components/Navbar';
import { SessionPanel } from './components/SessionPanel';
import { LiveRiskChart } from './components/LiveRiskChart';
import { VoiceAuthenticityPanel } from './components/VoiceAuthenticityPanel';
import { TranscriptStream } from './components/TranscriptStream';
import { AttackLabPanel } from './components/AttackLabPanel';
import { ForensicsTable } from './components/ForensicsTable';
import { EmergencyOverlay } from './components/EmergencyOverlay';
import { JudgeSandboxModal } from './components/JudgeSandboxModal';
import { CarrierCDRPanel } from './components/CarrierCDRPanel';
import { PolicyControlPanel } from './components/PolicyControlPanel';
import { SystemHealthPanel } from './components/SystemHealthPanel';

const SCENARIO_DESCRIPTIONS: Record<number, { title: string; icon: string; color: string }> = {
  1: { title: 'Banking Fraud (Hindi)', icon: '🏦', color: '#ef4444' },
  2: { title: 'Credit Card Scam (English)', icon: '💳', color: '#f59e0b' },
  3: { title: 'Legitimate Call (Baseline)', icon: '✅', color: '#10b981' },
};

function App() {
  const [activeScenario, setActiveScenario] = useState(1);
  const [showEmergency, setShowEmergency] = useState(false);
  const [emergencyDismissed, setEmergencyDismissed] = useState(false);
  const [showSandbox, setShowSandbox] = useState(false);

  const {
    sessionState,
    isConnected,
    latestFrame,
    engineMode,
    setEngineMode,
    startSession,
    stopSession,
  } = useVaaniWebSocket(activeScenario);

  const currentRisk = latestFrame?.riskScore ?? 0;
  const isCritical = currentRisk >= 90;

  // Trigger emergency overlay when risk goes critical
  useEffect(() => {
    if (isCritical && !emergencyDismissed && sessionState.status === 'THREAT') {
      setShowEmergency(true);
    }
  }, [isCritical, emergencyDismissed, sessionState.status]);

  // Reset dismiss flag when new session starts
  useEffect(() => {
    if (sessionState.status === 'ACTIVE') {
      setEmergencyDismissed(false);
      setShowEmergency(false);
    }
  }, [sessionState.sessionId]);

  const handleLaunch = (scenario: number) => {
    setActiveScenario(scenario);
    setEmergencyDismissed(false);
    setShowEmergency(false);
    startSession(scenario);
  };

  const handleDismissEmergency = () => {
    setShowEmergency(false);
    setEmergencyDismissed(true);
  };

  const scenarioInfo = SCENARIO_DESCRIPTIONS[activeScenario];

  return (
    <>
      {/* Background Grid & Orbs */}
      <div className="bg-grid" />
      <div className="bg-glow-orb bg-glow-orb--cyan" />
      <div className="bg-glow-orb bg-glow-orb--red" />

      {/* Emergency Overlay */}
      <EmergencyOverlay
        isVisible={showEmergency}
        riskScore={currentRisk}
        sessionId={sessionState.sessionId}
        onDismiss={handleDismissEmergency}
      />

      {/* Judge Evaluation Sandbox Modal */}
      <JudgeSandboxModal
        isOpen={showSandbox}
        onClose={() => setShowSandbox(false)}
      />

      {/* Sticky Navigation */}
      <Navbar
        isConnected={isConnected}
        riskScore={currentRisk}
        status={sessionState.status}
        onOpenSandbox={() => setShowSandbox(true)}
        engineMode={engineMode}
        onToggleEngineMode={() => setEngineMode(engineMode === 'live' ? 'mock' : 'live')}
      />

      {/* Main Content */}
      <div style={{ position: 'relative', zIndex: 1, padding: '20px 24px' }}>

        {/* Active Scenario Banner */}
        {sessionState.status !== 'IDLE' && (
          <div style={{
            display: 'flex', alignItems: 'center', gap: '12px',
            padding: '10px 16px', borderRadius: '10px', marginBottom: '16px',
            background: `linear-gradient(135deg, ${scenarioInfo.color}12, var(--bg-card))`,
            border: `1px solid ${scenarioInfo.color}30`,
          }}>
            <span style={{ fontSize: '22px' }}>{scenarioInfo.icon}</span>
            <div style={{ flex: 1 }}>
              <div style={{
                fontFamily: "'JetBrains Mono', monospace",
                fontSize: '13px', fontWeight: '700',
                color: scenarioInfo.color,
                letterSpacing: '0.04em',
              }}>
                SIH Demo — Scenario {activeScenario}: {scenarioInfo.title}
              </div>
              <div style={{ fontSize: '11px', color: 'var(--text-dim)', marginTop: '2px' }}>
                {sessionState.frames.length} frames processed · Session: {sessionState.sessionId.slice(-10)}
              </div>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span className={`badge badge--${
                sessionState.status === 'THREAT' ? 'alert'
                : sessionState.status === 'ACTIVE' ? 'live'
                : 'info'
              }`}>
                <span className="pulse-dot" />
                {sessionState.status}
              </span>
              {isConnected && (
                <button className="btn btn--ghost" style={{ fontSize: '11px', padding: '6px 12px' }}
                  onClick={stopSession}>
                  ◼ Stop
                </button>
              )}
            </div>
          </div>
        )}

        {/* 3-Column Dashboard Grid */}
        <div className="dashboard-grid">

          {/* ===== LEFT COLUMN: Session Status ===== */}
          <div>
            <SessionPanel
              session={sessionState}
              latestFrame={latestFrame}
              isConnected={isConnected}
            />
          </div>

          {/* ===== CENTER COLUMN: Main Analysis ===== */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>

            {/* Risk Trajectory Chart */}
            <LiveRiskChart
              trajectory={sessionState.riskTrajectory}
              isActive={isConnected}
            />

            {/* Voice Authenticity Panel */}
            <VoiceAuthenticityPanel frame={latestFrame} />

            {/* Transcript Stream */}
            <div style={{ flex: 1, minHeight: '300px' }}>
              <TranscriptStream
                frames={sessionState.frames}
                isActive={isConnected}
              />
            </div>

            {/* Forensics Table */}
            <ForensicsTable
              frames={sessionState.frames}
              sessionId={sessionState.sessionId}
              callerNumber={sessionState.callerNumber}
              startTime={sessionState.startTime}
            />
          </div>

          {/* ===== RIGHT COLUMN: Attack Lab + Carrier CDR ===== */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            <AttackLabPanel
              onLaunchScenario={handleLaunch}
              isRunning={isConnected}
              currentScenario={isConnected ? activeScenario : undefined}
            />

            {/* Carrier CDR & Telecom Infrastructure Panel */}
            <CarrierCDRPanel
              sessionId={sessionState.sessionId}
              isActive={isConnected || sessionState.status === 'ENDED'}
            />

            {/* Live Policy Control Panel */}
            <PolicyControlPanel />

            {/* System Performance & Diagnostic Panel */}
            <SystemHealthPanel />

            {/* Quick Stats Card */}
            <div className="card" style={{ padding: '16px' }}>
              <div className="section-header">
                <div className="section-header__icon">📊</div>
                <div className="section-header__title">Session Analytics</div>
              </div>
              {[
                { label: 'Total Frames', val: `${sessionState.frames.length}`, color: 'var(--cyan)' },
                { label: 'Fraud Frames', val: `${sessionState.frames.filter(f => f.isFraud).length}`, color: '#ef4444' },
                { label: 'Peak Risk', val: sessionState.frames.length ? `${Math.max(...sessionState.frames.map(f => f.riskScore))}` : '—', color: '#f59e0b' },
                { label: 'Avg Risk', val: sessionState.frames.length ? `${Math.round(sessionState.frames.reduce((acc, f) => acc + f.riskScore, 0) / sessionState.frames.length)}` : '—', color: 'var(--text-secondary)' },
                { label: 'Actions Triggered', val: `${sessionState.frames.filter(f => f.action !== 'MONITOR').length}`, color: '#f97316' },
              ].map(({ label, val, color }) => (
                <div key={label} style={{
                  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                  padding: '8px 0', borderBottom: '1px solid rgba(26,45,74,0.4)',
                }}>
                  <span style={{ fontSize: '11px', color: 'var(--text-dim)', fontFamily: "'JetBrains Mono', monospace" }}>{label}</span>
                  <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '13px', fontWeight: '700', color }}>{val}</span>
                </div>
              ))}
            </div>

            {/* Architecture Info Card */}
            <div className="card" style={{ padding: '16px' }}>
              <div className="section-header">
                <div className="section-header__icon">🧠</div>
                <div className="section-header__title">AI Pipeline</div>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {[
                  { label: 'Anti-Spoof', model: 'RawNet3', status: 'ACTIVE', color: '#10b981' },
                  { label: 'Speaker Verify', model: 'ECAPA-TDNN', status: 'ACTIVE', color: '#10b981' },
                  { label: 'STT Engine', model: 'Whisper-large', status: 'ACTIVE', color: '#10b981' },
                  { label: 'Intent NLP', model: 'XLM-RoBERTa', status: 'ACTIVE', color: '#10b981' },
                  { label: 'Temporal GRU', model: 'Custom GRU', status: 'ACTIVE', color: '#10b981' },
                  { label: 'Policy Engine', model: 'Rule-based', status: 'ACTIVE', color: '#06b6d4' },
                ].map(({ label, model, status, color }) => (
                  <div key={label} style={{
                    display: 'flex', alignItems: 'center', gap: '8px',
                    padding: '6px 8px', borderRadius: '6px',
                    background: 'rgba(255,255,255,0.02)',
                  }}>
                    <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: color, flexShrink: 0 }} />
                    <div style={{ flex: 1 }}>
                      <div style={{ fontSize: '11px', color: 'var(--text-primary)', fontFamily: "'JetBrains Mono', monospace", fontWeight: '600' }}>{label}</div>
                      <div style={{ fontSize: '9px', color: 'var(--text-dim)' }}>{model}</div>
                    </div>
                    <span style={{ fontSize: '9px', color, fontFamily: "'JetBrains Mono', monospace", fontWeight: '700' }}>{status}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Languages Supported */}
            <div className="card" style={{ padding: '16px' }}>
              <div className="section-header">
                <div className="section-header__icon">🌏</div>
                <div className="section-header__title">Language Coverage</div>
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '5px' }}>
                {['हिन्दी', 'English', 'বাংলা', 'தமிழ்', 'తెలుగు', 'मराठी', 'ਪੰਜਾਬੀ', 'ಕನ್ನಡ', 'ગુજરાતી', 'മലയാളം', 'ଓଡ଼ିଆ', 'অসমীয়া', 'اردو', 'Bodo', 'Meitei', 'Dogri'].map(lang => (
                  <span key={lang} style={{
                    padding: '3px 8px', borderRadius: '4px', fontSize: '10px',
                    background: 'rgba(6,182,212,0.08)', color: 'var(--cyan)',
                    border: '1px solid rgba(6,182,212,0.15)',
                    fontFamily: lang === 'English' || lang === 'Bodo' || lang === 'Meitei' || lang === 'Dogri' ? 'inherit' : 'serif',
                  }}>{lang}</span>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div style={{
          textAlign: 'center', padding: '24px', marginTop: '20px',
          borderTop: '1px solid var(--bg-border)',
          fontFamily: "'JetBrains Mono', monospace", fontSize: '11px', color: 'var(--text-dim)',
        }}>
          VAANIRAKSHAK · SIH 2026 Problem Statement SIH26104 ·
          AI-Powered Real-Time Voice Cloning Detection & Prevention ·
          <span style={{ color: 'var(--cyan)' }}> Privacy-First · On-Device AI · Zero Raw Audio Retention</span>
        </div>
      </div>
    </>
  );
}

export default App;
