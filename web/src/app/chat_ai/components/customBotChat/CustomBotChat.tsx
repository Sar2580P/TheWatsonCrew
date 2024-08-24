"use client";
import React, { useEffect, useRef } from "react";
import LoadingComponent from "@/components/Loading/Loading";
import ChatItem from "@/app/chat_ai/components/chatItem/ChatItem";
import classes from "@/app/chat_ai/components/customBotChat/CustomBotChat.module.css";

type Chat = {
  data: {
    role: string;
    parts: {
      content: {
        id: string;
        text: string;
        external_references: {};
        sources: string[];
        imgs: string[];
      }[];
    }[];
  }[];
  loading: boolean;
};

const CustomBotChat: React.FC<Chat> = ({ data, loading }) => {
  const chatsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (chatsRef.current) {
      chatsRef.current.scrollTop = chatsRef.current.scrollHeight;
    }
  }, [data]);

  return (
    <div className={classes["container"]}>
      <div className={classes["chats"]} ref={chatsRef}>
        {data.map((chat, index) => (
          <ChatItem key={index} message={chat.parts[0].content} user={chat.role} />
        ))}
        <div className={classes["loading"]}>
          {loading && <LoadingComponent height="auto" size="11px" width="auto" alignItems="flex-start" />}
        </div>
      </div>
    </div>
  );
};

export default CustomBotChat;
