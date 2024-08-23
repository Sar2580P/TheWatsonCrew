import React from "react";
import classes from "@/app/blog_ai/components/externalReferences/ExternalReferences.module.css";

const ExternalReferences = ({ externalReferences }: any) => {
  return (
    <div className={classes["container"]}>
      <h1>External References</h1>
      <div className={classes["external__references_box"]}>
        {Object.keys(externalReferences).map((key, index) => (
          <a key={index} href={externalReferences[key]} target="_blank" rel="noreferrer">
            {key}
          </a>
        ))}
      </div>
    </div>
  );
};

export default ExternalReferences;
