import React from "react";
import Image from "next/image";
import classes from "@/app/blog_ai/components/restImages/RestImages.module.css";

const urlRegex = new RegExp("^(http|https)://[^\\s/$.?#].[^\\s]*$", "i");

const RestImages = ({ restImages }: { restImages: string[] }) => {
  restImages = restImages.filter(img => urlRegex.test(img));

  return (
    <div className={classes["container"]}>
      <h1>Blog All Images</h1>
      <div
        className={classes["box__images"]}
        style={{ "--length": `${restImages.length}`, "--width": "240px", "--height": "135px" } as React.CSSProperties}
      >
        {restImages.map((img, index) => (
          <Image
            key={index}
            src={"/robot.jpg"}
            alt="blog"
            width={240}
            height={135}
            loader={({ src }) => img}
            style={
              {
                "--index": index,
              } as React.CSSProperties
            }
          />
        ))}
      </div>
    </div>
  );
};

export default RestImages;
