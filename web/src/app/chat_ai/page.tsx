import classes from "@/styles/chat_ai.module.css";
import Chat from "@/app/chat_ai/components/chat/Chat";

export default function ChatAI() {
  return (
    <div className={classes.container}>
      <div className={classes.box}>
        <Chat />
      </div>
    </div>
  );
}
