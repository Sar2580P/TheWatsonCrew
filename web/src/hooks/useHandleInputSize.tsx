import { useRef } from "react";

const useHandleInputSize = () => {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const handleInput = () => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = "auto";
      textarea.style.height = textarea.scrollHeight + "px";
    }
  };

  return { textareaRef, handleInput };
};

export default useHandleInputSize;
