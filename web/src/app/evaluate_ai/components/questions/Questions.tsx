"use client";
import { EVALUATE_AI } from "@/app/DummyData";
import AppContext from "@/contexts/AppContext";
import { TiTickOutline } from "react-icons/ti";
import { AiOutlineClose } from "react-icons/ai";
import React, { useEffect, useContext } from "react";
import useGetLLMResponse from "@/hooks/useGetLLMResponse";
import LoadingComponent from "@/components/Loading/Loading";
import Result from "@/app/evaluate_ai/components/result/Result";
import classes from "@/app/evaluate_ai/components/questions/Questions.module.css";

const Questions = () => {
  const {
    evaluateAiQuestions,
    onEvaluateAiQuestions,
    isevaluateAiAnswereCorrect,
    onEvaluateAiAnswerCorrect,
    isQuizCompleted,
    onQuizCompleted,
    quizResult,
    onQuizResult,
  } = useContext(AppContext);
  const { getLLMResponse, loading: get_loading } = useGetLLMResponse();

  useEffect(() => {
    const fetchData = async () => {
      if (evaluateAiQuestions.length > 0) return;
      const response = await getLLMResponse("evaluate_ai/");
      if (response) onEvaluateAiQuestions(response);
      else {
        onEvaluateAiQuestions(EVALUATE_AI);
      }
    };
    if (typeof window !== "undefined") fetchData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleAnswerChange = (questionId: string, optionValue: string, type: "text" | "single" | "multi") => {
    onEvaluateAiAnswerCorrect(questionId, optionValue);
  };

  useEffect(() => {
    const totalMarked = isevaluateAiAnswereCorrect.filter(
      a => a.selectedOption === true || a.selectedOption === false
    ).length;
    const correctAnswers = isevaluateAiAnswereCorrect.filter(a => a.selectedOption === true).length;
    if (totalMarked === evaluateAiQuestions.length && correctAnswers > 0) {
      onQuizResult({
        "Total Questions": `${evaluateAiQuestions.length}`,
        "Correct Answers": `${correctAnswers}`,
        "Incorrect Answers": `${evaluateAiQuestions.length - correctAnswers}`,
      });
      setTimeout(() => {
        if (isQuizCompleted === false) onQuizCompleted(true);
      }, 1000);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isevaluateAiAnswereCorrect, evaluateAiQuestions]);

  if (get_loading) {
    return <LoadingComponent height="70vh" />;
  }

  if (evaluateAiQuestions.length === 0) {
    return (
      <div
        className={classes["quiz-container"]}
        style={{
          height: "auto",
        }}
      >
        <p>No questions available. Please contact the administrator for more information.</p>
      </div>
    );
  }

  return (
    <div className={classes["quiz-container"]}>
      {evaluateAiQuestions.map((q, index) => (
        <div key={index} className={classes["question"]}>
          <h2>
            {index + 1}. {q.question}
          </h2>
          <div className={classes["is-correct"]}>
            {isevaluateAiAnswereCorrect[index].selectedOption == true && <TiTickOutline color="green" size="1.5em" />}
            {isevaluateAiAnswereCorrect[index].selectedOption == false && <AiOutlineClose color="red" size="1.5em" />}
          </div>
          {q.type === "text" && (
            <input
              type="text"
              id={`q${index}-option`}
              name={`question-${index}`}
              onChange={e => handleAnswerChange(q.id, e.target.value, q.type)}
            />
          )}
          {q.type === "single" &&
            q.options?.map(option => (
              <div key={option}>
                <input
                  type="radio"
                  id={`q${index}-option${option}`}
                  name={`question-${index}`}
                  value={option}
                  onChange={e => handleAnswerChange(q.id, e.target.value, q.type)}
                />
                <label htmlFor={`q${index}-option${option}`}>{option}</label>
              </div>
            ))}
          {q.type === "multi" &&
            q.options?.map(option => (
              <div key={option}>
                <input
                  type="checkbox"
                  id={`q${index}-option${option}`}
                  name={`question-${index}`}
                  value={option}
                  onChange={e => handleAnswerChange(q.id, e.target.value, q.type)}
                />
                <label htmlFor={`q${index}-option${option}`}>{option}</label>
              </div>
            ))}
        </div>
      ))}
      {isQuizCompleted && (
        <Result
          heading="Test Result 🎉"
          data={quizResult}
          onClose={() => {
            onQuizCompleted(false);
          }}
        />
      )}
    </div>
  );
};

export default Questions;
