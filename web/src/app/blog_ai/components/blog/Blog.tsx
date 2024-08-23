import React from "react";
import Image from "next/image";
import Markdown from "react-markdown";
import classes from "@/app/blog_ai/components/blog/Blog.module.css";
import Appreciation from "@/app/blog_ai/components/appreciation/Appreciation";
import RestImages from "@/app/blog_ai/components/restImages/RestImages";
import ExternalReferences from "@/app/blog_ai/components/externalReferences/ExternalReferences";
import Sources from "@/app/blog_ai/components/sources/Sources";

interface blog_ai {
  id: string;
  text: string;
  external_references: {};
  sources: string[];
  imgs: string[];
}

interface Props {
  blog: blog_ai;
  index: number;
}

const shadesOfWhite = [
  "#090a11cc",
  "#474748",
  "#444",
  "#333437",
  "#15172a",
  "#2c2e40",
  "#090a11",
  "#000",
  "#090a11",
  "#565872",
];

const Blog = ({ blog, index }: Props) => {
  return (
    <div className={classes["container"]} style={{ backgroundColor: shadesOfWhite[index % 10] }}>
      <div className={classes["blog"]}>
        <Appreciation />
        <Image
          src="/robot.jpg"
          alt="blog"
          width={960}
          height={540}
          loader={({ src }) => {
            if (blog.imgs.length > 0) {
              return blog.imgs[Math.floor(Math.random() * blog.imgs.length)];
            }
            return src;
          }}
        />
        <Markdown>{blog?.text}</Markdown>
        <RestImages restImages={blog.imgs} />
        <ExternalReferences externalReferences={blog.external_references} />
        <Sources sources={blog.sources} />
      </div>
    </div>
  );
};

export default Blog;
