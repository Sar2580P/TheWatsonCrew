import React from "react";
import classes from "@/app/watch_ai/components/externalReferences/ExternalReferences.module.css";

const urlRegex = new RegExp("^(http|https)://[^\\s/$.?#].[^\\s]*$", "i");

const ExternalReferences = ({ externalReferences }: any) => {
  const keys = Object.keys(externalReferences)
    .filter(key => urlRegex.test(externalReferences[key]))
    .slice(0, 50);

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
