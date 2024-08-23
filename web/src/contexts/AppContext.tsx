"use client";
import React, { useState, useEffect } from "react";
import { useNotification } from "@/hooks/useNotification";

interface blog_ai {
  id: string;
  text: string;
  external_references: {};
  sources: string[];
  imgs: string[];
}

type AppContextType = {
  link: string;
  setLink: (link: string) => void;
  links: string[];
  setLinksHandler: (link: string) => void;
  onDeleteLinkHandler: (link: string) => void;

  blogs: blog_ai[];
  setBlogsHandler: (blogs: blog_ai[]) => void;
};

const AppContext = React.createContext<AppContextType>({
  link: "",
  setLink: () => {},
  links: [],
  setLinksHandler: () => {},
  onDeleteLinkHandler: () => {},

  blogs: [],
  setBlogsHandler: () => {},
});

type Props = {
  children: React.ReactNode;
};

export const AppContextProvider: React.FC<Props> = props => {
  const { NotificationHandler } = useNotification();

  // CODE HOME AI HUB OR HOME PAGE
  const [link, setLink] = useState("");
  const [links, setLinks] = useState<string[]>([]);
  const setLinksHandler = (link: string) => {
    const urlRegex = new RegExp("^(http|https)://[^\\s/$.?#].[^\\s]*$", "i");
    if (urlRegex.test(link)) {
      setLinks(prev => [...prev, link]);
      localStorage.setItem("the_watson_crew_links", JSON.stringify([...links, link]));
      setLink("");
    } else {
      NotificationHandler("The Watson Crew", "Please enter a valid link", "Error");
    }
  };
  const onDeleteLinkHandler = (link: string) => {
    setLinks(prev => prev.filter(note => note !== link));
    localStorage.setItem("the_watson_crew_links", JSON.stringify(links.filter(note => note !== link)));
  };

  // CODE BLOG AI HUB OR BLOG PAGE
  const [blogs, setBlogs] = useState<blog_ai[]>([]);
  const setBlogsHandler = (blogs: blog_ai[]) => {
    setBlogs(blogs);
    if (typeof window !== "undefined") {
      localStorage.setItem("the_watson_crew_blogs", JSON.stringify(blogs));
    }
  };

  useEffect(() => {
    const loadLinks = () => {
      if (typeof window !== "undefined") {
        const savedLinks = localStorage.getItem("the_watson_crew_links");
        if (savedLinks) {
          setLinks(JSON.parse(savedLinks));
        }
      }

      if (typeof window !== "undefined") {
        const savedBlogs = localStorage.getItem("the_watson_crew_blogs");
        if (savedBlogs) {
          setBlogs(JSON.parse(savedBlogs));
        }
      }
    };
    loadLinks();
  }, []);

  return (
    <AppContext.Provider
      value={{
        link,
        setLink,
        links,
        setLinksHandler,
        onDeleteLinkHandler,

        blogs,
        setBlogsHandler,
      }}
    >
      {props.children}
    </AppContext.Provider>
  );
};

export default AppContext;
