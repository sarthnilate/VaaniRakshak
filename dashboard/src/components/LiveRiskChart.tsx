// ============================================================
// VAANIRAKSHAK — Live Risk Radar Chart (Recharts)
// ============================================================
import React, { useMemo } from 'react';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, ReferenceLine,
} from 'recharts';

interface RiskRadarProps {
  trajectory: number[];
  isActive: boolean;
}

const CustomTooltip: React.FC<{ active?: boolean; payload?: Array<{ value: number }> }> = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  const v = payload[0].value;
  const color = v >= 90 ? '#ef4444' : v >= 80 ? '#f59e0b' : v >= 60 ? '#f97316' : '#10b981';
  return (
    <div style={{
      background: 'rgba(10,16,32,0.95)', border: `1px solid ${color}40`,
      borderRadius: '8px', padding: '8px 14px',
      fontFamily: "'JetBrains Mono', monospace", fontSize: '13px',
    }}>
      <div style={{ color, fontWeight: '700' }}>Risk: {v}</div>
    </div>
  );
};

export const LiveRiskChart: React.FC<RiskRadarProps> = ({ trajectory, isActive }) => {
  const data = useMemo(() =>
    trajectory.map((v, i) => ({ frame: `F${i + 1}`, risk: v })),
    [trajectory]
  );

  const lastRisk = trajectory[trajectory.length - 1] ?? 0;
  const gradientId = `riskGrad_${isActive ? 'a' : 'i'}`;
  const strokeColor = lastRisk >= 90 ? '#ef4444' : lastRisk >= 80 ? '#f59e0b' : lastRisk >= 60 ? '#f97316' : '#10b981';

  return (
    <div className="card" style={{ padding: '20px' }}>
      <div className="section-header">
        <div className="section-header__icon">📈</div>
        <div>
          <div className="section-header__title">Live Risk Trajectory</div>
          <div style={{ fontSize: '11px', color: 'var(--text-dim)', marginTop: '2px' }}>
            Real-time multi-evidence risk score • 2s frames
          </div>
        </div>
        <div className="section-header__label">
          <span className="badge badge--live">
            <span className="pulse-dot" style={{ background: strokeColor }} />
            LIVE
          </span>
        </div>
      </div>

      {/* Threshold Labels */}
      <div style={{
        display: 'flex', gap: '12px', marginBottom: '12px', flexWrap: 'wrap',
      }}>
        {[
          { label: 'CRITICAL', val: 90, color: '#ef4444' },
          { label: 'HIGH', val: 80, color: '#f59e0b' },
          { label: 'MEDIUM', val: 60, color: '#f97316' },
          { label: 'LOW', val: 30, color: '#10b981' },
        ].map(({ label, val, color }) => (
          <div key={label} style={{
            display: 'flex', alignItems: 'center', gap: '5px',
            fontSize: '10px', color, fontFamily: "'JetBrains Mono', monospace",
            fontWeight: '600', letterSpacing: '0.06em',
          }}>
            <div style={{ width: '18px', height: '1px', background: color, opacity: 0.7 }} />
            {label} {val}
          </div>
        ))}
      </div>

      {data.length === 0 ? (
        <div style={{
          height: '200px', display: 'flex', alignItems: 'center', justifyContent: 'center',
          color: 'var(--text-dim)', fontFamily: "'JetBrains Mono', monospace", fontSize: '13px',
          border: '1px dashed var(--bg-border)', borderRadius: '8px',
          flexDirection: 'column', gap: '8px',
        }}>
          <span style={{ fontSize: '24px', opacity: 0.4 }}>📡</span>
          Awaiting call session...
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={200}>
          <AreaChart data={data} margin={{ top: 5, right: 5, left: -10, bottom: 5 }}>
            <defs>
              <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={strokeColor} stopOpacity={0.3} />
                <stop offset="95%" stopColor={strokeColor} stopOpacity={0.02} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(26,45,74,0.8)" vertical={false} />
            <XAxis dataKey="frame" tick={{ fill: 'var(--text-dim)', fontSize: 11, fontFamily: 'monospace' }} axisLine={false} tickLine={false} />
            <YAxis domain={[0, 100]} tick={{ fill: 'var(--text-dim)', fontSize: 11, fontFamily: 'monospace' }} axisLine={false} tickLine={false} />
            <Tooltip content={<CustomTooltip />} />
            {/* Threshold lines */}
            <ReferenceLine y={90} stroke="#ef4444" strokeDasharray="4 4" strokeOpacity={0.5} />
            <ReferenceLine y={80} stroke="#f59e0b" strokeDasharray="4 4" strokeOpacity={0.4} />
            <ReferenceLine y={60} stroke="#f97316" strokeDasharray="4 4" strokeOpacity={0.3} />
            <Area
              type="monotone" dataKey="risk"
              stroke={strokeColor} strokeWidth={2.5}
              fill={`url(#${gradientId})`}
              dot={false}
              animationDuration={600}
            />
          </AreaChart>
        </ResponsiveContainer>
      )}
    </div>
  );
};
