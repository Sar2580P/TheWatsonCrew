import classes from "@/reusables/Loader/Loader.module.css";

const Loader = ({ text }: { text: string }) => {
  return (
    <div className={classes["container"]}>
      <div className={classes["box"]}></div>
      <div className={classes["loading-box"]}>
        <div className={classes["pl"]}>
          <div className={classes["pl__dot"]}></div>
          <div className={classes["pl__dot"]}></div>
          <div className={classes["pl__dot"]}></div>
          <div className={classes["pl__dot"]}></div>
          <div className={classes["pl__dot"]}></div>
          <div className={classes["pl__dot"]}></div>
          <div className={classes["pl__dot"]}></div>
          <div className={classes["pl__dot"]}></div>
          <div className={classes["pl__dot"]}></div>
          <div className={classes["pl__dot"]}></div>
          <div className={classes["pl__dot"]}></div>
          <div className={classes["pl__dot"]}></div>
          <div className={classes["pl__text"]}>{text}</div>
        </div>
      </div>
    </div>
  );
};

export default Loader;
