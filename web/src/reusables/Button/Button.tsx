"use client";
import React from "react";
import classes from "@/reusables/Button/Button.module.css";

type ButtonProps = {
  onClick: () => void;
  text?: string;
};

const Button: React.FC<ButtonProps> = ({ onClick, text }) => {
  return (
    <div className={classes["container"]}>
      <button className={classes["button"]} onClick={onClick}>
        <span></span>
        <span></span>
        <span></span>
        {text}
      </button>
    </div>
  );
};

export default Button;
