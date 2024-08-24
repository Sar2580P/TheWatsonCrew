import React from "react";
import classes from "@/app/watch_ai/components/externalReferences/ExternalReferences.module.css";

const ExternalReferences = ({ externalReferences }: any) => {
  const keys = Object.keys(externalReferences).slice(0, 50);

  return (
    <div className={classes["container"]}>
      <h1>External References</h1>
      <div className={classes["external__references_box"]}>
        {keys.map(
          (key, index) =>
            key && (
              <a key={index} href={externalReferences[key]} target="_blank" rel="noreferrer">
                # {key}
              </a>
            )
        )}
      </div>
    </div>
  );
};

export default ExternalReferences;
