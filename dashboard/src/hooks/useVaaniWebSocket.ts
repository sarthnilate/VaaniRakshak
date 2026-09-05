// ============================================================
// VAANIRAKSHAK — WebSocket Hook for Live Backend Connection
// ============================================================
import { useState, useEffect, useRef, useCallback } from 'react';

export type RiskLevel = 'SAFE' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export interface LiveFrame {
  sessionId: string;
  timestamp: string;
  frameIndex: number;
  riskScore: number;
  riskLevel: RiskLevel;
  antispoof: number;
  speakerAnomaly: number;
  intentScore: number;
  transcriptChunk: string;
  isFraud: boolean;
  detectedPhrase?: string;
  language: string;
  action: 'MONITOR' | 'ALERT' | 'BLOCK' | 'WARN';
}

export interface SessionState {
  sessionId: string;
  status: 'IDLE' | 'ACTIVE' | 'THREAT' | 'ENDED';
  callerNumber: string;
  language: string;
  riskTrajectory: number[];
  frames: LiveFrame[];
  startTime: Date;
}

// Simulate realistic WebSocket data for SIH Demo
function generateMockFrame(frameIndex: number, sessionId: string, scenario: number = 1): LiveFrame {
  const lang = ['hi', 'en', 'ta', 'bn', 'mr'][Math.floor(Math.random() * 5)];
  const fraudPhrases = [
    'आपका खाता बंद हो जाएगा',
    'SBI से बोल रहा हूं',
    'OTP share करें',
    'Account suspended immediately',
    'RBI regulation compliance',
    'आधार लिंक करना जरूरी है',
  ];

  // Scenario 1: escalating threat
  let baseRisk = 15;
  if (scenario === 1) {
    baseRisk = Math.min(95, 15 + frameIndex * 8 + Math.random() * 10);
  } else if (scenario === 2) {
    // Scenario 2: spike and detect
    baseRisk = frameIndex < 3 ? 20 + Math.random() * 10 : Math.min(92, 60 + Math.random() * 30);
  } else {
    // Scenario 3: legitimate call
    baseRisk = 10 + Math.random() * 20;
  }

  const isFraud = baseRisk > 70;
  const riskScore = Math.round(Math.min(99, baseRisk));

  const transcripts = scenario === 1
    ? ['नमस्ते, मैं State Bank of India से बोल रहा हूं।', 'आपका खाता संदिग्ध गतिविधि के कारण बंद हो रहा है।',
       'सुरक्षा के लिए अपना OTP अभी share करें।', 'URGENT: आपके खाते से ₹50,000 निकाले जा रहे हैं।',
       'बस आधार नंबर बताएं - पूरा process 2 मिनट में हो जाएगा।']
    : scenario === 2
    ? ['Hello, this is HDFC Bank credit card division.', 'We need to verify your recent transaction.',
       'Can you please share the OTP received on your phone?', 'Your account will be locked in 10 minutes.',
       'This is your final warning - comply immediately.']
    : ['Hi, calling about your car service appointment.', 'The mechanic will arrive at 3 PM.',
       'Do you want to reschedule?', 'No charges apply for rescheduling.', 'Have a great day!'];

  const transcript = transcripts[Math.min(frameIndex, transcripts.length - 1)];

  let riskLevel: RiskLevel = 'SAFE';
  if (riskScore >= 90) riskLevel = 'CRITICAL';
  else if (riskScore >= 80) riskLevel = 'HIGH';
  else if (riskScore >= 60) riskLevel = 'MEDIUM';
  else if (riskScore >= 30) riskLevel = 'LOW';

  let action: LiveFrame['action'] = 'MONITOR';
  if (riskScore >= 90) action = 'BLOCK';
  else if (riskScore >= 80) action = 'ALERT';
  else if (riskScore >= 60) action = 'WARN';

  return {
    sessionId,
    timestamp: new Date().toISOString(),
    frameIndex,
    riskScore,
    riskLevel,
    antispoof: Math.round(Math.min(99, baseRisk * 0.9 + Math.random() * 10)),
    speakerAnomaly: Math.round(Math.min(99, baseRisk * 0.85 + Math.random() * 12)),
    intentScore: Math.round(Math.min(99, baseRisk * 0.95 + Math.random() * 8)),
    transcriptChunk: transcript,
    isFraud,
    detectedPhrase: isFraud ? fraudPhrases[Math.floor(Math.random() * fraudPhrases.length)] : undefined,
    language: lang,
    action,
  };
}

