"use client";
import { useContext } from "react";
import { MdDelete } from "react-icons/md";
import classes from "@/components/components/link/Link.module.css";
import AppContext from "@/contexts/AppContext";

interface LinksProps {
  index: number;
  link: string;
}

const Links = ({ index, link }: LinksProps) => {
  const { onDeleteLinkHandler } = useContext(AppContext);

  return (
    <div className={classes["container"]}>
      <span>{index}.</span>
      <a href={link} target="_blank" rel="noopener noreferrer">
        {link}
      </a>
      <button onClick={() => onDeleteLinkHandler(link)}>
        <MdDelete size={20} />
        Delete
      </button>
    </div>
  );
};

export default Links;
