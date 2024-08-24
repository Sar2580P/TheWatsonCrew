import React, { useState } from "react";
import { MdArrowDropDown } from "react-icons/md";
import { MdArrowDropUp } from "react-icons/md";
import classes from "@/app/chat_ai/components/sources/Sources.module.css";

const Sources = ({ sources }: { sources: string[] }) => {
  const [showAll, setShowAll] = useState(false);

  const toggleShowAll = () => {
    setShowAll(prev => !prev);
  };

  return (
    <div className={classes["container"]}>
      <h1 className={classes["heading"]}>Sources</h1>
      <div className={classes["sources__links"]}>
        {sources.slice(0, showAll ? sources.length : Math.min(2, sources.length)).map((source, index) => (
          <a
            key={index}
            href={source}
            target="_blank"
            rel="noreferrer"
            style={{
              width: "max-content",
            }}
          >
            {source.substring(0, 50)}...
          </a>
        ))}
        {!showAll && sources.length > 2 && (
          <button onClick={toggleShowAll} className={classes["show-all-button"]}>
            Show All <MdArrowDropDown />
          </button>
        )}
        {showAll && sources.length > 2 && (
          <button onClick={toggleShowAll} className={classes["show-all-button"]}>
            Show Two <MdArrowDropUp />
          </button>
        )}
      </div>
    </div>
  );
};

export default Sources;
