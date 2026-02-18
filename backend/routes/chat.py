from flask import Blueprint, request, jsonify
from services.chat_rag import chat_travel_recommendation

chat_bp = Blueprint("chat", __name__)

@chat_bp.post("/api/chat")
def chat():
    # Parse JSON safely
    data = request.get_json(force=True, silent=True) or {}

    message = (data.get("message") or "").strip()
    city = (data.get("city") or "").strip().lower() or None
    month = (data.get("month") or "").strip() or None
    fallback = (data.get("fallback") or "last_year").strip().lower()
    context = data.get("context") or {}
    history = data.get("history") or []

    if not message:
        return jsonify({"error": "Message is required"}), 400

    try:
        result = chat_travel_recommendation(
            message=message,
            city=city,
            month=month,
            fallback=fallback,
            context=context,
            history=history,
        )
    except TypeError as e:
        # Helps you immediately see signature mismatches
        return jsonify({
            "error": "chat_travel_recommendation() signature mismatch",
            "details": str(e),
        }), 500
    except Exception as e:
        return jsonify({
            "error": "Chat service failed",
            "details": str(e),
        }), 500

    # Allow simple or structured responses
    if isinstance(result, str):
        return jsonify({"reply": result})

    # Expected structured shape:
    # {
    #   reply: "...",
    #   needs?: ["month", "city"],
    #   context?: {...}
    # }
    return jsonify(result)
