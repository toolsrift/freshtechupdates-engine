import React from "react";
import { AbsoluteFill, Audio, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { slide } from "@remotion/transitions/slide";
import { wipe } from "@remotion/transitions/wipe";
import { flip } from "@remotion/transitions/flip";
import { clockWipe } from "@remotion/transitions/clock-wipe";
import { COMPONENTS, TRANSITIONS, brandFont } from "./generated/registry";
import { IllusScene, IllusBundle } from "./ftu/IllusScene";

export type Beat = {
  component: string;
  props: Record<string, unknown>;
  frames: number;
  start: number;
  transition: string;
  transitionFrames: number;
  captions: { text: string; startMs: number; endMs: number; timestampMs: number; confidence: number }[];
  logoProp: boolean;
  logoSize?: "big" | "small";
  tag: string;
  source: string;
  visual?: { bundle: IllusBundle; place: "top" | "bottom" | "left" | "right" | "corner" | "background" } | null;
};
export type Plan = {
  format: "short" | "long";
  width: number;
  height: number;
  fps: number;
  total: number;
  look: { accent: string; ink: string; background: string; font: string; bgCss?: string; light?: boolean; show?: string; sub?: string };
  captionsComponent: string | null;
  beats: Beat[];
  audio: string;
};

export const FtLogo: React.FC<{ size?: number }> = ({ size = 120 }) => (
  <Img src={staticFile("ftlogo.svg")} style={{ width: size, height: Math.round((size * 595) / 935) }} />
);

function presentation(name: string, i: number, width: number, height: number) {
  const dirs = ["from-right", "from-left", "from-bottom", "from-top"] as const;
  switch (name) {
    case "fade": return fade();
    case "slide": return slide({ direction: dirs[i % dirs.length] });
    case "wipe": return wipe({ direction: dirs[(i + 1) % dirs.length] });
    case "flip": return flip({ direction: dirs[i % dirs.length] });
    case "clock": return clockWipe({ width, height });
    default: {
      const f = TRANSITIONS[name];
      return f ? f({}) : fade();
    }
  }
}

const Chrome: React.FC<{ beat: Beat; plan: Plan; last: boolean }> = ({ beat, plan, last }) => {
  const frame = useCurrentFrame();
  const { width } = useVideoConfig();
  if (last) return null;
  const short = plan.format === "short";
  const u = width / (short ? 1080 : 1920);
  const o = interpolate(frame, [4, 16], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ pointerEvents: "none", fontFamily: brandFont, color: plan.look.ink, opacity: o }}>
      <div style={{ position: "absolute", left: 48 * u, top: (short ? 96 : 40) * u, display: "flex", alignItems: "center", gap: 14 * u }}>
        {beat.logoProp ? null : <FtLogo size={(short ? 92 : 78) * u} />}
        {beat.logoProp ? null : <span style={{ fontSize: (short ? 30 : 26) * u, fontWeight: 600, opacity: 0.92 }}>freshtechupdates</span>}
        {beat.tag ? (
          <span style={{ fontSize: (short ? 26 : 22) * u, fontWeight: 500, color: plan.look.accent, marginLeft: 8 * u }}>· {beat.tag}</span>
        ) : null}
      </div>
      {beat.source ? (
        <div style={{ position: "absolute", left: 48 * u, bottom: (short ? 70 : 36) * u, fontSize: (short ? 24 : 20) * u, opacity: 0.6, fontWeight: 500 }}>
          Source: {beat.source}
        </div>
      ) : null}
    </AbsoluteFill>
  );
};

const Captions: React.FC<{ beat: Beat; plan: Plan }> = ({ beat, plan }) => {
  const C = plan.captionsComponent ? COMPONENTS[plan.captionsComponent] : null;
  const { width, height } = useVideoConfig();
  if (!C || !beat.captions.length) return null;
  const short = plan.format === "short";
  return (
    <AbsoluteFill style={{ justifyContent: "flex-end", alignItems: "center", paddingBottom: height * (short ? 0.085 : 0.07), fontFamily: brandFont }}>
      <div style={{ width: width * (short ? 0.86 : 0.7), display: "flex", justifyContent: "center", textAlign: "center", wordSpacing: "0.22em" }}>
        <C captions={beat.captions} fontSize={short ? 60 : 48} color={plan.look.ink} activeColor={plan.look.accent} popScale={1} />
      </div>
    </AbsoluteFill>
  );
};

