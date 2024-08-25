import React from "react";
import Markdown from "react-markdown";
import Sources from "@/app/chat_ai/components/sources/Sources";
import RestImages from "@/app/chat_ai/components/restImages/RestImages";
import classes from "@/app/chat_ai/components/chatItem/ChatItem.module.css";
import ExternalReferences from "@/app/chat_ai/components/externalReferences/ExternalReferences";

type ChatItemProps = {
  message: {
    id: string;
    text: string;
    external_references: {};
    sources: string[];
    imgs: string[];
  }[];
  user: string;
};

const ChatItem: React.FC<ChatItemProps> = ({ message, user }) => {
  return (
    <div
      className={classes["container"]}
      style={{
        alignSelf: user === "bot" ? "flex-end" : "flex-start",
      }}
    >
      <div className={`${classes["message-box"]} ${classes[user]}`}>
        <div className={classes["user-logo"]}>{user.substring(0, 2)}</div>
        <div className={classes["message"]}>
          {message?.map((markdownString, index) => (
            <div
              className={classes["each-markdown"]}
              style={{
                backgroundColor: `hsl(${180 + index * 10}, 6%, 12%)`,
                padding: user === "bot" ? "1rem" : "",
              }}
              key={index}
            >
              <Markdown key={index}>{markdownString.text}</Markdown>
              {user == "bot" && (
                <div className={classes["other-details"]}>
                  {markdownString.imgs.length > 0 && <RestImages restImages={markdownString.imgs} />}
                  {Object.keys(markdownString.external_references).length > 0 && (
                    <ExternalReferences externalReferences={markdownString.external_references} />
                  )}
                  {markdownString.sources.length > 0 && <Sources sources={markdownString.sources} />}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ChatItem;
