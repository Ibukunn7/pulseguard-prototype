// Small dependency-free SVG line chart.
//
// props:
//   series: [{ key, label, color, points: [{ x, y }], dashed }]
//   band:   optional [{ x, low, high }] drawn as a shaded area
//   yMin, yMax: optional axis bounds
//   height: SVG height (width is responsive)

const W = 640;
const PAD = { top: 10, right: 12, bottom: 24, left: 44 };

function scale(domain, range) {
  const [d0, d1] = domain;
  const [r0, r1] = range;
  const span = d1 - d0 || 1;
  return (v) => r0 + ((v - d0) / span) * (r1 - r0);
}

export default function TrendChart({ series, band, yMin, yMax, height = 180 }) {
  const xs = series.flatMap((s) => s.points.map((p) => p.x));
  if (band) xs.push(...band.map((b) => b.x));
  const ys = series.flatMap((s) => s.points.map((p) => p.y));
  if (band) ys.push(...band.flatMap((b) => [b.low, b.high]));

  if (xs.length === 0) {
    return <div className="legend">No data yet</div>;
  }

  const xDomain = [Math.min(...xs), Math.max(1, Math.max(...xs))];
  const lo = yMin ?? Math.min(...ys);
  const hi = yMax ?? Math.max(...ys);
  const yDomain = [Math.floor(lo * 0.95), Math.ceil(hi * 1.05) || 1];

  const sx = scale(xDomain, [PAD.left, W - PAD.right]);
  const sy = scale(yDomain, [height - PAD.bottom, PAD.top]);

  const path = (pts) =>
    pts.map((p, i) => `${i ? "L" : "M"}${sx(p.x).toFixed(1)},${sy(p.y).toFixed(1)}`).join(" ");

  const bandPath = band && band.length
    ? [
        ...band.map((b, i) => `${i ? "L" : "M"}${sx(b.x).toFixed(1)},${sy(b.high).toFixed(1)}`),
        ...[...band].reverse().map((b) => `L${sx(b.x).toFixed(1)},${sy(b.low).toFixed(1)}`),
        "Z",
      ].join(" ")
    : null;

  const yTicks = 4;
  const ticks = Array.from({ length: yTicks + 1 }, (_, i) =>
    yDomain[0] + ((yDomain[1] - yDomain[0]) * i) / yTicks
  );
  const weekTicks = [];
  for (let d = 7; d <= xDomain[1]; d += 7) weekTicks.push(d);

  return (
    <svg className="chart" viewBox={`0 0 ${W} ${height}`} role="img">
      {ticks.map((t) => (
        <g key={t}>
          <line className="axis" x1={PAD.left} x2={W - PAD.right} y1={sy(t)} y2={sy(t)} />
          <text x={PAD.left - 6} y={sy(t) + 3} textAnchor="end">{Math.round(t)}</text>
        </g>
      ))}
      {weekTicks.map((d) => (
        <g key={d}>
          <line className="axis" x1={sx(d)} x2={sx(d)} y1={PAD.top} y2={height - PAD.bottom} />
          <text x={sx(d)} y={height - 8} textAnchor="middle">wk {d / 7}</text>
        </g>
      ))}
      {bandPath && <path d={bandPath} fill="rgba(96,165,250,0.15)" stroke="none" />}
      {series.map((s) => (
        <path
          key={s.key}
          d={path(s.points)}
          fill="none"
          stroke={s.color}
          strokeWidth={2}
          strokeDasharray={s.dashed ? "5 4" : undefined}
        />
      ))}
    </svg>
  );
}
