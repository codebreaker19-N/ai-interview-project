import { useEffect, useRef, useState } from "react";

function VoiceInput({ value, onChange }) {
  const recognitionRef = useRef(null);

  const [isListening, setIsListening] = useState(false);
  const [supported, setSupported] = useState(true);

  useEffect(() => {
    const SpeechRecognition =
      window.SpeechRecognition ||
      window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      setSupported(false);
      return;
    }

    const recognition = new SpeechRecognition();

    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    recognition.onresult = (event) => {
      let finalTranscript = "";

      for (
        let i = event.resultIndex;
        i < event.results.length;
        i++
      ) {
        const transcript =
          event.results[i][0].transcript;

        if (event.results[i].isFinal) {
          finalTranscript += transcript + " ";
        }
      }

      if (finalTranscript.trim()) {
        onChange(
          `${value || ""} ${finalTranscript}`.trim()
        );
      }
    };

    recognition.onerror = () => {
      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognitionRef.current = recognition;

    return () => {
      recognition.stop();
    };
  }, []);

  const startListening = () => {
    if (!recognitionRef.current) return;

    try {
      recognitionRef.current.start();
      setIsListening(true);
    } catch {
      setIsListening(false);
    }
  };

  const stopListening = () => {
    if (!recognitionRef.current) return;

    recognitionRef.current.stop();
    setIsListening(false);
  };

  if (!supported) {
    return (
      <div>
        Voice input is not supported in this browser.
      </div>
    );
  }

  return (
    <div>
      <button
        type="button"
        onClick={
          isListening
            ? stopListening
            : startListening
        }
      >
        {isListening
          ? "⏹ Stop Recording"
          : "🎙️ Start Recording"}
      </button>
    </div>
  );
}

export default VoiceInput;