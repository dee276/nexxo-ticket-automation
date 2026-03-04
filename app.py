from flask import Flask, request, jsonify, render_template
from db import init_db, insert_ticket, list_tickets, get_conn
from rules import classify_ticket

app = Flask(__name__)

@app.get("/")
def home():
    return render_template("index.html")


@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/tickets")
def create_ticket():
    payload = request.get_json(force=True) or {}
    subject = (payload.get("subject") or "").strip()
    body = (payload.get("body") or "").strip()
    source = (payload.get("source") or "email").strip()

    if not subject or not body:
        return jsonify({"error": "subject and body are required"}), 400

    classification = classify_ticket(subject, body)
    ticket_id = insert_ticket(
        source=source,
        subject=subject,
        body=body,
        category=classification.category,
        priority=classification.priority,
        confidence=float(classification.confidence),
        routed_to=classification.routed_to,
    )

    return jsonify({
        "id": ticket_id,
        "category": classification.category,
        "priority": classification.priority,
        "confidence": classification.confidence,
        "routed_to": classification.routed_to
    }), 201

@app.get("/tickets")
def get_tickets():
    limit = int(request.args.get("limit", 50))
    return jsonify(list_tickets(limit=limit))


@app.get("/stats")
def stats():
    with get_conn() as conn:
        by_category = conn.execute("""
            SELECT category, COUNT(*) AS count
            FROM tickets
            GROUP BY category
            ORDER BY count DESC;
        """).fetchall()

        by_priority = conn.execute("""
            SELECT priority, COUNT(*) AS count
            FROM tickets
            GROUP BY priority
            ORDER BY count DESC;
        """).fetchall()

        total = conn.execute("SELECT COUNT(*) AS count FROM tickets;").fetchone()["count"]

    return jsonify({
        "total": total,
        "by_category": [dict(r) for r in by_category],
        "by_priority": [dict(r) for r in by_priority],
    })


if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)