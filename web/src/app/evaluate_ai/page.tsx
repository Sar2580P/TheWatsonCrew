import classes from "@/styles/evaluate_ai.module.css";
import Questions from "@/app/evaluate_ai/components/questions/Questions";

export default function Evaluate() {
  return (
    <div className={classes.container}>
      <div className={classes.box}>
        <h1>Test Your Knowledge</h1>
        <Questions />
      </div>
    </div>
  );
}
