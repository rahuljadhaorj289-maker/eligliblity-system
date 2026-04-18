from flask import Flask, request, render_template_string
import json, os, random, string

app = Flask(__name__)
FILE_NAME = "data.json"

# ---------- LOAD ----------
def load_data():
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r") as f:
            return json.load(f)
    return {}

# ---------- SAVE ----------
def save_data(data):
    with open(FILE_NAME, "w") as f:
        json.dump(data, f, indent=4)

# ---------- KEY ----------
def generate_key():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# ---------- COMMON STYLE ----------
STYLE = """
<style>
body {
    font-family: 'Segoe UI', sans-serif;
    background: linear-gradient(135deg, #667eea, #764ba2);
    margin: 0;
}
.container {
    width: 420px;
    margin: 60px auto;
    background: white;
    padding: 25px;
    border-radius: 15px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
}
h2 { text-align:center; }

input {
    width: 100%;
    padding: 10px;
    margin: 6px 0;
    border-radius: 8px;
    border: 1px solid #ccc;
}
button {
    width: 100%;
    padding: 12px;
    background: linear-gradient(135deg,#667eea,#764ba2);
    border: none;
    color: white;
    border-radius: 10px;
    font-size: 16px;
    cursor: pointer;
    transition: 0.3s;
}
button:hover {
    transform: scale(1.05);
}
a {
    display:block;
    text-align:center;
    margin:10px 0;
    background:#ff7a18;
    color:white;
    padding:10px;
    border-radius:10px;
    text-decoration:none;
}
a:hover { background:#ff5722; }
</style>
"""

# ---------- HOME ----------
@app.route("/")
def home():
    return render_template_string(STYLE + """
    <div class="container">
        <h2>Company Eligibility System</h2>
        <a href="/company">Company Panel</a>
        <a href="/candidate">Candidate Panel</a>
    </div>
    """)

# ---------- COMPANY ----------
@app.route("/company", methods=["GET","POST"])
def company():
    if request.method == "POST":
        db = load_data()

        company = {
            "10th": float(request.form["tenth"]),
            "12th": float(request.form["twelfth"]),
            "grad": float(request.form["grad"]),
            "backlogs": int(request.form["backlogs"]),
            "questions":[]
        }

        n = int(request.form["num"])

        for i in range(1, n+1):
            company["questions"].append({
                "question": request.form[f"q{i}"],
                "correct": request.form[f"a{i}"].lower(),
                "marks": int(request.form[f"m{i}"])
            })

        key = generate_key()
        db[key] = company
        save_data(db)

        return render_template_string(STYLE + f"""
        <div class="container">
            <h2>✅ Company Created</h2>
            <h3>Your Key: {key}</h3>
            <a href="/">Go Home</a>
        </div>
        """)

    return render_template_string(STYLE + """
    <div class="container">
    <h2>Company Setup</h2>

    <form method="POST">
    <input name="tenth" placeholder="10th %">
    <input name="twelfth" placeholder="12th %">
    <input name="grad" placeholder="Graduation %">
    <input name="backlogs" placeholder="Max Backlogs">
    <input name="num" placeholder="Number of Questions">

    <h3>Questions</h3>

    Q1: <input name="q1" placeholder="Question">
    <input name="a1" placeholder="Answer">
    <input name="m1" placeholder="Marks">

    Q2: <input name="q2" placeholder="Question">
    <input name="a2" placeholder="Answer">
    <input name="m2" placeholder="Marks">

    Q3: <input name="q3" placeholder="Question">
    <input name="a3" placeholder="Answer">
    <input name="m3" placeholder="Marks">

    <button type="submit">Create</button>
    </form>
    </div>
    """)

# ---------- ENTER KEY ----------
@app.route("/candidate", methods=["GET","POST"])
def candidate():
    if request.method == "POST":
        key = request.form["key"].upper()
        db = load_data()

        if key not in db:
            return render_template_string(STYLE + """
            <div class="container">
            <h3>❌ Invalid Key</h3>
            <a href="/candidate">Try Again</a>
            </div>
            """)

        company = db[key]

        questions_html = ""
        for i, q in enumerate(company["questions"], start=1):
            questions_html += f"""
            <p><b>{q['question']}</b></p>
            <input name="ans{i}" placeholder="Your Answer">
            """

        return render_template_string(STYLE + f"""
        <div class="container">
        <h2>Candidate Form</h2>

        <form method="POST" action="/submit">
        <input type="hidden" name="key" value="{key}">

        <input name="name" placeholder="Name">
        <input name="tenth" placeholder="10th %">
        <input name="twelfth" placeholder="12th %">
        <input name="grad" placeholder="Graduation %">
        <input name="backlogs" placeholder="Backlogs">

        <h3>Questions</h3>
        {questions_html}

        <button type="submit">Submit</button>
        </form>
        </div>
        """)

    return render_template_string(STYLE + """
    <div class="container">
    <h2>Enter Company Key</h2>
    <form method="POST">
        <input name="key" placeholder="Enter Key">
        <button type="submit">Start Test</button>
    </form>
    </div>
    """)

# ---------- SUBMIT ----------
@app.route("/submit", methods=["POST"])
def submit():
    db = load_data()
    key = request.form["key"]
    company = db[key]

    tenth = float(request.form["tenth"])
    twelfth = float(request.form["twelfth"])
    grad = float(request.form["grad"])
    backlogs = int(request.form["backlogs"])

    academic = (tenth + twelfth + grad) / 3

    score = 0
    total = 0

    for i, q in enumerate(company["questions"], start=1):
        ans = request.form.get(f"ans{i}", "").lower()
        if ans == q["correct"]:
            score += q["marks"]
        total += q["marks"]

    test = (score/total)*100 if total else 0

    eligible = not (
        tenth < company["10th"] or
        twelfth < company["12th"] or
        grad < company["grad"] or
        backlogs > company["backlogs"]
    )

    final = (0.4 * academic) + (0.6 * test)

    status = "Eligible ✅" if eligible and test >= 60 else "Not Eligible ❌"

    return render_template_string(STYLE + f"""
    <div class="container">
    <h2>Final Result</h2>

    <p><b>Academic:</b> {round(academic,2)}%</p>
    <p><b>Test:</b> {round(test,2)}%</p>
    <p><b>Final:</b> {round(final,2)}%</p>

    <h3>{status}</h3>

    <a href="/">Home</a>
    </div>
    """)

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)
