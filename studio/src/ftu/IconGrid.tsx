import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { Icon, TipCard } from "./IllusHero";
import { IllusScene, IllusBundle } from "./IllusScene";

// A list told with icons: 2-6 tiles pop in one by one (each with an icon, a short label and an optional value),
// optional title above and an optional small illustration in the corner.
export type IconGridProps = {
  title?: string;                       // *word* = accent
  items: { icon: string; label: string; value?: string }[];
  bundle?: IllusBundle;                 // optional illustration (set by build.py from props.scene)
  tip?: string;
  accent?: string; ink?: string; fontFamily?: string;
};

export const IconGrid: React.FC<IconGridProps> = ({ title, items, bundle, tip, accent = "#22D3EE", ink = "#F8FAFC", fontFamily }) => {
  const frame = useCurrentFrame();
  const { fps, width, height, durationInFrames } = useVideoConfig();
  const vertical = height > width;
  const u = width / (vertical ? 1080 : 1920);
  const n = Math.min(items.length, 6);
  const cols = vertical ? (n <= 3 ? 1 : 2) : (n <= 3 ? n : n === 4 ? 2 : 3);
  const rows = Math.ceil(n / cols);
  const gridW = vertical ? 940 * u : (bundle ? 1180 : 1560) * u;
  const tileH = vertical ? (cols === 1 ? (n > 3 ? 170 : 190) : 260) * u : (rows === 1 ? 360 : 250) * u;
  const step = Math.max(8, Math.min(22, Math.floor((durationInFrames * 0.5) / Math.max(1, n))));
  const tp = (title || "").split(/(\*[^*]+\*)/g).filter(Boolean);
  return (
    <AbsoluteFill style={{ fontFamily, alignItems: vertical ? "center" : "flex-start", justifyContent: "center", paddingLeft: vertical ? 0 : 120 * u }}>
      {bundle ? <IllusScene bundle={bundle} style={vertical ? { left: 160 * u, right: 160 * u, top: 190 * u, height: 420 * u } : { right: 40 * u, top: 200 * u, width: 620 * u, height: 680 * u }} /> : null}
      <div style={{ width: gridW, display: "flex", flexDirection: "column", gap: 34 * u, marginTop: vertical && bundle ? 330 * u : 0, marginBottom: vertical ? 120 * u : 0 }}>
        {title ? (
          <div style={{ fontSize: (vertical ? 70 : 64) * u, fontWeight: 700, color: ink, lineHeight: 1.08, letterSpacing: "-0.02em",
            opacity: interpolate(frame, [2, 14], [0, 1], { extrapolateRight: "clamp" }) }}>
            {tp.map((t, i) => t.startsWith("*") ? <span key={i} style={{ color: accent }}>{t.slice(1, -1)}</span> : <span key={i}>{t}</span>)}
          </div>
        ) : null}
        <div style={{ display: "grid", gridTemplateColumns: `repeat(${cols}, 1fr)`, gap: 24 * u }}>
          {items.slice(0, n).map((it, i) => {
            const p = spring({ frame: frame - (10 + i * step), fps, config: { damping: 13, mass: 0.6 } });
            const row = cols === 1;
            return (
              <div key={i} style={{ height: tileH, borderRadius: 30 * u, background: "rgba(255,255,255,0.06)", border: `2px solid ${accent}40`,
                display: "flex", flexDirection: row ? "row" : "column", alignItems: row ? "center" : "flex-start", justifyContent: row ? "flex-start" : "space-between",
                gap: 26 * u, padding: 32 * u, opacity: p, transform: `translateY(${(1 - p) * 50}px) scale(${0.9 + 0.1 * p})` }}>
                <div style={{ width: 110 * u, height: 110 * u, borderRadius: 28 * u, background: accent, display: "flex", alignItems: "center", justifyContent: "center", flex: "none",
                  transform: `rotate(${(1 - p) * -20}deg)` }}>
                  <Icon name={it.icon} size={62 * u} color="#0B1020" />
                </div>
                <div style={{ display: "flex", flexDirection: "column", gap: 6 * u }}>
                  {it.value ? <span style={{ fontSize: 64 * u, fontWeight: 800, color: accent, letterSpacing: "-0.02em", lineHeight: 1 }}>{it.value}</span> : null}
                  <span style={{ fontSize: (vertical ? 44 : 38) * u, fontWeight: 600, color: ink, lineHeight: 1.15 }}>{it.label}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
      {tip ? <TipCard text={tip} accent={accent} ink={ink} u={u} vertical={vertical} at={Math.round(durationInFrames * 0.55)} /> : null}
    </AbsoluteFill>
  );
};
