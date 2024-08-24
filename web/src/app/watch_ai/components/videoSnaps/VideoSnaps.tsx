"use client";
import { WATCH_AI } from "@/app/DummyData";
import Loader from "@/reusables/Loader/Loader";
import AppContext from "@/contexts/AppContext";
import useGetLLMResponse from "@/hooks/useGetLLMResponse";
import React, { useState, useEffect, useContext } from "react";
import Sources from "@/app/watch_ai/components/sources/Sources";
import VideoSnap from "@/app/watch_ai/components/videoSnap/VideoSnap";
import { MdOutlineNavigateNext, MdOutlineNavigateBefore } from "react-icons/md";
import classes from "@/app/watch_ai/components/videoSnaps/VideoSnaps.module.css";
import ExternalReferences from "@/app/watch_ai/components/externalReferences/ExternalReferences";

interface watch_ai {
  heading: string;
  content: string;
  metadata: {
    external_references: {};
    sources: string[];
    imgs: string[];
  };
}

const VideoSnaps: React.FC = () => {
  const { getLLMResponse, loading } = useGetLLMResponse();
  const [currentVideoSnapIndex, setCurrentVideoSnapIndex] = useState(0);
  const { videoSnaps, onSetVideoSnapsHandler } = useContext(AppContext);

  useEffect(() => {
    const fetchData = async () => {
      if (videoSnaps.length > 0) return;
      const response = await getLLMResponse("watch_ai/");
      if (response) onSetVideoSnapsHandler(response);
      else onSetVideoSnapsHandler(WATCH_AI);
    };
    if (typeof window !== "undefined") fetchData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleEnd = () => {
    if (currentVideoSnapIndex < videoSnaps.length - 1) {
      setCurrentVideoSnapIndex(currentVideoSnapIndex + 1);
    } else {
      setCurrentVideoSnapIndex(0);
    }
  };

  const handleNext = () => {
    setCurrentVideoSnapIndex(prevIndex => (prevIndex + 1) % videoSnaps.length);
  };
  const handlePrev = () => {
    setCurrentVideoSnapIndex(prevIndex => (prevIndex - 1 + videoSnaps.length) % videoSnaps.length);
  };

  if (loading || videoSnaps.length === 0) return <Loader text="Loading..." />;

  const currenVideoSnap = videoSnaps[currentVideoSnapIndex];

  return (
    <div className={classes["container"]}>
      <VideoSnap
        key={currentVideoSnapIndex}
        heading={currenVideoSnap.heading}
        content={currenVideoSnap.content}
        imgs={currenVideoSnap?.metadata.imgs || []}
        onEnd={handleEnd}
      />
      <div className={classes["buttons"]}>
        <button onClick={handlePrev} className={classes["prev-button"]}>
          <MdOutlineNavigateBefore />
        </button>
        <button onClick={handleNext} className={classes["next-button"]}>
          <MdOutlineNavigateNext />
        </button>
      </div>
      <ExternalReferences externalReferences={currenVideoSnap.metadata.external_references} />
      <Sources sources={currenVideoSnap.metadata.sources} />
    </div>
  );
};

export default VideoSnaps;
