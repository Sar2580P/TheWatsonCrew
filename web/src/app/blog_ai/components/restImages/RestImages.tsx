import React from "react";
import Image from "next/image";
import classes from "@/app/blog_ai/components/restImages/RestImages.module.css";

const RestImages = ({ restImages }: { restImages: string[] }) => {
  return (
    <div className={classes["container"]}>
      <h1>Blog All Images</h1>
      <div className={classes["box__images"]}>
        {restImages.map((img, index) => (
          <Image key={index} src={"/robot.jpg"} alt="blog" width={240} height={135} loader={({ src }) => img} />
        ))}
      </div>
    </div>
  );
};

export default RestImages;
