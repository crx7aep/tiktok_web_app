from flask import Flask, render_template, request, send_file
from pathlib import Path
import subprocess
import os
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = Path("uploads")
PROCESSED_FOLDER = Path("processed")
UPLOAD_FOLDER.mkdir(exist_ok=True)
PROCESSED_FOLDER.mkdir(exist_ok=True)

def process_video(input_path, output_path):
    # FFmpeg command: video 2x speed, audio unchanged
    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-filter:v", "setpts=0.5*PTS",  # speed up video 2x
        "-c:a", "copy",
        str(output_path)
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("video")
        if not file:
            return "No file uploaded", 400

        filename = file.filename.replace(" ", "_")
        temp_path = UPLOAD_FOLDER / f"{uuid.uuid4()}_{filename}"
        file.save(temp_path)

        output_name = request.form.get("output_name") or f"processed_{filename}"
        output_path = PROCESSED_FOLDER / output_name

        process_video(temp_path, output_path)

        # Cleanup uploaded file
        temp_path.unlink(missing_ok=True)

        return send_file(output_path, as_attachment=True)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
