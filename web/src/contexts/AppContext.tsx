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

interface Question {
  question: string;
  type: "text" | "single" | "multi";
  options?: string[];
  id: string;
  answer: string;
}

type Chat = {
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

interface watch_ai {
  heading: string;
  content: string;
  metadata: {
    external_references: {};
    sources: string[];
    imgs: string[];
  };
}

type AppContextType = {
  link: string;
  setLink: (link: string) => void;
  links: string[];
  setLinksHandler: (link: string) => void;
  onDeleteLinkHandler: (link: string) => void;

  blogs: blog_ai[];
  setBlogsHandler: (blogs: blog_ai[]) => void;

  evaluateAiQuestions: Question[];
  onEvaluateAiQuestions: (questions: Question[]) => void;
  isevaluateAiAnswereCorrect: { id: string; selectedOption: boolean | null }[];
  onEvaluateAiAnswerCorrect: (id: string, selectedOption: string) => void;
  isQuizCompleted: boolean;
  onQuizCompleted: (toggle: boolean) => void;
  quizResult: Record<string, string>;
  onQuizResult: (result: Record<string, string>) => void;

  converseAiChats: Chat;
  onConverseAiChats: (chat: Chat) => void;
  currentQuestion: string;
  setCurrentQuestion: (question: string) => void;

  videoSnaps: watch_ai[];
  onSetVideoSnapsHandler: (videoSnaps: watch_ai[]) => void;
};

const AppContext = React.createContext<AppContextType>({
  link: "",
  setLink: () => {},
  links: [],
  setLinksHandler: () => {},
  onDeleteLinkHandler: () => {},

  blogs: [] as blog_ai[],
  setBlogsHandler: () => {},

  evaluateAiQuestions: [] as Question[],
  onEvaluateAiQuestions: () => {},
  isevaluateAiAnswereCorrect: [],
  onEvaluateAiAnswerCorrect: () => {},
  isQuizCompleted: false,
  onQuizCompleted: () => {},
  quizResult: {},
  onQuizResult: () => {},

  converseAiChats: [] as Chat,
  onConverseAiChats: () => {},
  currentQuestion: "",
  setCurrentQuestion: () => {},

  videoSnaps: [] as watch_ai[],
  onSetVideoSnapsHandler: () => {},
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
  };

  // CODE PERSONALIZED AI ASSESSMENTS PAGE
  const [evaluateAiQuestions, setEvaluateAiQuestions] = useState<Question[]>([]);
  const [isevaluateAiAnswereCorrect, setIsevaluateAiAnswereCorrect] = useState<
    { id: string; selectedOption: boolean | null }[]
  >([]);
  const onEvaluateAiQuestions = (questions: Question[]) => {
    setEvaluateAiQuestions(questions);
    setIsevaluateAiAnswereCorrect(questions.map(question => ({ id: question.id, selectedOption: null })));
  };
  const onEvaluateAiAnswerCorrect = (id: string, selectedOption: string) => {
    const isCorrect = evaluateAiQuestions.find(question => question.id === id)?.answer === selectedOption;
    setIsevaluateAiAnswereCorrect(prev =>
      prev.map(item => (item.id === id ? { ...item, selectedOption: isCorrect } : item))
    );
  };
  const [isQuizCompleted, setIsQuizCompleted] = useState(false);
  const onQuizCompleted = (toggle: boolean) => {
    setIsQuizCompleted(toggle);
  };
  const [quizResult, setQuizResult] = useState<Record<string, string>>({});
  const onQuizResult = (result: Record<string, string>) => {
    setQuizResult(result);
  };

  // CODE INTELLIGENT AI CHATBOT PAGE
  const [converseAiMarkdown, setConverseAiMarkdown] = useState<string[]>([]);
  const onConverseAiMarkdown = (markdown: string[]) => {
    setConverseAiMarkdown(markdown);
  };
  const [converseAiChats, setConverseAiChats] = useState<Chat>([]);
  const onConverseAiChats = (chat: Chat) => {
    setConverseAiChats(prev => [...prev, ...chat]);
  };
  const [currentQuestion, setCurrentQuestion] = useState<string>("");

  // CODE WATCH AI HUB OR WATCH PAGE
  const [videoSnaps, setVideoSnaps] = useState<watch_ai[]>([]);
  const onSetVideoSnapsHandler = (videoSnaps: watch_ai[]) => {
    setVideoSnaps(videoSnaps);
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

        blogs,
        setBlogsHandler,

        evaluateAiQuestions,
        onEvaluateAiQuestions,
        isevaluateAiAnswereCorrect,
        onEvaluateAiAnswerCorrect,
        isQuizCompleted,
        onQuizCompleted,
        quizResult,
        onQuizResult,

        converseAiChats,
        onConverseAiChats,
        currentQuestion,
        setCurrentQuestion,

        videoSnaps,
        onSetVideoSnapsHandler,
      }}
    >
      {props.children}
    </AppContext.Provider>
  );
};

export default AppContext;
