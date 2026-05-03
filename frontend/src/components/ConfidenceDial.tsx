"use client";
import { useEffect, useRef, useState } from "react";

const SIZE = 120;
const STROKE = 10;
const RADIUS = (SIZE - STROKE) / 2;
const CIRC = Math.PI * RADIUS; // semicircle length

export function ConfidenceDial({
  value,
  threshold = 0.5,
  className = "",
}: {
  value: number;
  threshold?: number;
  className?: string;
}) {
  const safe = Math.max(0, Math.min(1, value));
  const lowConf = safe < threshold;
  const stroke = lowConf ? "#b45309" : "#0f766e";

  const [animated, setAnimated] = useState(0);
  const ran = useRef(false);
  useEffect(() => {
    if (ran.current) {
      setAnimated(safe);
      return;
    }
    ran.current = true;
    const t = window.setTimeout(() => setAnimated(safe), 30);
    return () => window.clearTimeout(t);
  }, [safe]);

  const dash = animated * CIRC;
  const tickAngle = -180 + threshold * 180;

  return (
    <div
      className={`relative flex flex-col items-center ${className}`}
      role="meter"
      aria-valuenow={Number(safe.toFixed(2))}
      aria-valuemin={0}
      aria-valuemax={1}
      aria-label={`confidence ${safe.toFixed(2)} of 1.0${lowConf ? ", below threshold" : ""}`}
    >
      <svg
        width={SIZE}
        height={SIZE / 2 + STROKE}
        viewBox={`0 0 ${SIZE} ${SIZE / 2 + STROKE}`}
        className="overflow-visible"
      >
        {/* track */}
        <path
          d={`M ${STROKE / 2} ${SIZE / 2}
              A ${RADIUS} ${RADIUS} 0 0 1 ${SIZE - STROKE / 2} ${SIZE / 2}`}
          fill="none"
          stroke="#e5e7eb"
          strokeWidth={STROKE}
          strokeLinecap="round"
        />
        {/* value */}
        <path
          d={`M ${STROKE / 2} ${SIZE / 2}
              A ${RADIUS} ${RADIUS} 0 0 1 ${SIZE - STROKE / 2} ${SIZE / 2}`}
          fill="none"
          stroke={stroke}
          strokeWidth={STROKE}
          strokeLinecap="round"
          strokeDasharray={`${dash} ${CIRC}`}
          style={{ transition: "stroke-dasharray 600ms cubic-bezier(.2,.8,.2,1)" }}
        />
        {/* threshold tick */}
        <g transform={`rotate(${tickAngle} ${SIZE / 2} ${SIZE / 2})`}>
          <line
            x1={SIZE / 2}
            y1={SIZE / 2 - RADIUS - STROKE / 2}
            x2={SIZE / 2}
            y2={SIZE / 2 - RADIUS + STROKE / 2}
            stroke="#94a3b8"
            strokeWidth={1.5}
            strokeDasharray="2 2"
          />
        </g>
      </svg>
      <div className="-mt-7 text-center">
        <div className="font-display text-2xl font-semibold tabular-nums text-ink">
          {safe.toFixed(2)}
        </div>
        <div className="text-[10px] uppercase tracking-wider text-ink-muted">
          confidence
        </div>
      </div>
    </div>
  );
}

export default ConfidenceDial;
