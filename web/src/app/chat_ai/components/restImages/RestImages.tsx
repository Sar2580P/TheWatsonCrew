import React from "react";
import Image from "next/image";
import classes from "@/app/chat_ai/components/restImages/RestImages.module.css";

const urlRegex = new RegExp("^(http|https)://[^\\s/$.?#].[^\\s]*$", "i");

const RestImages = ({ restImages }: { restImages: string[] }) => {
  restImages = restImages.filter(img => urlRegex.test(img));

  return (
    <div className={classes["container"]}>
      <h1 className={classes["heading"]}>All Images</h1>
      <div className={classes["box__images"]}>
        {restImages.map((img, index) => (
          <Image key={index} src={"/robot.jpg"} alt="blog" width={240} height={135} loader={({ src }) => img} />
        ))}
      </div>
    </div>
  );
};

export default RestImages;
