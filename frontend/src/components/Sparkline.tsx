export function Sparkline({
  values,
  width = 240,
  height = 48,
  className = "",
}: {
  values: number[];
  width?: number;
  height?: number;
  className?: string;
}) {
  if (!values.length) {
    return (
      <div
        style={{ width, height }}
        className={`flex items-center justify-center text-[11px] text-ink-muted ${className}`}
      >
        no samples yet
      </div>
    );
  }
  const min = Math.min(...values);
  const max = Math.max(...values);
  const span = max - min || 1;
  const stepX = values.length > 1 ? width / (values.length - 1) : 0;
  const points = values
    .map((v, i) => {
      const x = i * stepX;
      const y = height - ((v - min) / span) * (height - 4) - 2;
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");

  const last = values[values.length - 1];
  const lastX = (values.length - 1) * stepX;
  const lastY = height - ((last - min) / span) * (height - 4) - 2;

  return (
    <svg
      width={width}
      height={height}
      viewBox={`0 0 ${width} ${height}`}
      className={className}
      role="img"
      aria-label={`sparkline of ${values.length} samples, current ${last.toFixed(2)}`}
    >
      <polyline
        fill="none"
        stroke="#0f766e"
        strokeWidth={1.5}
        strokeLinejoin="round"
        strokeLinecap="round"
        points={points}
      />
      <circle cx={lastX} cy={lastY} r={3} fill="#0f766e" />
    </svg>
  );
}

export default Sparkline;