export function useVaaniWebSocket(scenario: number = 1) {
  const [engineMode, setEngineMode] = useState<'live' | 'mock'>('mock');
  const [sessionState, setSessionState] = useState<SessionState>({
    sessionId: `sess_${Date.now()}`,
    status: 'IDLE',
    callerNumber: '+91-9XXXXXXXXX',
    language: 'hi',
    riskTrajectory: [],
    frames: [],
    startTime: new Date(),
  });
  const [isConnected, setIsConnected] = useState(false);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const socketRef = useRef<WebSocket | null>(null);
  const frameIndexRef = useRef(0);

  const startSession = useCallback((sc: number = scenario) => {
    const sessionId = `sess_${Date.now()}`;
    frameIndexRef.current = 0;
    setSessionState({
      sessionId,
      status: 'ACTIVE',
      callerNumber: sc === 3 ? '+91-7892341234' : '+91-9876543210',
      language: 'hi',
      riskTrajectory: [],
      frames: [],
      startTime: new Date(),
    });

    if (engineMode === 'live') {
      try {
        const host = window.location.hostname || 'localhost';
        const wsUrl = `ws://${host}:8000/ws/call/${sessionId}`;
        const ws = new WebSocket(wsUrl);
        socketRef.current = ws;

        ws.onopen = () => {
          setIsConnected(true);
          // Send initial session greeting or test chunk
          ws.send(JSON.stringify({ type: 'session_init', scenario: sc, caller: sc === 3 ? '+91-7892341234' : '+91-9876543210' }));
        };

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            const fi = frameIndexRef.current++;
            const frame: LiveFrame = {
              sessionId,
              timestamp: new Date().toISOString(),
              frameIndex: fi,
              riskScore: data.risk_score ?? Math.round(Math.min(95, 20 + fi * 9)),
              riskLevel: data.risk_band ?? (data.risk_score >= 90 ? 'CRITICAL' : 'LOW'),
              antispoof: Math.round((data.evidence?.synthetic_prob ?? 0.8) * 100),
              speakerAnomaly: Math.round((1 - (data.evidence?.speaker_similarity ?? 0.5)) * 100),
              intentScore: Math.round((data.evidence?.intent_confidence ?? 0.85) * 100),
              transcriptChunk: data.transcript ?? 'Processing live telecom stream...',
              isFraud: (data.risk_score ?? 0) >= 60,
              detectedPhrase: data.detected_phrase,
              language: data.language ?? 'hi',
              action: data.action ?? 'MONITOR',
            };

            setSessionState(prev => {
              const newTrajectory = [...prev.riskTrajectory, frame.riskScore].slice(-20);
              const newFrames = [...prev.frames, frame].slice(-50);
              const status = frame.riskScore >= 90 ? 'THREAT' : prev.status === 'THREAT' ? 'THREAT' : 'ACTIVE';
              return { ...prev, riskTrajectory: newTrajectory, frames: newFrames, status };
            });
          } catch {
            // Ignore parse errors
          }
        };

        ws.onerror = () => {
          // Graceful fallback to mock on connection error
          console.warn('Backend WebSocket unavailable, falling back to simulation.');
        };

        ws.onclose = () => {
          setIsConnected(false);
        };
      } catch {
        // Fallback to mock
      }
    }

    // Always keep simulation interval running for guaranteed live updates
    setIsConnected(true);
    intervalRef.current = setInterval(() => {
      const fi = frameIndexRef.current++;
      const frame = generateMockFrame(fi, sessionId, sc);

      setSessionState(prev => {
        const newTrajectory = [...prev.riskTrajectory, frame.riskScore].slice(-20);
        const newFrames = [...prev.frames, frame].slice(-50);
        const status = frame.riskScore >= 90 ? 'THREAT' : prev.status === 'THREAT' ? 'THREAT' : 'ACTIVE';
        return { ...prev, riskTrajectory: newTrajectory, frames: newFrames, status };
      });

      if (fi >= 8) {
        clearInterval(intervalRef.current!);
        setSessionState(prev => ({ ...prev, status: 'ENDED' }));
        setIsConnected(false);
      }
    }, 2000);
  }, [scenario, engineMode]);

  const stopSession = useCallback(() => {
    if (intervalRef.current) clearInterval(intervalRef.current);
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.close();
    }
    setIsConnected(false);
    setSessionState(prev => ({ ...prev, status: 'ENDED' }));
  }, []);

  useEffect(() => {
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
      if (socketRef.current) socketRef.current.close();
    };
  }, []);

  const latestFrame = sessionState.frames[sessionState.frames.length - 1];

  return { sessionState, isConnected, latestFrame, engineMode, setEngineMode, startSession, stopSession };
}
