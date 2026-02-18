const MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
];

export default function MonthPicker({ onPick }) {
    return (
        <div className="chat-month">
            <div className="chat-month-title">When are you traveling?</div>

            <div className="chat-month-grid">
                {MONTHS.map((m) => (
                    <button key={m} className="chat-month-btn" onClick={() => onPick(m)}>
                        {m}
                    </button>
                ))}
            </div>

            <div className="chat-month-hint">
                Pick a month first — then ask for vibes, budget, beach, walkable, etc.
            </div>
        </div>
    );
}
