import path from "path";
import { Config } from "@remotion/cli/config";

Config.setVideoImageFormat("jpeg");
Config.setChromiumOpenGlRenderer("angle");
Config.overrideWebpackConfig((c) => ({
  ...c,
  resolve: {
    ...c.resolve,
    alias: {
      ...(c.resolve?.alias ?? {}),
      "@": path.join(process.cwd(), "src"),
      "@remotion/google-fonts": path.join(process.cwd(), "src", "fontshim"),
    },
  },
}));
