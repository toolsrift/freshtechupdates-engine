import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { Icon } from "./IllusHero";
import { IllusScene, IllusBundle } from "./IllusScene";

// Side by side (or top/bottom in a Short): two things compared, each with an illustration or icon,
// a name, a big value and up to 3 short facts; "vs" badge in the middle.
type Side = { name: string; value?: string; icon?: string; facts?: string[]; bundle?: IllusBundle };
export type CompareProps = { title?: string; left: Side; right: Side; accent?: string; ink?: string; fontFamily?: string };

export const Compare: React.FC<CompareProps> = ({ title, left, right, accent = "#22D3EE", ink = "#F8FAFC", fontFamily }) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const vertical = height > width;
  const u = width / (vertical ? 1080 : 1920);
  const side = (s: Side, i: number) => {
    const p = spring({ frame: frame - (8 + i * 16), fps, config: { damping: 15 } });
    const col = i === 0 ? ink : accent;
    return (
      <div key={i} style={{ flex: 1, position: "relative", borderRadius: 34 * u, background: "rgba(255,255,255,0.05)", border: `2px solid ${col}33`, padding: 36 * u,
        display: "flex", flexDirection: "column", gap: 14 * u, opacity: p, transform: `translate${vertical ? "Y" : "X"}(${(1 - p) * (i ? 80 : -80)}px)` }}>
        <div style={{ position: "relative", height: (vertical ? 330 : 360) * u }}>
          {s.bundle ? <IllusScene bundle={s.bundle} style={{ inset: 0 }} /> : (
            <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center" }}>
              <div style={{ width: 200 * u, height: 200 * u, borderRadius: 50 * u, background: `${col}22`, display: "flex", alignItems: "center", justifyContent: "center" }}>
                <Icon name={s.icon || "circle"} size={110 * u} color={col} />
              </div>
            </div>)}
        </div>
        <div style={{ fontSize: 46 * u, fontWeight: 700, color: ink }}>{s.name}</div>
        {s.value ? <div style={{ fontSize: 88 * u, fontWeight: 800, color: col, lineHeight: 1, letterSpacing: "-0.03em" }}>{s.value}</div> : null}
        {(s.facts || []).slice(0, 3).map((f, k) => (
          <div key={k} style={{ fontSize: 32 * u, color: ink, opacity: interpolate(frame, [30 + i * 16 + k * 8, 40 + i * 16 + k * 8], [0, 0.85], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }}>• {f}</div>
        ))}
      </div>
    );
  };
  const tp = (title || "").split(/(\*[^*]+\*)/g).filter(Boolean);
  const vs = spring({ frame: frame - 26, fps, config: { damping: 9 } });
  return (
    <AbsoluteFill style={{ fontFamily, padding: vertical ? `${200 * u}px ${60 * u}px ${300 * u}px` : `${130 * u}px ${120 * u}px ${110 * u}px`, gap: 30 * u }}>
      {title ? <div style={{ fontSize: (vertical ? 66 : 60) * u, fontWeight: 700, color: ink, letterSpacing: "-0.02em" }}>
        {tp.map((t, i) => t.startsWith("*") ? <span key={i} style={{ color: accent }}>{t.slice(1, -1)}</span> : <span key={i}>{t}</span>)}</div> : null}
      <div style={{ flex: 1, display: "flex", flexDirection: vertical ? "column" : "row", gap: 40 * u, position: "relative" }}>
        {side(left, 0)}{side(right, 1)}
        <div style={{ position: "absolute", left: "50%", top: "50%", width: 120 * u, height: 120 * u, marginLeft: -60 * u, marginTop: -60 * u, borderRadius: 60 * u,
          background: accent, color: "#0B1020", fontWeight: 800, fontSize: 46 * u, display: "flex", alignItems: "center", justifyContent: "center", transform: `scale(${vs})` }}>vs</div>
      </div>
    </AbsoluteFill>
  );
};
