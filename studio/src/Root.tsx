import { Composition } from "remotion";
import { Video, Plan } from "./Video";
import { Thumb } from "./Thumb";

const EMPTY: Plan = {
  format: "short", width: 1080, height: 1920, fps: 30, total: 30,
  look: { accent: "#22D3EE", ink: "#F8FAFC", background: "#0A0F1E", font: "Manrope" },
  captionsComponent: null, beats: [], audio: "",
};

export const RemotionRoot = () => (
  <>
  <Composition
    id="Video"
    component={Video as any}
    durationInFrames={30}
    fps={30}
    width={1080}
    height={1920}
    defaultProps={{ plan: EMPTY }}
    calculateMetadata={({ props }: any) => ({
      durationInFrames: Math.max(1, props.plan.total),
      width: props.plan.width,
      height: props.plan.height,
      fps: props.plan.fps,
    })}
  />
  <Composition
    id="Thumb"
    component={Thumb as any}
    durationInFrames={1}
    fps={30}
    width={1280}
    height={720}
    defaultProps={{ plan: EMPTY, beat: 0, frame: 0, text: "", layout: "left", w: 1280, h: 720 }}
    calculateMetadata={({ props }: any) => ({ width: props.w ?? 1280, height: props.h ?? 720,
      durationInFrames: Math.max(1, props.plan.beats[props.beat]?.frames ?? 1) })}
  />
  </>
);
