"use client";
import React from "react";
import classes from "@/reusables/Button/Button.module.css";

type ButtonProps = {
  onClick: () => void;
  text?: string;
  bottom?: string;
};

const Button: React.FC<ButtonProps> = ({ onClick, text, bottom }) => {
  return (
    <div
      className={classes["container"]}
      style={{
        bottom: bottom,
      }}
    >
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
