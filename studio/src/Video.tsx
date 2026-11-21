import React from "react";
import { AbsoluteFill, Audio, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { slide } from "@remotion/transitions/slide";
import { wipe } from "@remotion/transitions/wipe";
import { flip } from "@remotion/transitions/flip";
import { clockWipe } from "@remotion/transitions/clock-wipe";
import { COMPONENTS, TRANSITIONS, brandFont } from "./generated/registry";

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
};
export type Plan = {
  format: "short" | "long";
  width: number;
  height: number;
  fps: number;
  total: number;
  look: { accent: string; ink: string; background: string; font: string };
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
    <AbsoluteFill style={{ justifyContent: "flex-end", alignItems: "center", paddingBottom: height * (short ? 0.13 : 0.1), fontFamily: brandFont }}>
      <div style={{ width: width * (short ? 0.86 : 0.7), display: "flex", justifyContent: "center", textAlign: "center", wordSpacing: "0.22em" }}>
        <C captions={beat.captions} fontSize={short ? 60 : 48} color={plan.look.ink} activeColor={plan.look.accent} popScale={1} />
      </div>
    </AbsoluteFill>
  );
};

const BeatView: React.FC<{ beat: Beat; plan: Plan; last: boolean }> = ({ beat, plan, last }) => {
  const C = COMPONENTS[beat.component];
  const extra: Record<string, unknown> = {};
  if (beat.logoProp) extra.logo = <FtLogo size={beat.logoSize === "big" ? (plan.format === "short" ? 260 : 200) : 64} />;
  return (
    <AbsoluteFill style={{ background: plan.look.background }}>
      {C ? <C {...beat.props} {...extra} /> : <AbsoluteFill style={{ background: "red" }} />}
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
    <AbsoluteFill style={{ background: plan.look.background }}>
      <TransitionSeries>{items}</TransitionSeries>
      {plan.audio ? <Audio src={staticFile(plan.audio)} /> : null}
    </AbsoluteFill>
  );
};
