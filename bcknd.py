from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import json

app = Flask(__name__)

# Load the answer key with QID → Option ID
with open('answer_key.json', 'r') as f:
    answer_key = json.load(f)

def parse_response_sheet(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    questions = []
    rows = soup.find_all("tr")

    for row in rows:
        cells = row.find_all("td")
        if len(cells) >= 4:
            try:
                qid = cells[0].text.strip()
                selected_option_id = cells[1].text.strip()
                correct_option_id = cells[2].text.strip()
                status = cells[3].text.strip()

                questions.append({
                    "qid": qid,
                    "selected": selected_option_id,
                    "correct": correct_option_id,
                    "status": status
                })
            except:
                continue
    return questions

def calculate_score(responses, answer_key):
    score = 0
    for q in responses:
        qid = q["qid"]
        selected = q["selected"]
        correct = answer_key.get(qid, "")

        if selected == "":
            continue
        elif selected == correct:
            score += 5
        else:
            score -= 1
    return score

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            html_content = file.read().decode('utf-8')
            responses = parse_response_sheet(html_content)
            total_score = calculate_score(responses, answer_key)
            return render_template('frntnd.html', score=total_score)

    return render_template('frntnd.html', score=None)

if __name__ == '__main__':
    app.run(debug=True)