// Where an illustration goes next to a Remocn component, and how the component moves aside.
function visualLayout(place: string, w: number, h: number) {
  const short = h > w;
  switch (place) {
    case "top": return { ill: { left: w * 0.04, right: w * 0.04, top: h * 0.1, height: h * 0.34 }, comp: `translateY(${h * 0.17}px) scale(0.86)` };
    case "bottom": return { ill: { left: w * 0.04, right: w * 0.04, top: h * 0.56, height: h * 0.32 }, comp: `translateY(${-h * 0.15}px) scale(0.86)` };
    case "left": return { ill: { left: w * 0.02, top: h * 0.12, width: w * 0.5, height: h * 0.76 }, comp: `translateX(${w * 0.22}px) scale(0.74)` };
    case "right": return { ill: { right: w * 0.02, top: h * 0.12, width: w * 0.5, height: h * 0.76 }, comp: `translateX(${-w * 0.22}px) scale(0.74)` };
    case "corner": return { ill: short ? { right: w * 0.02, bottom: h * 0.2, width: w * 0.5, height: h * 0.18 } : { right: w * 0.02, bottom: h * 0.05, width: w * 0.3, height: h * 0.3 }, comp: "none" };
    default: return { ill: { left: 0, right: 0, top: h * 0.15, height: h * 0.7, opacity: 0.22 }, comp: "none" };
  }
}

const BeatView: React.FC<{ beat: Beat; plan: Plan; last: boolean }> = ({ beat, plan, last }) => {
  const C = COMPONENTS[beat.component];
  const { width, height } = useVideoConfig();
  const extra: Record<string, unknown> = {};
  if (beat.logoProp) extra.logo = <FtLogo size={beat.logoSize === "big" ? (plan.format === "short" ? 260 : 200) : 64} />;
  if (beat.component.startsWith("ftu-")) Object.assign(extra, { fontFamily: brandFont, accent: plan.look.accent, ink: plan.look.ink, ...beat.props });
  const v = beat.visual ? visualLayout(beat.visual.place, width, height) : null;
  const comp = C ? <C {...beat.props} {...extra} /> : <AbsoluteFill style={{ background: "red" }} />;
  return (
    <AbsoluteFill style={{ background: plan.look.bgCss || plan.look.background }}>
      {v && beat.visual!.place === "background" ? <IllusScene bundle={beat.visual!.bundle} style={v.ill as React.CSSProperties} /> : null}
      {v && v.comp !== "none" ? <AbsoluteFill style={{ transform: v.comp }}>{comp}</AbsoluteFill> : comp}
      {v && beat.visual!.place !== "background" ? <IllusScene bundle={beat.visual!.bundle} style={v.ill as React.CSSProperties} /> : null}
      <Captions beat={beat} plan={plan} />
      <Chrome beat={beat} plan={plan} last={last} />
    </AbsoluteFill>
  );
};

export const Video: React.FC<{ plan: Plan }> = ({ plan }) => {
  const { width, height } = useVideoConfig();
  const items: React.ReactNode[] = [];
  plan.beats.forEach((b, i) => {
    if (i > 0 && b.transition !== "none" && b.transitionFrames > 0) {
      items.push(
        <TransitionSeries.Transition key={`t${i}`} presentation={presentation(b.transition, i, width, height) as any}
          timing={linearTiming({ durationInFrames: b.transitionFrames })} />
      );
    }
    items.push(
      <TransitionSeries.Sequence key={`b${i}`} durationInFrames={b.frames}>
        <BeatView beat={b} plan={plan} last={i === plan.beats.length - 1} />
      </TransitionSeries.Sequence>
    );
  });
  return (
    <AbsoluteFill style={{ background: plan.look.bgCss || plan.look.background }}>
      <TransitionSeries>{items}</TransitionSeries>
      {plan.audio ? <Audio src={staticFile(plan.audio)} /> : null}
    </AbsoluteFill>
  );
};
