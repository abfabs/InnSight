import { useEffect, useMemo, useRef, useState } from "react";
import { sendChatMessage } from "../api/chat";
import ChatMessage from "./ChatMessage";

export default function ChatPanel({ defaultCity = null, onResetRef = null }) {
    const storageKey = useMemo(() => {
        return defaultCity
            ? `innsight_chat_state_city_${String(defaultCity).toLowerCase()}`
            : "innsight_chat_state_landing";
    }, [defaultCity]);

    const endRef = useRef(null);
    const inputRef = useRef(null);

    const defaultGreeting = useMemo(
        () => [
            {
                role: "assistant",
                content:
                    "Hey! 😊 I'm **InnSight**, your travel assistant. I cover Amsterdam, Bordeaux, Crete, Lisbon, Rome, and Sicily — ask me anything!",
            },
        ],
        []
    );

    const [messages, setMessages] = useState(() => {
        try {
            const saved = JSON.parse(localStorage.getItem(storageKey) || "null");
            if (saved?.messages?.length) return saved.messages;
        } catch { }
        return defaultGreeting;
    });

    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);

    const [context, setContext] = useState(() => {
        try {
            const saved = JSON.parse(localStorage.getItem(storageKey) || "null");
            return saved?.context || {};
        } catch {
            return {};
        }
    });

    const [city, setCity] = useState(() => {
        try {
            const saved = JSON.parse(localStorage.getItem(storageKey) || "null");
            return saved?.city ?? defaultCity ?? null;
        } catch {
            return defaultCity ?? null;
        }
    });

    const [month, setMonth] = useState(() => {
        try {
            const saved = JSON.parse(localStorage.getItem(storageKey) || "null");
            return saved?.month ?? null;
        } catch {
            return null;
        }
    });

    // ✅ Reset function (exposed to parent via ref)
    function resetChat() {
        try {
            localStorage.removeItem(storageKey);
        } catch { }

        setMessages(defaultGreeting);
        setContext({});
        setMonth(null);

        // keep city on city pages, clear it on landing
        setCity(defaultCity ?? null);

        setInput("");
        setLoading(false);

        setTimeout(() => inputRef.current?.focus(), 0);
    }

    // ✅ Register resetChat in the ref so Header/App can call it
    useEffect(() => {
        if (onResetRef && typeof onResetRef === "object") {
            onResetRef.current = resetChat;
            return () => {
                // only clear if we're the one who set it
                if (onResetRef.current === resetChat) onResetRef.current = null;
            };
        }
    }, [onResetRef, storageKey, defaultCity, defaultGreeting]);

    // If storageKey changes (Landing <-> City page), load the other conversation
    useEffect(() => {
        try {
            const saved = JSON.parse(localStorage.getItem(storageKey) || "null");

            setMessages(saved?.messages?.length ? saved.messages : defaultGreeting);
            setContext(saved?.context || {});
            setCity(saved?.city ?? defaultCity ?? null);
            setMonth(saved?.month ?? null);
        } catch {
            setMessages(defaultGreeting);
            setContext({});
            setCity(defaultCity ?? null);
            setMonth(null);
        }

        setTimeout(() => inputRef.current?.focus(), 0);
    }, [storageKey, defaultCity, defaultGreeting]);

    // Persist chat state so it survives refresh
    useEffect(() => {
        try {
            localStorage.setItem(
                storageKey,
                JSON.stringify({ messages, context, city, month })
            );
        } catch { }
    }, [storageKey, messages, context, city, month]);

    // Scroll to bottom
    useEffect(() => {
        endRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages, loading]);

    // Auto-focus input
    useEffect(() => {
        inputRef.current?.focus();
    }, []);

    useEffect(() => {
        if (!loading) inputRef.current?.focus();
    }, [loading]);

    async function onSend() {
        if (loading) return;

        const text = input.trim();
        if (!text) {
            inputRef.current?.focus();
            return;
        }

        const updatedMessages = [...messages, { role: "user", content: text }];
        setMessages(updatedMessages);
        setInput("");
        setLoading(true);
        setTimeout(() => inputRef.current?.focus(), 0);

        // Build history from the last 8 turns (exclude the default greeting)
        const historyForApi = updatedMessages
            .filter((m) => m.role === "user" || m.role === "assistant")
            .slice(-8)
            .map(({ role, content }) => ({ role, content }));

        try {
            const res = await sendChatMessage({
                message: text,
                city,
                month,
                context,
                fallback: "last_year",
                history: historyForApi,
            });

            const reply = res?.reply ?? "Hmm, something went wrong.";
            setMessages((prev) => [...prev, { role: "assistant", content: reply }]);

            if (res?.context) setContext(res.context);
            if (res?.city) setCity(res.city);
            if (res?.month) setMonth(res.month);
        } catch (err) {
            setMessages((prev) => [
                ...prev,
                {
                    role: "assistant",
                    content: `Request failed: ${String(err?.message || err)}`,
                },
            ]);
        } finally {
            setLoading(false);
            setTimeout(() => inputRef.current?.focus(), 0);
        }
    }

    return (
        <div className="chat-card">
            <div className="chat-header">
                <div className="chat-title">InnSight</div>
                <div className="chat-subtitle">
                    {city ? <span className="chat-chip">{city}</span> : null}
                    {month ? <span className="chat-chip">{month}</span> : null}
                </div>
            </div>

            <div className="chat-body">
                {messages.map((m, i) => (
                    <ChatMessage key={i} role={m.role} content={m.content} />
                ))}
                {loading && <ChatMessage role="assistant" content="Thinking…" />}
                <div ref={endRef} />
            </div>

            <div className="chat-input-row">
                <input
                    ref={inputRef}
                    className="chat-input"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Type anything…"
                    onKeyDown={(e) => e.key === "Enter" && onSend()}
                    disabled={loading}
                    autoFocus
                />
                <button className="chat-send" onClick={onSend} disabled={loading}>
                    Send
                </button>
            </div>
        </div>
    );
}
