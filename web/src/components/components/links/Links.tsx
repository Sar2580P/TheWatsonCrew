"use client";
import classes from "@/components/components/links/Links.module.css";
import Link from "@/components/components/link/Link";
import React, { useContext } from "react";
import Button from "@/reusables/Button/Button";
import AppContext from "@/contexts/AppContext";
import usePostLLMResponse from "@/hooks/usePostLLMResponse";

const Links = () => {
  const { links } = useContext(AppContext);
  const { postLLMResponse, loading } = usePostLLMResponse();
  const handleSubmit = async () => {
    const response = await postLLMResponse({ links: links }, "link_knowledge_base/");
  };

  return (
    <div className={classes["container"]}>
      {links.map((link, index) => (
        <Link key={index} link={link} index={index + 1} />
      ))}
      {links.length > 0 ? <Button onClick={handleSubmit} text="Update AI knowledge" bottom="1rem" /> : null}
    </div>
  );
};

export default Links;
