import classes from "@/styles/watch_ai.module.css";
import VideoSnaps from "@/app/watch_ai/components/videoSnaps/VideoSnaps";

export default function Watch() {
  return (
    <div className={classes.container}>
      <div className={classes.box}>
        <VideoSnaps />
      </div>
    </div>
  );
}
