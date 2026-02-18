import { useEffect, useState } from "react";
import ChatPanel from "./ChatPanel";

export default function ChatWidget({ defaultCity = null, onResetRef = null }) {
    const [open, setOpen] = useState(false);

    useEffect(() => {
        const saved = localStorage.getItem("innsight_chat_open");
        if (saved === "1") setOpen(true);
    }, []);

    useEffect(() => {
        localStorage.setItem("innsight_chat_open", open ? "1" : "0");
    }, [open]);

    return (
        <div className="chat-widget">
            <div className={`chat-window ${open ? "is-open" : "is-closed"}`}>
                <div className="chat-window-header">
                    <div className="chat-window-title">InnSight</div>
                    <button
                        type="button"
                        className="chat-window-close"
                        onClick={() => setOpen(false)}
                        aria-label="Close chat"
                    >
                        ✕
                    </button>
                </div>

                <div className="chat-window-body">
                    <ChatPanel defaultCity={defaultCity} onResetRef={onResetRef} />
                </div>
            </div>

            <button
                type="button"
                className="chat-fab"
                onClick={() => setOpen((v) => !v)}
                aria-label={open ? "Close chat" : "Open chat"}
            >
                💬
            </button>
        </div>
    );
}
