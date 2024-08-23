import React from "react";
import Image from "next/image";
import { CiPlay1 } from "react-icons/ci";
import { CiShare2 } from "react-icons/ci";
import { FaRegComment } from "react-icons/fa";
import { CiBookmarkPlus } from "react-icons/ci";
import { PiHandsClappingLight } from "react-icons/pi";
import classes from "@/app/blog_ai/components/appreciation/Appreciation.module.css";

const Appreciation = () => {
  return (
    <div className={classes["container"]}>
      <div className={classes["user"]}>
        <div className={classes["user__image"]}>
          <Image src="/robot.jpg" alt="blog" width={50} height={50} />
        </div>
        <div className={classes["user__name__follow__time"]}>
          <div className={classes["user__name__follow"]}>
            <div className={classes["user__name"]}>The Watson Crew</div>
            <div className={classes["user__follow"]}>Follow</div>
          </div>
          <div className={classes["user__time"]}>
            <div className={classes["user__time__text"]}>7 min read</div>
            <div className={classes["user__time__dot"]}>·</div>
            <div className={classes["user__time__date"]}>
              {new Date().toLocaleDateString("en-US", {
                weekday: "long",
                year: "numeric",
                month: "long",
                day: "numeric",
              })}
            </div>
          </div>
        </div>
      </div>
      <div className={classes["appreciation"]}>
        <div className={classes["appreciation__icons"]}>
          <div className={classes["appreciation__icon"]}>
            <PiHandsClappingLight size={28} /> 83
          </div>
          <div className={classes["appreciation__icon"]}>
            <FaRegComment size={28} /> 5
          </div>
        </div>
        <div className={classes["appreciation__icons"]}>
          <div className={classes["appreciation__icon"]}>
            <CiBookmarkPlus size={28} />
          </div>
          <div className={classes["appreciation__icon"]}>
            <CiPlay1 size={28} />
          </div>
          <div className={classes["appreciation__icon"]}>
            <CiShare2 size={28} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Appreciation;
