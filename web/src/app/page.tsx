import classes from "@/styles/page.module.css";
import Links from "@/components/components/links/Links";
import AddLink from "@/components/components/addLink/AddLink";

export default function Home() {
  return (
    <div className={classes.container}>
      <div className={classes.box}>
        <h1>
          AI-driven app with smart navigation, interactive chatbot, insightful videos, and personalized assessments.
        </h1>
        <div className={classes["paragraph"]}>
          <p>
            The Learning App is designed to provide a personalized educational experience. Users can input links to
            resources they want to learn from, and the LLM will update its knowledge base accordingly. The app offers
            various features, including reading generated pages, learning through video lectures, taking tests, and
            chatting with the AI.
          </p>
          <AddLink />
        </div>
        <Links />
      </div>
    </div>
  );
}
