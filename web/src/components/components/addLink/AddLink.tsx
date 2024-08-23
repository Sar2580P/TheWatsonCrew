"use client";
import React, { useContext } from "react";
import { IoMdAdd } from "react-icons/io";
import AppContext from "@/contexts/AppContext";
import classes from "@/components/components/addLink/AddLink.module.css";

const AddLink = () => {
  const { link, setLink, setLinksHandler } = useContext(AppContext);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLinksHandler(link);
  };
  const onChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setLink(e.target.value);
  };

  return (
    <div className={classes["container"]}>
      <div className={classes["box"]}>
        <input placeholder=" " onChange={onChange} id="text" name="text" value={link} />
        <label>
          <span>
            Add a link to a resource you want to learn from, and the LLM will update its knowledge base accordingly
          </span>
        </label>
      </div>
      <button onClick={handleSubmit}>
        <IoMdAdd size={20} />
        &nbsp;
        <span>Add Link</span>
      </button>
    </div>
  );
};

export default AddLink;
