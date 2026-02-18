import { fetchJSON } from "./client";

export async function sendChatMessage({ message, city, month, fallback = "last_year", context = {}, history = [] }) {
    return fetchJSON("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, city, month, fallback, context, history }),
    });
}
