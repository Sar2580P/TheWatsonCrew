"use client";
import React, { useState, useEffect } from "react";
import { useNotification } from "@/hooks/useNotification";

type AppContextType = {
  link: string;
  setLink: (link: string) => void;
  links: string[];
  setLinksHandler: (link: string) => void;
  onDeleteLinkHandler: (link: string) => void;
};

const AppContext = React.createContext<AppContextType>({
  link: "",
  setLink: () => {},
  links: [],
  setLinksHandler: () => {},
  onDeleteLinkHandler: () => {},
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

  useEffect(() => {
    const loadLinks = () => {
      if (typeof window !== "undefined") {
        const savedLinks = localStorage.getItem("the_watson_crew_links");
        if (savedLinks) {
          setLinks(JSON.parse(savedLinks));
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
      }}
    >
      {props.children}
    </AppContext.Provider>
  );
};

export default AppContext;
