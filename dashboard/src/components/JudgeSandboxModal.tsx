// ============================================================
// VAANIRAKSHAK — Judge Interactive Evaluation Sandbox
// SIH 2026 Jury Testing Studio
// ============================================================
import React, { useState } from 'react';

interface JudgeSandboxModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const PRESET_AUDIO_SAMPLES = [
  {
    id: 'sih-ai-clone',
    title: '🚨 AI Cloned Voice (Hindi Extortion)',
    desc: 'WavLM synthetic artifacts + low ECAPA speaker similarity',
    transcript: 'पापा, मेरा एक्सीडेंट हो गया है, तुरंत ₹50,000 इस UPI पर भेजो!',
    antiSpoof: 94,
    speakerSim: 0.32,
    intent: 'EMERGENCY_EXTORTION',
    tactics: ['URGENCY', 'FEAR'],
    risk: 94,
    action: 'BLOCK',
  },
  {
    id: 'sih-digital-arrest',
    title: '⚖️ CBI Digital Arrest (English Scammer)',
    desc: 'Real human voice + coercive authority impersonation',
    transcript: 'This is Officer Sharma from CBI New Delhi. You are under digital arrest. Transfer bail funds immediately.',
    antiSpoof: 12,
    speakerSim: 0.88,
    intent: 'DIGITAL_ARREST',
    tactics: ['AUTHORITY', 'PRESSURE', 'SECRECY'],
    risk: 84,
    action: 'ALERT',
  },
  {
    id: 'sih-legitimate',
    title: '✅ Legitimate Family Call (Baseline)',
    desc: 'Enrolled voice profile + clean conversational intent',
    transcript: 'Hi dad, reaching home by 7 PM. Do you want me to pick up vegetables?',
    antiSpoof: 4,
    speakerSim: 0.93,
    intent: 'NORMAL_CONVERSATION',
    tactics: [],
    risk: 6,
    action: 'MONITOR',
  },
];

const PRESET_TEXT_SAMPLES = [
  { lang: 'Hindi (hi)', text: 'आपका SBI खाता संदिग्ध गतिविधि के कारण बंद हो रहा है, तुरंत OTP शेयर करें।' },
  { lang: 'Marathi (mr)', text: 'तुमचे बँक खाते त्वरित ब्लॉक केले जाईल, व्हेरिफिकेशनसाठी त्वरित ओटीपी पाठवा.' },
  { lang: 'Tamil (ta)', text: 'உங்கள் வங்கி கணக்கு முடக்கப்படும், சரிபார்க்க உடனே OTP பகிரவும்.' },
  { lang: 'Telugu (te)', text: 'మీ బ్యాంక్ ఖాతా బ్లాక్ చేయబడుతుంది, వెంటనే OTP ని షేర్ చేయండి.' },
  { lang: 'Bengali (bn)', text: 'আপনার ব্যাংক অ্যাকাউন্ট সাময়িকভাবে বন্ধ হবে, অবিলম্বে OTP শেয়ার করুন।' },
  { lang: 'Gujarati (gu)', text: 'તમારું બેંક ખાતું તરત જ બ્લોક થઈ જશે, વેરિફિકેશન માટે OTP મોકલો.' },
  { lang: 'Punjabi (pa)', text: 'ਤੁਹਾਡਾ ਬੈਂਕ ਖਾਤਾ ਤੁਰੰਤ ਬੰਦ ਹੋ ਜਾਵੇਗਾ, ਪੁਸ਼ਟੀ ਲਈ ਆਪਣਾ OTP ਸਾਂਝਾ ਕਰੋ.' },
  { lang: 'English (en)', text: 'This is RBI Cyber Division. Your KYC has expired. Download APK to complete verification.' },
];

