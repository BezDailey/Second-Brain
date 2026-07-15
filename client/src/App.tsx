import { useState, useRef, useEffect } from "react";

type Source = {
  title: string;
  content_snippet: string;
  metadata: Record<string, unknown>;
};

type Message = {
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
};

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [filterField, setFilterField] = useState("title");
  const [filterValue, setFilterValue] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function sendQuestion(e: React.FormEvent) {
    e.preventDefault();
    const question = input.trim();
    if (!question) return;

    const filters = filterValue.trim()
      ? { [filterField]: filterValue.trim() }
      : undefined;

    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("/api/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, filters }),
      });
      if (!res.ok) {
        throw new Error(`Server returned ${res.status}`);
      }
      const data = await res.json();

      const answer =
        !data.answer || data.answer === "Empty Response"
          ? "No matching notes found for that filter."
          : data.answer;
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: answer, sources: data.sources },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Something went wrong reaching the API.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <h1>Second Brain</h1>
      <div>
        {messages.map((m, i) => (
          <div key={i}>
            <p>
              <strong>{m.role === "user" ? "You" : "Assistant"}:</strong>{" "}
              {m.content}
            </p>
            {m.sources && m.sources.length > 0 && (
              <div>
                {m.sources.map((s, j) => (
                  <details key={j}>
                    <summary>{s.title}</summary>
                    <p>{s.content_snippet}</p>
                  </details>
                ))}
              </div>
            )}
          </div>
        ))}
        {loading && <p>Thinking...</p>}
        <div ref={bottomRef} />
      </div>
      <div>
        <label>Filter: </label>
        <select
          value={filterField}
          onChange={(e) => setFilterField(e.target.value)}
        >
          <option value="title">Title</option>
          <option value="tags">Tag</option>
        </select>
        <input
          value={filterValue}
          onChange={(e) => setFilterValue(e.target.value)}
          placeholder="value (optional)"
        />
        <button type="button" onClick={() => setFilterValue("")}>
          Clear
        </button>
      </div>
      <form onSubmit={sendQuestion}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask your notes..."
        />
        <button type="submit" disabled={loading || !input.trim()}>
          Send
        </button>
      </form>
    </main>
  );
}

export default App;
