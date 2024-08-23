"use client";
import classes from "@/app/evaluate_ai/components/result/Result.module.css";

interface ResultProps {
  heading: string;
  data: Record<string, string>;
  onClose: () => void;
}

const Result: React.FC<ResultProps> = ({ heading, data, onClose }) => {
  return (
    <div className={classes.overlay}>
      <div className={classes.popup}>
        <h1>
          <strong>{heading}</strong>
        </h1>
        <button className={classes.closeButton} onClick={onClose}>
          &times;
        </button>
        <div className={classes.content}>
          {Object.entries(data).map(([key, value]) => (
            <div key={key} className={classes.item}>
              <span>{key}: </span>
              {value}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Result;