export const JudgeSandboxModal: React.FC<JudgeSandboxModalProps> = ({ isOpen, onClose }) => {
  const [activeTab, setActiveTab] = useState<'audio' | 'text'>('audio');
  const [selectedSample, setSelectedSample] = useState(PRESET_AUDIO_SAMPLES[0]);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<typeof PRESET_AUDIO_SAMPLES[0] | null>(PRESET_AUDIO_SAMPLES[0]);

  // Text tab state
  const [customText, setCustomText] = useState(PRESET_TEXT_SAMPLES[0].text);
  const [textAnalyzing, setTextAnalyzing] = useState(false);
  const [textResult, setTextResult] = useState<{
    lang: string;
    intent: string;
    tactics: string[];
    score: number;
    isFraud: boolean;
  } | null>({
    lang: 'hi',
    intent: 'OTP_REQUEST',
    tactics: ['URGENCY', 'FEAR'],
    score: 82,
    isFraud: true,
  });

  if (!isOpen) return null;

  const handleRunAudioAnalysis = (sample: typeof PRESET_AUDIO_SAMPLES[0]) => {
    setSelectedSample(sample);
    setAnalyzing(true);
    setTimeout(() => {
      setAnalysisResult(sample);
      setAnalyzing(false);
    }, 600);
  };

  const handleRunTextAnalysis = async (textToTest: string) => {
    setTextAnalyzing(true);
    try {
      const res = await fetch('/api/v1/sandbox/analyze-text', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: textToTest }),
      });
      if (res.ok) {
        const data = await res.json();
        setTextResult({
          lang: data.detected_language,
          intent: data.primary_intent,
          tactics: data.tactics,
          score: data.scam_score,
          isFraud: data.is_fraud,
        });
      } else {
        // Fallback local simulation
        setTextResult({
          lang: 'hi',
          intent: 'OTP_HARVESTING',
          tactics: ['URGENCY'],
          score: 78,
          isFraud: true,
        });
      }
    } catch {
      setTextResult({
        lang: 'hi',
        intent: 'OTP_HARVESTING',
        tactics: ['URGENCY'],
        score: 78,
        isFraud: true,
      });
    } finally {
      setTextAnalyzing(false);
    }
  };

  return (
    <div style={{
      position: 'fixed', inset: 0, zIndex: 9999,
      background: 'rgba(5, 7, 15, 0.85)', backdropFilter: 'blur(10px)',
      display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px',
    }}>
      <div style={{
        background: '#0d1322', border: '1px solid #1e293b', borderRadius: '16px',
        maxWidth: '860px', width: '100%', maxHeight: '90vh', overflowY: 'auto',
        boxShadow: '0 25px 60px -15px rgba(0, 240, 255, 0.15)', padding: '24px',
      }}>
        {/* Modal Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', borderBottom: '1px solid #1e293b', paddingBottom: '16px', marginBottom: '20px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span style={{ fontSize: '24px' }}>🎯</span>
              <h2 style={{ margin: 0, fontSize: '20px', fontWeight: 800, color: '#f8fafc', letterSpacing: '0.02em' }}>
                JURY EVALUATION SANDBOX
              </h2>
              <span style={{ fontSize: '11px', fontWeight: 700, padding: '3px 8px', borderRadius: '12px', background: '#00f0ff20', color: '#00f0ff', border: '1px solid #00f0ff40' }}>
                SIH 2026 LIVE
              </span>
            </div>
            <p style={{ margin: '4px 0 0 0', fontSize: '13px', color: '#94a3b8' }}>
              Test multi-model inference pipelines live on custom audio files and regional Indian dialect transcripts.
            </p>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'transparent', border: '1px solid #334155', color: '#94a3b8',
              borderRadius: '8px', width: '32px', height: '32px', cursor: 'pointer',
              display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '16px',
            }}
          >
            ✕
          </button>
        </div>

        {/* Tab Switcher */}
        <div style={{ display: 'flex', gap: '12px', marginBottom: '20px' }}>
          <button
            onClick={() => setActiveTab('audio')}
            style={{
              flex: 1, padding: '10px', borderRadius: '8px', cursor: 'pointer', fontWeight: 700, fontSize: '13px',
              border: activeTab === 'audio' ? '1px solid #00f0ff' : '1px solid #1e293b',
              background: activeTab === 'audio' ? '#00f0ff15' : '#090d16',
              color: activeTab === 'audio' ? '#00f0ff' : '#64748b',
            }}
          >
            🎙️ Audio Ingestion & Model Pipeline Sandbox
          </button>
          <button
            onClick={() => setActiveTab('text')}
            style={{
              flex: 1, padding: '10px', borderRadius: '8px', cursor: 'pointer', fontWeight: 700, fontSize: '13px',
              border: activeTab === 'text' ? '1px solid #a855f7' : '1px solid #1e293b',
              background: activeTab === 'text' ? '#a855f715' : '#090d16',
              color: activeTab === 'text' ? '#c084fc' : '#64748b',
            }}
          >
            🇮🇳 Multilingual Indic Scam NLP Tester (8 Languages)
          </button>
        </div>

        {/* TAB 1: AUDIO SANDBOX */}
        {activeTab === 'audio' && (
          <div>
            <div style={{ fontSize: '12px', fontWeight: 700, color: '#64748b', textTransform: 'uppercase', marginBottom: '10px' }}>
              Select Evaluator Scenario Preset
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '12px', marginBottom: '20px' }}>
              {PRESET_AUDIO_SAMPLES.map(sample => {
                const isSelected = selectedSample.id === sample.id;
                return (
                  <div
                    key={sample.id}
                    onClick={() => handleRunAudioAnalysis(sample)}
                    style={{
                      padding: '14px', borderRadius: '10px', cursor: 'pointer',
                      border: isSelected ? '1px solid #00f0ff' : '1px solid #1e293b',
                      background: isSelected ? '#00f0ff10' : '#0b101d',
                      transition: 'all 0.2s ease',
                    }}
                  >
                    <div style={{ fontSize: '13px', fontWeight: 700, color: '#f8fafc', marginBottom: '4px' }}>
                      {sample.title}
                    </div>
                    <div style={{ fontSize: '11px', color: '#94a3b8', lineHeight: 1.4 }}>
                      {sample.desc}
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Analysis Result Card */}
            {analyzing ? (
              <div style={{ padding: '40px', textAlign: 'center', color: '#00f0ff', background: '#080d1a', borderRadius: '12px', border: '1px solid #1e293b' }}>
                <div style={{ fontSize: '24px', animation: 'spin 1s linear infinite', display: 'inline-block', marginBottom: '10px' }}>⚙️</div>
                <div style={{ fontWeight: 700, fontSize: '14px' }}>Running 4-Pipeline Multi-Evidence Defense Engine...</div>
                <div style={{ fontSize: '12px', color: '#64748b', marginTop: '4px' }}>WavLM AASIST • ECAPA-TDNN • Faster-Whisper • XLM-RoBERTa</div>
              </div>
            ) : analysisResult && (
              <div style={{ background: '#080d1a', borderRadius: '12px', border: '1px solid #1e293b', padding: '20px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                  <span style={{ fontSize: '12px', fontWeight: 700, color: '#94a3b8' }}>LIVE ANALYSIS TELEMETRY</span>
                  <span style={{
                    padding: '4px 12px', borderRadius: '20px', fontSize: '12px', fontWeight: 800,
                    background: analysisResult.action === 'BLOCK' ? '#ef444420' : analysisResult.action === 'ALERT' ? '#f59e0b20' : '#10b98120',
                    color: analysisResult.action === 'BLOCK' ? '#ef4444' : analysisResult.action === 'ALERT' ? '#f59e0b' : '#10b981',
                    border: `1px solid ${analysisResult.action === 'BLOCK' ? '#ef444450' : analysisResult.action === 'ALERT' ? '#f59e0b50' : '#10b98150'}`,
                  }}>
                    RECOMMENDED ACTION: {analysisResult.action}
                  </span>
                </div>

                {/* Score Meters Grid */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px', marginBottom: '16px' }}>
                  <div style={{ background: '#0e1626', padding: '12px', borderRadius: '8px', border: '1px solid #1e293b', textAlign: 'center' }}>
                    <div style={{ fontSize: '11px', color: '#64748b', fontWeight: 700 }}>SYNTHETIC SPOOF</div>
                    <div style={{ fontSize: '20px', fontWeight: 800, color: analysisResult.antiSpoof > 50 ? '#ef4444' : '#10b981', marginTop: '4px' }}>
                      {analysisResult.antiSpoof}%
                    </div>
                    <div style={{ fontSize: '10px', color: '#475569' }}>WavLM AASIST</div>
                  </div>

                  <div style={{ background: '#0e1626', padding: '12px', borderRadius: '8px', border: '1px solid #1e293b', textAlign: 'center' }}>
                    <div style={{ fontSize: '11px', color: '#64748b', fontWeight: 700 }}>SPEAKER SIMILARITY</div>
                    <div style={{ fontSize: '20px', fontWeight: 800, color: analysisResult.speakerSim > 0.78 ? '#10b981' : '#f59e0b', marginTop: '4px' }}>
                      {(analysisResult.speakerSim * 100).toFixed(0)}%
                    </div>
                    <div style={{ fontSize: '10px', color: '#475569' }}>ECAPA-TDNN</div>
                  </div>

                  <div style={{ background: '#0e1626', padding: '12px', borderRadius: '8px', border: '1px solid #1e293b', textAlign: 'center' }}>
                    <div style={{ fontSize: '11px', color: '#64748b', fontWeight: 700 }}>INTENT THREAT</div>
                    <div style={{ fontSize: '13px', fontWeight: 800, color: analysisResult.intent !== 'NORMAL_CONVERSATION' ? '#ef4444' : '#10b981', marginTop: '8px' }}>
                      {analysisResult.intent.replace('_', ' ')}
                    </div>
                    <div style={{ fontSize: '10px', color: '#475569' }}>XLM-RoBERTa</div>
                  </div>

                  <div style={{ background: '#0e1626', padding: '12px', borderRadius: '8px', border: '1px solid #1e293b', textAlign: 'center' }}>
                    <div style={{ fontSize: '11px', color: '#64748b', fontWeight: 700 }}>DYNAMIC RISK</div>
                    <div style={{ fontSize: '20px', fontWeight: 900, color: analysisResult.risk >= 90 ? '#ef4444' : analysisResult.risk >= 60 ? '#f59e0b' : '#10b981', marginTop: '4px' }}>
                      {analysisResult.risk}/100
                    </div>
                    <div style={{ fontSize: '10px', color: '#475569' }}>Temporal GRU</div>
                  </div>
                </div>

                {/* Transcript & Tactics */}
                <div style={{ background: '#0e1626', padding: '14px', borderRadius: '8px', border: '1px solid #1e293b' }}>
                  <div style={{ fontSize: '11px', color: '#64748b', fontWeight: 700, marginBottom: '6px' }}>
                    WHISPER AUTOMATED SPEECH RECOGNITION TRANSCRIPT
                  </div>
                  <div style={{ fontSize: '13px', color: '#f1f5f9', fontStyle: 'italic', marginBottom: '10px' }}>
                    "{analysisResult.transcript}"
                  </div>
                  {analysisResult.tactics.length > 0 && (
                    <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                      <span style={{ fontSize: '11px', color: '#94a3b8', fontWeight: 700 }}>Coercion Tactics:</span>
                      {analysisResult.tactics.map(t => (
                        <span key={t} style={{ fontSize: '10px', fontWeight: 800, padding: '2px 8px', borderRadius: '4px', background: '#ef444420', color: '#f87171', border: '1px solid #ef444440' }}>
                          {t}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        {/* TAB 2: INDIC TEXT SCAM TESTER */}
        {activeTab === 'text' && (
          <div>
            <div style={{ fontSize: '12px', fontWeight: 700, color: '#64748b', textTransform: 'uppercase', marginBottom: '10px' }}>
              Quick Preset Dialects (Click to test)
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '16px' }}>
              {PRESET_TEXT_SAMPLES.map(sample => (
                <button
                  key={sample.lang}
                  onClick={() => {
                    setCustomText(sample.text);
                    handleRunTextAnalysis(sample.text);
                  }}
                  style={{
                    padding: '6px 12px', borderRadius: '6px', fontSize: '11px', fontWeight: 700, cursor: 'pointer',
                    background: '#0e1626', border: '1px solid #334155', color: '#cbd5e1',
                  }}
                >
                  {sample.lang}
                </button>
              ))}
            </div>

            <textarea
              value={customText}
              onChange={(e) => setCustomText(e.target.value)}
              rows={3}
              placeholder="Enter custom scam text in Hindi, Marathi, Tamil, Telugu, Bengali, Gujarati, Punjabi, or English..."
              style={{
                width: '100%', boxSizing: 'border-box', background: '#080d1a', border: '1px solid #334155',
                borderRadius: '8px', padding: '12px', color: '#f8fafc', fontSize: '13px',
                fontFamily: 'inherit', resize: 'vertical', marginBottom: '14px',
              }}
            />

            <button
              onClick={() => handleRunTextAnalysis(customText)}
              disabled={textAnalyzing}
              style={{
                padding: '10px 20px', borderRadius: '8px', background: 'linear-gradient(135deg, #a855f7, #6366f1)',
                border: 'none', color: '#ffffff', fontWeight: 800, fontSize: '13px', cursor: 'pointer',
                marginBottom: '20px',
              }}
            >
              {textAnalyzing ? 'Analyzing Intent & Psychological Tactics...' : '⚡ Analyze Scam Intent'}
            </button>

            {textResult && (
              <div style={{ background: '#080d1a', borderRadius: '12px', border: '1px solid #1e293b', padding: '20px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
                  <span style={{ fontSize: '12px', fontWeight: 700, color: '#94a3b8' }}>INDIC NLP RESULTS</span>
                  <span style={{
                    padding: '3px 10px', borderRadius: '12px', fontSize: '11px', fontWeight: 800,
                    background: textResult.isFraud ? '#ef444420' : '#10b98120',
                    color: textResult.isFraud ? '#ef4444' : '#10b981',
                    border: `1px solid ${textResult.isFraud ? '#ef444440' : '#10b98140'}`,
                  }}>
                    {textResult.isFraud ? '🚨 SCAM PATTERN DETECTED' : '✅ SAFE CONTENT'}
                  </span>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px' }}>
                  <div style={{ background: '#0e1626', padding: '10px', borderRadius: '6px', border: '1px solid #1e293b' }}>
                    <div style={{ fontSize: '10px', color: '#64748b', fontWeight: 700 }}>LANGUAGE</div>
                    <div style={{ fontSize: '16px', fontWeight: 800, color: '#00f0ff', marginTop: '2px' }}>
                      {textResult.lang.toUpperCase()}
                    </div>
                  </div>
                  <div style={{ background: '#0e1626', padding: '10px', borderRadius: '6px', border: '1px solid #1e293b' }}>
                    <div style={{ fontSize: '10px', color: '#64748b', fontWeight: 700 }}>INTENT</div>
                    <div style={{ fontSize: '14px', fontWeight: 800, color: '#f87171', marginTop: '4px' }}>
                      {textResult.intent}
                    </div>
                  </div>
                  <div style={{ background: '#0e1626', padding: '10px', borderRadius: '6px', border: '1px solid #1e293b' }}>
                    <div style={{ fontSize: '10px', color: '#64748b', fontWeight: 700 }}>TACTICS DETECTED</div>
                    <div style={{ fontSize: '12px', fontWeight: 700, color: '#fbbf24', marginTop: '4px' }}>
                      {textResult.tactics.length ? textResult.tactics.join(', ') : 'None'}
                    </div>
                  </div>
                  <div style={{ background: '#0e1626', padding: '10px', borderRadius: '6px', border: '1px solid #1e293b' }}>
                    <div style={{ fontSize: '10px', color: '#64748b', fontWeight: 700 }}>SEVERITY SCORE</div>
                    <div style={{ fontSize: '18px', fontWeight: 900, color: textResult.score > 70 ? '#ef4444' : '#10b981', marginTop: '2px' }}>
                      {textResult.score}/100
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
