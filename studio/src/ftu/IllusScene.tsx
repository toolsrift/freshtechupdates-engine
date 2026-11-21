import React, { useLayoutEffect, useMemo, useRef } from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import gsap from "gsap";

// GSAP's `svgOrigin` (a pivot in the SVG's global coordinates) is wrong for elements inside scaled groups
// (the people in illus.py scenes): their arms flew off-screen. We convert every svgOrigin into a pixel
// `transformOrigin` relative to the element's own box, measured on the pristine SVG before any tween runs.
function fixOrigins(root: HTMLElement, code: string) {
  const svg = root.querySelector("svg") as SVGSVGElement | null;
  const origins = new Map<string, string>();
  if (!svg) return origins;
  const rootInv = svg.getScreenCTM()?.inverse();
  const pass = (target: any, vars: any) => {
    if (!vars || typeof vars !== "object" || !vars.svgOrigin || typeof target !== "string") return;
    const el = root.querySelector(target) as SVGGraphicsElement | null;
    if (!el || !rootInv) return;
    const [X, Y] = String(vars.svgOrigin).split(/\s+/).map(Number);
    const parent = el.parentNode as SVGGraphicsElement;
    const pm = (parent.getScreenCTM ? parent.getScreenCTM() : null);
    if (!pm) return;
    // global svg point -> screen -> parent's user space (= the element's untransformed space)
    const pt = svg.createSVGPoint(); pt.x = X; pt.y = Y;
    const scr = pt.matrixTransform(svg.getScreenCTM()!);
    const loc = scr.matrixTransform(pm.inverse());
    const bb = el.getBBox();
    origins.set(`${target}|${vars.svgOrigin}`, `${loc.x - bb.x}px ${loc.y - bb.y}px`);
  };
  const rec = { to: (t: any, v: any) => pass(t, v), fromTo: (t: any, a: any, b: any) => { pass(t, a); pass(t, b); }, set: (t: any, v: any) => pass(t, v) };
  try { new Function("tl", "gsap", code)(rec, gsap); } catch (e) { /* the real run reports errors */ }
  return origins;
}

function swap(origins: Map<string, string>, target: any, vars: any) {
  if (!vars || typeof vars !== "object" || !vars.svgOrigin) return vars;
  const o = origins.get(`${target}|${vars.svgOrigin}`);
  if (!o) return vars;
  const { svgOrigin, ...rest } = vars;
  return { ...rest, transformOrigin: o };
}

export type IllusBundle = { svg: string; js: string[]; css: string; viewBox: string; prefix: string; scene: string; family: string };

// Plays an engine/illus.py scene: its GSAP timeline is built once, paused, and seeked to the current frame,
// so every frame is deterministic (Remotion renders frames out of order across tabs).
export const IllusScene: React.FC<{ bundle: IllusBundle; style?: React.CSSProperties }> = ({ bundle, style }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const ref = useRef<HTMLDivElement>(null);
  const tl = useRef<gsap.core.Timeline | null>(null);
  const html = useMemo(
    () => `<svg viewBox="${bundle.viewBox}" width="100%" height="100%" preserveAspectRatio="xMidYMid meet" style="overflow:visible">${bundle.svg}</svg>`,
    [bundle.svg, bundle.viewBox],
  );
  useLayoutEffect(() => {
    if (!ref.current) return;
    // Fresh SVG nodes on every build: GSAP caches transform data (incl. svgOrigin offsets) on elements,
    // so a second mount (Remotion/React can mount twice) would otherwise double the pivot offsets.
    ref.current.innerHTML = html;
    const t = gsap.timeline({ paused: true });
    const code = bundle.js.join(";\n");
    const origins = fixOrigins(ref.current, code);
    const wrap = {
      to: (tg: any, v: any, pos?: any) => t.to(tg, swap(origins, tg, v), pos),
      fromTo: (tg: any, a: any, b: any, pos?: any) => t.fromTo(tg, swap(origins, tg, a), swap(origins, tg, b), pos),
      set: (tg: any, v: any, pos?: any) => t.set(tg, swap(origins, tg, v), pos),
    };
    try {
      new Function("tl", "gsap", code)(wrap, gsap);
    } catch (e) {
      console.error("IllusScene", bundle.scene, e);
    }
    tl.current = t;
    return () => { t.kill(); tl.current = null; };
  }, [html, bundle.js.join("\n")]);
  useLayoutEffect(() => {
    tl.current?.seek(frame / fps, false);
  }, [frame, fps]);
  return (
    <div className={`sc sc-${bundle.prefix}`} style={{ position: "absolute", ...style }}>
      <style>{bundle.css}</style>
      <div ref={ref} style={{ width: "100%", height: "100%" }} />
    </div>
  );
};
