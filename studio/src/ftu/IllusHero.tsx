import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { icons } from "lucide-react";
import { IllusScene, IllusBundle } from "./IllusScene";

type Point = { icon?: string; text: string };
export type IllusHeroProps = {
  bundle: IllusBundle;
  headline: string;            // *word* = accent
  kicker?: string;             // small line above the headline
  points?: Point[];            // up to 3, each max ~6 words; icon = any lucide icon name (e.g. "cpu", "shield-check")
  stat?: { value: string; label: string };
  tip?: string;                // FT Bot tip / reaction in a speech card (v1 style), max ~16 words
  layout?: "auto" | "illus-left" | "illus-right" | "stack" | "full";
  accent?: string; ink?: string; fontFamily?: string;
};

const pascal = (s: string) => s.split(/[-_ ]/).map((p) => p.charAt(0).toUpperCase() + p.slice(1)).join("");
export const Icon: React.FC<{ name?: string; size: number; color: string }> = ({ name, size, color }) => {
  const C: any = name ? (icons as any)[pascal(name)] : null;
  return C ? <C size={size} color={color} strokeWidth={2.2} /> : null;
};

export const IllusHero: React.FC<IllusHeroProps> = ({ bundle, headline, kicker, points = [], stat, tip, layout = "auto", accent = "#22D3EE", ink = "#F8FAFC", fontFamily }) => {
  const frame = useCurrentFrame();
  const { fps, width, height, durationInFrames } = useVideoConfig();
  const vertical = height > width;
  const lay = layout === "auto" ? (vertical ? "stack" : "illus-left") : layout;
  const u = width / (vertical ? 1080 : 1920);
  const words = headline.split(/\s+/);
  let inAcc = false;
  const rise = (d: number) => spring({ frame: frame - d, fps, config: { damping: 16, mass: 0.7 } });

  // slow camera push on the illustration so a long beat never sits still
  const push = interpolate(frame, [0, Math.max(60, durationInFrames)], [1, 1.07], { extrapolateRight: "clamp" });
  const ill0: React.CSSProperties = lay === "full"
    ? (vertical ? { left: 0, right: 0, top: 220 * u, height: 1000 * u } : { left: 200 * u, right: 200 * u, top: 60 * u, height: 820 * u })
    : lay === "stack"
    ? { left: 30 * u, right: 30 * u, top: 210 * u, height: 660 * u }
    : lay === "illus-left" ? { left: 40 * u, top: 150 * u, width: 1000 * u, height: 760 * u }
    : { right: 40 * u, top: 150 * u, width: 1000 * u, height: 760 * u };
  const ill: React.CSSProperties = { ...ill0, transform: `scale(${push})`, transformOrigin: "50% 60%" };
  const text: React.CSSProperties = lay === "full"
    ? (vertical ? { left: 70 * u, right: 70 * u, top: 1170 * u, textAlign: "left" } : { left: 160 * u, right: 160 * u, bottom: 150 * u, textAlign: "center", alignItems: "center" })
    : lay === "stack"
    ? { left: 70 * u, right: 70 * u, top: 900 * u, textAlign: "left" }
    : lay === "illus-left" ? { left: 1060 * u, right: 90 * u, top: 0, bottom: 0, justifyContent: "center" }
    : { left: 90 * u, width: 820 * u, top: 0, bottom: 0, justifyContent: "center" };
  const hSize = (vertical ? 84 : 76) * u * (words.length > 8 ? 0.82 : 1);

  return (
    <AbsoluteFill style={{ fontFamily }}>
      <IllusScene bundle={bundle} style={ill} />
      <div style={{ position: "absolute", display: "flex", flexDirection: "column", gap: 26 * u, ...text }}>
        {kicker ? (
          <div style={{ fontSize: 30 * u, fontWeight: 600, color: accent, opacity: interpolate(frame, [6, 16], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }}>{kicker}</div>
        ) : null}
        <div style={{ fontSize: hSize, fontWeight: 700, lineHeight: 1.06, color: ink, letterSpacing: "-0.02em" }}>
          {words.map((w, i) => {
            const starts = w.startsWith("*"); const ends = w.endsWith("*") || w.endsWith("*,") || w.endsWith("*.");
            if (starts) inAcc = true;
            const acc = inAcc;
            if (ends) inAcc = false;
            const p = rise(8 + i * 3);
            return (
              <span key={i} style={{ display: "inline-block", marginRight: "0.26em", color: acc ? accent : ink, opacity: p, transform: `translateY(${(1 - p) * 40}px)` }}>
                {w.replace(/\*/g, "")}
              </span>
            );
          })}
        </div>
        {stat ? (
          <div style={{ display: "flex", alignItems: "baseline", gap: 18 * u, opacity: rise(24), transform: `scale(${0.9 + 0.1 * rise(24)})`, transformOrigin: "0 50%" }}>
            <span style={{ fontSize: 110 * u, fontWeight: 800, color: accent, letterSpacing: "-0.03em" }}>{stat.value}</span>
            <span style={{ fontSize: 32 * u, color: ink, opacity: 0.75, maxWidth: 380 * u, lineHeight: 1.2 }}>{stat.label}</span>
          </div>
        ) : null}
        {points.slice(0, 3).map((pt, i) => {
          const p = rise(26 + i * 7);
          return (
            <div key={i} style={{ display: "flex", alignItems: "center", gap: 18 * u, opacity: p, transform: `translateX(${(1 - p) * -50}px)` }}>
              <div style={{ width: (vertical ? 76 : 66) * u, height: (vertical ? 76 : 66) * u, borderRadius: 18 * u, background: `${accent}22`, border: `2px solid ${accent}66`, display: "flex", alignItems: "center", justifyContent: "center", flex: "none" }}>
                <Icon name={pt.icon} size={36 * u} color={accent} />
              </div>
              <span style={{ fontSize: (vertical ? 44 : 38) * u, color: ink, fontWeight: 500, lineHeight: 1.2 }}>{pt.text}</span>
            </div>
          );
        })}
      </div>
      {tip ? <TipCard text={tip} accent={accent} ink={ink} u={u} vertical={vertical} at={Math.round(durationInFrames * 0.45)} top={lay === "full" ? 1030 : 700} /> : null}
    </AbsoluteFill>
  );
};

// v1's "FT Bot" tip: a speech card with the mini bot, sliding in mid-beat.
export const TipCard: React.FC<{ text: string; accent: string; ink: string; u: number; vertical: boolean; at: number; top?: number }> = ({ text, accent, ink, u, vertical, at, top = 700 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = spring({ frame: frame - at, fps, config: { damping: 14, mass: 0.6 } });
  const pos: React.CSSProperties = vertical ? { left: 60 * u, right: 60 * u, top: top * u } : { right: 80 * u, bottom: 190 * u, width: 640 * u };
  return (
    <div style={{ position: "absolute", ...pos, opacity: p, transform: `translateY(${(1 - p) * 30}px) scale(${0.92 + 0.08 * p})`, transformOrigin: "100% 100%",
      display: "flex", gap: 18 * u, alignItems: "center", background: "rgba(255,255,255,0.96)", borderRadius: 26 * u, padding: `${20 * u}px ${26 * u}px`,
      boxShadow: "0 18px 40px rgba(0,0,0,.35)", borderLeft: `${10 * u}px solid ${accent}` }}>
      <MiniBot size={78 * u} accent={accent} />
      <div style={{ display: "flex", flexDirection: "column", gap: 4 * u }}>
        <span style={{ fontSize: 22 * u, fontWeight: 700, color: accent, filter: "brightness(0.75)" }}>FT Bot</span>
        <span style={{ fontSize: (vertical ? 34 : 30) * u, color: "#141826", fontWeight: 500, lineHeight: 1.25 }}>{text}</span>
      </div>
    </div>
  );
};

export const MiniBot: React.FC<{ size: number; accent: string }> = ({ size, accent }) => (
  <svg width={size} height={size} viewBox="-100 -150 200 250" style={{ flex: "none" }}>
    <line x1="0" y1="-98" x2="0" y2="-126" stroke="#1E2452" strokeWidth="8" strokeLinecap="round" />
    <circle cx="0" cy="-134" r="13" fill="#FFD166" />
    <rect x="-72" y="-102" width="144" height="112" rx="28" fill={accent} />
    <rect x="-52" y="-84" width="104" height="72" rx="18" fill="#F4F6FB" />
    <ellipse cx="-22" cy="-54" rx="10" ry="13" fill="#1E2452" /><ellipse cx="22" cy="-54" rx="10" ry="13" fill="#1E2452" />
    <path d="M -16 -32 Q 0 -20 16 -32" stroke="#1E2452" strokeWidth="6" fill="none" strokeLinecap="round" />
    <rect x="-44" y="18" width="88" height="72" rx="18" fill="#FF4D6D" />
  </svg>
);
