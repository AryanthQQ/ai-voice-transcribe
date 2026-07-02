/**
 * Semicircular risk gauge (pure SVG). Color shifts with the score.
 */
export function RiskGauge({ score }: { score: number }) {
  const clamped = Math.max(0, Math.min(100, score));
  const radius = 70;
  const stroke = 14;
  const cx = 90;
  const cy = 90;

  const startAngle = 180;
  const endAngle = 0;
  const angle = startAngle - (clamped / 100) * (startAngle - endAngle);

  const polar = (a: number) => {
    const rad = (a * Math.PI) / 180;
    return { x: cx + radius * Math.cos(rad), y: cy - radius * Math.sin(rad) };
  };

  const arc = (from: number, to: number) => {
    const s = polar(from);
    const e = polar(to);
    const large = Math.abs(from - to) > 180 ? 1 : 0;
    const sweep = from > to ? 1 : 0;
    return `M ${s.x} ${s.y} A ${radius} ${radius} 0 ${large} ${sweep} ${e.x} ${e.y}`;
  };

  const color = clamped >= 60 ? "#ef4444" : clamped >= 35 ? "#f97316" : clamped >= 12 ? "#f59e0b" : "#10b981";

  return (
    <div className="flex flex-col items-center">
      <svg viewBox="0 0 180 110" className="w-full max-w-[220px]">
        <path d={arc(180, 0)} fill="none" stroke="#eef2f6" strokeWidth={stroke} strokeLinecap="round" />
        <path
          d={arc(180, angle)}
          fill="none"
          stroke={color}
          strokeWidth={stroke}
          strokeLinecap="round"
          style={{ transition: "all 0.9s cubic-bezier(0.22,1,0.36,1)" }}
        />
        <text x="90" y="78" textAnchor="middle" className="fill-slate-900" style={{ fontSize: 34, fontWeight: 800 }}>
          {clamped}
        </text>
        <text x="90" y="96" textAnchor="middle" className="fill-slate-400" style={{ fontSize: 10, fontWeight: 600 }}>
          / 100 RISK
        </text>
      </svg>
    </div>
  );
}
