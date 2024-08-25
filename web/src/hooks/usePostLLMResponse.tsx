"use client";
import { useState } from "react";
import { useNotification } from "./useNotification";

const usePostLLMResponse = () => {
  const { NotificationHandler } = useNotification();
  const [loading, setLoading] = useState(false);

  const postLLMResponse = async (data: any, path: string) => {
    console.log(data);
    try {
      setLoading(true);
      await new Promise(resolve => setTimeout(resolve, 1500));
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/thewatsoncrew/${path}`, {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });
      const responsedata = await response.json();
      console.log(responsedata);
      if (responsedata.response === "Failed") {
        NotificationHandler("The Watson Crew", responsedata.response, "Error");
        setLoading(false);
        return null;
      }
      NotificationHandler("The Watson Crew", "The AI has been updated", "Success");
      setLoading(false);
      return responsedata.response;
    } catch (err) {
      setLoading(false);
      console.log(err);
      // NotificationHandler("The Watson Crew", "Something went wrong", "Error");
      return null;
    }
  };
  return { postLLMResponse, loading };
};

export default usePostLLMResponse;
