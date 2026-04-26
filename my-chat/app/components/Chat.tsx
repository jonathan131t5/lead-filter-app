"use client";

import { useEffect, useState } from "react";

type Msg = {
  role: "user" | "assistant";
  content: string;
};

export default function Chat() {
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");

  useEffect(() => {
    setMessages([
      {
        role: "assistant",
        content: "👋 הכנס טלפון כדי להתחיל",
      },
    ]);
  }, []);

  const send = async () => {
    if (!input.trim()) return;

    const userMessage: Msg = {
      role: "user",
      content: input,
    };

    const updatedMessages = [...messages, userMessage];

    setMessages(updatedMessages);
    setInput("");

    const res = await fetch("http://localhost:8000/message", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        phone_number: input,
        name: null,
        content: input,
      }),
    });

    const data = await res.json();

    setMessages((prev) => [
      ...prev,
      { role: "assistant", content: data.content },
    ]);
  };

  return (
    <div>
      <div>
        {messages.map((m, i) => (
          <div key={i}>{m.content}</div>
        ))}
      </div>

      <input
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="כתוב כאן..."
      />

      <button onClick={send}>שלח</button>
    </div>
  );
}