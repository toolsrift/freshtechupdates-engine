import React from "react";
import { AbsoluteFill } from "remotion";
import { COMPONENTS, brandFont } from "./generated/registry";
import { FtLogo, Plan } from "./Video";

// Thumbnail / cover: one beat frozen on its settled frame, plus a short headline.
// text: "Anthropic is *public*" -> the *word* gets the accent.
export const Thumb: React.FC<{ plan: Plan; beat: number; frame: number; text: string; scale?: number; layout?: "left" | "bottom" | "none" }> = ({
  plan, beat, frame, text, scale = 0.82, layout = "left",
}) => {
  const b = plan.beats[Math.min(beat, plan.beats.length - 1)];
  const C = COMPONENTS[b.component];
  const parts = text.split(/(\*[^*]+\*)/g).filter(Boolean);
  const big = layout === "left";
  return (
    <AbsoluteFill style={{ background: plan.look.background, fontFamily: brandFont }}>
      <AbsoluteFill style={{ transform: big ? `translateX(22%) scale(${scale})` : `scale(${scale})` }}>
        {C ? <C {...b.props} {...(b.logoProp ? { logo: <FtLogo size={64} /> } : {})} /> : null}
      </AbsoluteFill>
      {layout === "none" ? null : (
        <AbsoluteFill style={big
          ? { background: `linear-gradient(90deg, ${plan.look.background} 38%, transparent 70%)`, justifyContent: "center", paddingLeft: 64 }
          : { background: `linear-gradient(0deg, ${plan.look.background} 28%, transparent 55%)`, justifyContent: "flex-end", alignItems: "center", paddingBottom: 220 }}>
          <div style={{ color: plan.look.ink, fontSize: big ? 104 : 116, fontWeight: 700, lineHeight: 1.02, maxWidth: big ? 640 : 960,
            textAlign: big ? "left" : "center", letterSpacing: "-0.02em" }}>
            {parts.map((p, i) => p.startsWith("*")
              ? <span key={i} style={{ color: plan.look.accent }}>{p.slice(1, -1)}</span>
              : <span key={i}>{p}</span>)}
          </div>
        </AbsoluteFill>
      )}
      <div style={{ position: "absolute", left: big ? 64 : 0, right: big ? undefined : 0, top: 44, display: "flex", justifyContent: big ? "flex-start" : "center", alignItems: "center", gap: 14 }}>
        <FtLogo size={big ? 110 : 150} />
      </div>
    </AbsoluteFill>
  );
};
