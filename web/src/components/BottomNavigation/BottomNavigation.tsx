import React from "react";
import classes from "@/components/BottomNavigation/bottomNavigation.module.css";
import Link from "next/link";

interface BottomNavigationItem {
  left: {
    name: string;
    link: string;
    display: string;
  };
  right: {
    name: string;
    link: string;
    display: string;
  };
}

const BottomNavigation = ({ left, right }: BottomNavigationItem) => {
  return (
    <div className={classes.bottomNavigation}>
      <div className={classes.left}>
        <Link
          href={left.link}
          style={{
            display: left.display,
          }}
        >
          <span> {left.name}</span>
          <i></i>
        </Link>
      </div>
      <div className={classes.right}>
        <Link
          href={right.link}
          style={{
            display: right.display,
          }}
        >
          <span> {right.name}</span>
          <i></i>
        </Link>
      </div>
    </div>
  );
};

export default BottomNavigation;
