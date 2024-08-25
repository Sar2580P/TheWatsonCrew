"use client";
import Image from "next/image";
import Markdown from "react-markdown";
import React, { useEffect, useState } from "react";
import classes from "@/app/watch_ai/components/videoSnap/VideoSnap.module.css";

interface VideoSnapProps {
  heading: string;
  imgs: string[];
  content: string;
  onEnd: () => void;
}

const VideoSnap: React.FC<VideoSnapProps> = ({ heading, imgs, content, onEnd }) => {
  const [currentCharIndex, setCurrentCharIndex] = useState<number | null>(null);
  const [currentCharLength, setCurrentCharLength] = useState<number | null>(null);
  const [isPaused, setIsPaused] = useState(false);
  const [utterance, setUtterance] = useState<SpeechSynthesisUtterance | null>(null);
  const [rate, setRate] = useState(1);

  useEffect(() => {
    const utterance = new SpeechSynthesisUtterance(content);
    utterance.lang = "en-IN";
    utterance.pitch = 2;
    utterance.rate = rate;
    utterance.volume = 1;
    utterance.onboundary = event => {
      setCurrentCharIndex(event.charIndex);
      setCurrentCharLength(event.charLength);
    };
    utterance.onerror = event => {
      console.error("onerror event", event);
    };
    utterance.onend = () => {
      setCurrentCharIndex(null);
      setCurrentCharLength(null);
      onEnd();
    };
    setUtterance(utterance);
    return () => {
      speechSynthesis.cancel();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [content, onEnd]);

  const handleRateChange = (event: any) => {
    const newRate = parseFloat(event.target.value);
    setRate(newRate);
  };

  const playSpeech = () => {
    if (utterance) {
      speechSynthesis.speak(utterance);
      setIsPaused(false);
    }
  };
  const pauseSpeech = () => {
    speechSynthesis.pause();
    setIsPaused(true);
  };
  const resumeSpeech = () => {
    speechSynthesis.resume();
    setIsPaused(false);
  };

  const renderTextWithHighlight = () => {
    if (currentCharIndex !== null && currentCharLength !== null) {
      const before = content.substring(0, currentCharIndex);
      const highlighted = content.substring(currentCharIndex, currentCharIndex + currentCharLength);
      const after = content.substring(currentCharIndex + currentCharLength);

      return (
        <>
          <Markdown>{before}</Markdown>
          <span> {highlighted} </span>
          <Markdown>{after}</Markdown>
        </>
      );
    }
    return <Markdown>{content}</Markdown>;
  };

  return (
    <div className={classes["container"]}>
      <div className={classes["images"]}>
        {imgs.map((img, index) => (
          <Image key={index} src="/robot.jpg" alt={img} width={280} height={180} loader={({ src }) => img} />
        ))}
      </div>
      <div className={classes["video-container"]}>
        <h2>{heading}</h2>
        <video autoPlay loop muted playsInline src="/video.mp4"></video>
        <div className={classes["lower-background"]}></div>
        <div className={classes["desc"]}>{renderTextWithHighlight()}</div>
        <div className={classes.controls}>
          {!isPaused && typeof window !== "undefined" && window.speechSynthesis && !speechSynthesis.speaking && (
            <div className={classes["rate-slider"]}>
              <label htmlFor="rateSlider">speed: {rate}</label>
              <input
                type="range"
                id="rateSlider"
                min="0.5"
                max="2"
                step="0.1"
                value={rate}
                onChange={handleRateChange}
                className={classes.rateSlider}
              />
            </div>
          )}
          {!isPaused && typeof window !== "undefined" && window.speechSynthesis && !speechSynthesis.speaking && (
            <button onClick={playSpeech}>Play</button>
          )}
          {!isPaused && typeof window !== "undefined" && window.speechSynthesis && speechSynthesis.speaking && (
            <button onClick={pauseSpeech}>Pause</button>
          )}
          {isPaused && <button onClick={resumeSpeech}>Resume</button>}
        </div>
      </div>
    </div>
  );
};

export default VideoSnap;
