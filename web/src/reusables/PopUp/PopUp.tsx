"use client";
import styles from "@/reusables/PopUp/PopUp.module.css";

interface PopupProps {
  heading: string;
  data: Record<string, string>;
  onClose: () => void;
}

const Popup: React.FC<PopupProps> = ({ heading, data, onClose }) => {
  return (
    <div className={styles.overlay}>
      <div className={styles.popup}>
        <h1>
          <strong>{heading}</strong>
        </h1>
        <button className={styles.closeButton} onClick={onClose}>
          &times;
        </button>
        <div className={styles.content}>
          {Object.entries(data).map(([key, value]) => (
            <div key={key} className={styles.item}>
              <span>{key}: </span>
              {value}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Popup;
