"use client";
import { BLOG_AI } from "@/app/DummyData";
import AppContext from "@/contexts/AppContext";
import classes from "@/styles/blog_ai.module.css";
import React, { useEffect, useContext } from "react";
import Blog from "@/app/blog_ai/components/blog/Blog";
import useGetLLMResponse from "@/hooks/useGetLLMResponse";
import LoadingComponent from "@/components/Loading/Loading";

export default function Blogs() {
  const { blogs, setBlogsHandler } = useContext(AppContext);
  const { getLLMResponse, loading } = useGetLLMResponse();

  useEffect(() => {
    const fetchData = async () => {
      const response = await getLLMResponse("blogs_ai/");
      if (response) setBlogsHandler(response);
      else setBlogsHandler(BLOG_AI);
    };
    if (typeof window !== "undefined") fetchData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className={classes.container}>
      <div className={classes.box}>
        {loading ? <LoadingComponent /> : blogs.map((blog, index) => <Blog key={index} blog={blog} index={index} />)}
      </div>
    </div>
  );
}
