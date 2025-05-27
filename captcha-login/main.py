from flask import Flask, request, jsonify, send_from_directory, render_template_string, redirect
import os
import csv

app = Flask(__name__)
EXPORT_FOLDER = "export"
LABEL_FILE = os.path.join(EXPORT_FOLDER, "labels.csv")
os.makedirs(EXPORT_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/edit-labels")
def edit_labels():
    rows_html = ""
    if os.path.exists(LABEL_FILE):
        with open(LABEL_FILE, newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                img_path = f"/download/{row['filename']}"
                rows_html += f'''
                <tr>
                    <td><img src="{img_path}"></td>
                    <td>{row['filename']}<input type="hidden" name="filename" value="{row['filename']}"></td>
                    <td>{row['text']}</td>
                    <td><input name="text" value="{row['text']}" maxlength="8"></td>
                </tr>
                '''
    return render_template_string(open("static/edit.html").read(), rows=rows_html)

@app.route("/update-labels", methods=["POST"])
def update_labels():
    filenames = request.form.getlist("filename")
    texts = request.form.getlist("text")

    with open(LABEL_FILE, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["filename", "text"])
        for f, t in zip(filenames, texts):
            writer.writerow([f, t])
    return redirect("/edit-labels")

@app.route("/download/<path:filename>")
def download_file(filename):
    return send_from_directory(EXPORT_FOLDER, filename, as_attachment=False)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
