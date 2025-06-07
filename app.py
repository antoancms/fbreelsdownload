from flask import Flask, request, jsonify, render_template_string
import json
import subprocess

app = Flask(__name__)

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>FastVideoSave Clone</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; padding: 2rem; background: #f4f4f4; }
        form { margin-bottom: 2rem; }
        input[type=url] { width: 100%; padding: 1rem; font-size: 1rem; }
        button { padding: 1rem 2rem; font-size: 1rem; background: #007BFF; color: white; border: none; cursor: pointer; }
        #result { background: white; padding: 1rem; border-radius: 8px; margin-top: 1rem; }
        img { max-width: 100%; height: auto; border-radius: 6px; margin-top: 1rem; }
        a { display: inline-block; margin-top: 0.5rem; color: #007BFF; text-decoration: none; }
    </style>
</head>
<body>
    <h1>FastVideoSave Clone (Test)</h1>
    <form id="fetchForm">
        <input type="url" name="videoUrl" placeholder="Paste Facebook or Instagram link here..." required />
        <button type="submit">Download</button>
    </form>
    <div id="result"></div>

    <script>
    document.getElementById("fetchForm").addEventListener("submit", async function(e) {
        e.preventDefault();
        const url = this.videoUrl.value;

        const res = await fetch('/download', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({url})
        });

        const data = await res.json();
        const result = document.getElementById("result");
        result.innerHTML = "";

        if (data.formats) {
            result.innerHTML += `<h2>${data.title}</h2><img src="${data.thumbnail}" />`;
            data.formats.forEach(f => {
                result.innerHTML += `<a href="${f.url}" target="_blank">Download ${f.ext}</a><br>`;
            });
        } else {
            result.innerHTML = `<p style='color:red;'>Error: ${data.error}</p>`;
        }
    });
    </script>
</body>
</html>
'''

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/download", methods=["POST"])
def download_video():
    url = request.json.get("url")
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        command = ["yt-dlp", "--skip-download", "--no-warnings", "--quiet", "--print-json", url]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output, error = process.communicate()

        if process.returncode != 0:
            return jsonify({"error": error.strip()}), 500

        info = json.loads(output)
        formats = [
            {"format_id": f["format_id"], "url": f["url"], "ext": f["ext"]}
            for f in info.get("formats", []) if "video" in f.get("format", "")
        ]

        return jsonify({
            "title": info.get("title"),
            "thumbnail": info.get("thumbnail"),
            "formats": formats
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Do not start Flask with debug or reloader to avoid system exit errors in sandbox
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
