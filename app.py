import traceback
from bs4 import BeautifulSoup
import requests
from flask import Flask, request, session, Response, jsonify
from selenium_login import login_with_selenium

app = Flask(__name__)
app.secret_key = 'IOCogBitRoboIO' # Nara Kage #

def apply_selenium_cookies(sess: requests.Session, cookies):
    for c in cookies:
        sess.cookies.set(c['name'], c['value'], domain=c.get('domain'), path=c.get('path'))
    return sess

def target_url(path: str) -> str:
    if path.startswith(('http://', 'https://')):
        return path
    return f"https://www.jokerapp888e.net/{path}"

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'POST'])
def proxy(path):
    url = target_url(path)
    sess = requests.Session()

    # On login endpoint, run Selenium once
    if path.startswith("Service/Login") and request.is_json:
        creds = request.get_json()
        cookies, result, redirect_url = login_with_selenium(creds["username"], creds["password"])
        print("📤 cookies:", cookies)
        sess = requests.Session()
        for c in cookies:
            sess.cookies.set(c['name'], c['value'], domain=c.get('domain'))
        session['cookies'] = sess.cookies.get_dict()
        resp = jsonify(result)
        resp.status_code = 200
        return resp

    else:
        sess.cookies.update(session.get('cookies', {}))

    headers = {
        'User-Agent': request.headers.get('User-Agent', ''),
        'Referer': 'https://www.jokerapp888e.net/GameIndex',
        'Origin': 'https://www.jokerapp888e.net',
    }

    try:
        args = request.args.to_dict()
        resp = (sess.post if request.method == 'POST' else sess.get)(
            url,
            params=args,
            json=request.get_json(silent=True) if request.method == 'POST' else None,
            headers=headers
        )

        session['cookies'] = sess.cookies.get_dict()

        content_type = resp.headers.get('Content-Type', 'text/html')
        excluded = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        out_headers = [(k, v) for k, v in resp.headers.items() if k.lower() not in excluded]

        # Only inject script if response is HTML
        if "text/html" in content_type:
            soup = BeautifulSoup(resp.content, "html.parser")

            inject_script = """
            <script>
                (function () {
                    console.log("✅ Login Watcher Activated");
                    function injectLoadingDiv() {
                        if (document.getElementById('loadingSite')) return; // already injected

                        const div = document.createElement('div');
                        div.className = "loading-page ng-scope";
                        div.id = "loadingSite";
                        div.setAttribute("ng-if", "loadingPage");
                        div.setAttribute("ng-style", "{'visibility' : (isFirstLoad == false) ? 'visible' : ''}");
                        div.style.visibility = "visible";
                        div.innerHTML = `<i class="icon icon-spinner6 spin"></i>`;
                        document.body.appendChild(div);
                    }

                    function removeLoadingDiv() {
                        const el = document.getElementById('loadingSite');
                        if (el) el.remove();
                    }

                    // WATCH FETCH
                    const originalFetch = window.fetch;
                    window.fetch = async function (...args) {
                        console.log("📦 fetch:", args[0]);
                        const response = await originalFetch.apply(this, args);
                        if (args[0].includes('/Service/Login')) {
                            const cloned = response.clone();
                            try {
                                const json = await cloned.json();
                                console.log("[fetch] /Service/Login →", json);
                                if (json.success) {
                                    window.location.href = "/";
                                }
                            } catch (e) {
                                console.error("Error parsing fetch JSON:", e);
                            }
                        }
                        return response;
                    };

                    // WATCH XHR
                    const open = XMLHttpRequest.prototype.open;
                    XMLHttpRequest.prototype.open = function (method, url) {
                        console.log("📦 XHR open to:", url);
                        this._url = url;
                        this.addEventListener("loadstart", function () {
                            if (this._url.includes('/Service/Login')) {
                                console.log("📦 XHR → injecting loading spinner...");
                                injectLoadingDiv();
                            }
                        });
                        this.addEventListener("load", function () {
                            if (this._url.includes('/Service/Login')) {
                                try {
                                    const json = JSON.parse(this.responseText);
                                    console.log("[xhr] /Service/Login →", json);
                                    if (json.Success) {
                                        window.location.href = "/";
                                    }
                                } catch (e) {
                                    console.error("Error parsing XHR JSON:", e);
                                }
                            }
                        });

                        return open.apply(this, arguments);
                    };
                })();
                </script>
            """

            if soup.body:
                soup.body.append(BeautifulSoup(inject_script, "html.parser"))
            else:
                soup.append(BeautifulSoup(inject_script, "html.parser"))

            modified_html = str(soup)
            return Response(modified_html, resp.status_code, headers=out_headers, content_type=content_type)

        return Response(resp.content, resp.status_code, headers=out_headers, content_type=content_type)

    except Exception as e:
        print(traceback.format_exc())
        return f"<h3>Proxy error</h3><pre>{e}</pre>"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
