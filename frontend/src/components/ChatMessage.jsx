export default function ChatMessage({ role, content }) {
    return <div className={`chat-bubble ${role}`}>{content}</div>;
}
