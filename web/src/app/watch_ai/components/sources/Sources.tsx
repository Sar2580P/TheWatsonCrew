import React, { useState } from "react";
import { MdArrowDropDown } from "react-icons/md";
import { MdArrowDropUp } from "react-icons/md";
import classes from "@/app/watch_ai/components/sources/Sources.module.css";

const urlRegex = new RegExp("^(http|https)://[^\\s/$.?#].[^\\s]*$", "i");

const Sources = ({ sources }: { sources: string[] }) => {
  sources = sources.filter(source => urlRegex.test(source));
  const [showAll, setShowAll] = useState(false);

  const toggleShowAll = () => {
    setShowAll(prev => !prev);
  };

  return (
    <div className={classes["container"]}>
      <h1>Sources</h1>
      <div className={classes["sources__links"]}>
        {sources.slice(0, showAll ? sources.length : Math.min(2, sources.length)).map((source, index) => (
          <a key={index} href={source} target="_blank" rel="noreferrer">
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
