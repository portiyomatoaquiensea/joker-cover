import traceback
import requests
from flask import Flask, request, session, Response, jsonify, redirect
from selenium_login import login_with_selenium

app = Flask(__name__)
app.secret_key = 'your-secret-key'

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
        # if result['Success']:
        #     return redirect(redirect_url)
        # else:
        #     return resp

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
            json=request.get_json(silent=True) if request.method=='POST' else None,
            headers=headers
        )

        session['cookies'] = sess.cookies.get_dict()
        excluded = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        out_headers = [(k, v) for k, v in resp.headers.items() if k.lower() not in excluded]
        return Response(resp.content, resp.status_code, headers=out_headers, content_type=resp.headers.get('Content-Type', 'text/html'))
    except Exception as e:
        print(traceback.format_exc())
        return f"<h3>Proxy error</h3><pre>{e}</pre>"


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
