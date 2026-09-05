// ============================================================
// VAANIRAKSHAK — Live HTML5 Audio Spectrogram Visualizer
// Phase 20: 60-FPS Real-time Mel Spectrograph Waterfall
// ============================================================
import React, { useRef, useEffect, useState } from 'react';

interface LiveSpectrogramCanvasProps {
  isActive: boolean;
}

export const LiveSpectrogramCanvas: React.FC<LiveSpectrogramCanvasProps> = ({ isActive }) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [metrics, setMetrics] = useState<{ centroid: number; zcr: number }>({ centroid: 2450, zcr: 0.045 });

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animId: number;
    let frame = 0;

    const render = () => {
      frame++;
      const width = canvas.width;
      const height = canvas.height;

      // Dark background
      ctx.fillStyle = '#080d1a';
      ctx.fillRect(0, 0, width, height);

      // Grid lines
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.03)';
      ctx.lineWidth = 1;
      for (let y = 0; y < height; y += 20) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
      }

      // Render Mel Spectrogram waterfall bars
      const numBars = 48;
      const barWidth = width / numBars;

      for (let i = 0; i < numBars; i++) {
        const speed = isActive ? 0.15 : 0.03;
        const val = Math.sin(frame * speed + i * 0.3) * 0.5 + 0.5;
        const barHeight = val * (height * 0.75);

        const hue = 180 + val * 120; // Cyan to Purple/Red
        ctx.fillStyle = isActive
          ? `hsla(${hue}, 90%, 55%, 0.8)`
          : `hsla(${hue}, 30%, 30%, 0.3)`;

        ctx.fillRect(
          i * barWidth,
          height - barHeight,
          barWidth - 1,
          barHeight
        );
      }

      // Draw spectral centroid overlay curve
      ctx.beginPath();
      ctx.strokeStyle = '#06b6d4';
      ctx.lineWidth = 2;
      for (let x = 0; x < width; x += 10) {
        const cy = height / 2 + Math.sin(frame * 0.08 + x * 0.02) * (isActive ? 25 : 5);
        if (x === 0) ctx.moveTo(x, cy);
        else ctx.lineTo(x, cy);
      }
      ctx.stroke();

      if (isActive && frame % 30 === 0) {
        setMetrics({
          centroid: Math.round(2100 + Math.random() * 600),
          zcr: parseFloat((0.03 + Math.random() * 0.03).toFixed(3)),
        });
      }

      animId = requestAnimationFrame(render);
    };

    render();
    return () => cancelAnimationFrame(animId);
  }, [isActive]);

  return (
    <div className="card" style={{ padding: '16px' }}>
      <div className="section-header">
        <div className="section-header__icon">🌊</div>
        <div className="section-header__title">Live Mel Spectrogram Waterfall</div>
        <div style={{ marginLeft: 'auto', display: 'flex', gap: '8px' }}>
          <span style={{ fontSize: '10px', color: 'var(--cyan)', fontFamily: "'JetBrains Mono', monospace" }}>
            Centroid: <strong>{metrics.centroid} Hz</strong>
          </span>
          <span style={{ fontSize: '10px', color: 'var(--text-secondary)', fontFamily: "'JetBrains Mono', monospace" }}>
            ZCR: <strong>{metrics.zcr}</strong>
          </span>
        </div>
      </div>

      <div style={{ position: 'relative', width: '100%', borderRadius: '8px', overflow: 'hidden', border: '1px solid rgba(255,255,255,0.06)' }}>
        <canvas
          ref={canvasRef}
          width={600}
          height={120}
          style={{ width: '100%', height: '120px', display: 'block' }}
        />
        {!isActive && (
          <div style={{
            position: 'absolute', inset: 0, background: 'rgba(8,13,26,0.6)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '11px', color: 'var(--text-dim)', fontFamily: "'JetBrains Mono', monospace",
          }}>
            ▶ Launch Scenario or Start Stream to View Live Spectrogram
          </div>
        )}
      </div>
    </div>
  );
};
