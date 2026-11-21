#!/usr/bin/env python3
"""Optional local preview server and opt-in Gemini API bridge.

The static site and the guide chatbot work without this endpoint.  Set
EEMON_LLM_ENABLED=1 and EEMON_GEMINI_API_KEY only after reviewing the provider's
terms, budget, and input-data policy. NO secrets are exposed to the client.
"""
from __future__ import annotations
import collections
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import json
import os
from pathlib import Path
import re
import time
from urllib import request
from urllib.error import URLError
from urllib.parse import urlsplit

SITE = Path(__file__).resolve().parent / 'site'
MODEL = os.environ.get('EEMON_GEMINI_MODEL', 'gemini-3.5-flash')
RATE_LIMIT = 10  # per-IP per rolling hour (local preview only)
_calls: dict[str, collections.deque] = collections.defaultdict(collections.deque)

SYSTEM = '''あなたは「ええもん探しパパ」の購入前ガイドのAIです。
日本語で簡潔かつ親切に、買う条件・比較方法を説明します。
特定商品の価格・最安値・在庫・キャンペーン・購入経験・商品の安全性を実測したふりをしないでください。
この環境ではリアルタイムの商品データ、広告提携、購入履歴、個人情報を取得できません。
不確かなメーカー仕様・車種適合・安全規格は、公式資料の確認を勧めてください。
年齢・健康・家族関係・住所などの個人情報を要求しないでください。
商品を一方的に押し売りせず、用途・予算・優先条件を確認して3点以内の判断材料を返してください。
''' 


def remote_enabled():
    return os.environ.get('EEMON_LLM_ENABLED') == '1' and bool(os.environ.get('EEMON_GEMINI_API_KEY')) and bool(re.fullmatch(r'[\w.-]{3,80}', MODEL))


def generate_remote(question: str, *, opener=request.urlopen) -> str:
    if not remote_enabled():
        raise RuntimeError('remote AI disabled')
    if not isinstance(question, str) or not question.strip() or len(question)>240:
        raise ValueError('question must be 1-240 chars')
    url = 'https://generativelanguage.googleapis.com/v1beta/models/' + MODEL + ':generateContent'
    payload = {'systemInstruction': {'parts': [{'text': SYSTEM}]},
               'contents': [{'role': 'user', 'parts': [{'text': question}]}],
               'generationConfig': {'temperature':0.25,'maxOutputTokens':600}}
    encoded = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    req = request.Request(url, data=encoded, headers={'Content-Type':'application/json',
        'x-goog-api-key':os.environ['EEMON_GEMINI_API_KEY']}, method='POST')
    with opener(req, timeout=10) as response:
        obj=json.load(response)
    candidates=obj.get('candidates') or []
    if not candidates:
        raise RuntimeError('model returned no content')
    parts=(candidates[0].get('content') or {}).get('parts') or []
    answer=''.join(p.get('text','') for p in parts if isinstance(p,dict))
    if not answer.strip():raise RuntimeError('model returned empty text')
    return answer[:4000]


class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,directory=str(SITE),**kwargs)

    def log_message(self, format, *args):
        # Do not persist prompts, IPs, credential fragments or URLs in access logs.
        return

    def do_GET(self):
        if urlsplit(self.path).path == '/api/health':
            self.reply(200, {'remote_ai_available':remote_enabled(), 'mode':'optional_owner_consent'})
            return
        if urlsplit(self.path).path.startswith('/api/'):
            self.reply(404, {'error':'not found'});return
        return super().do_GET()

    def reply(self, code, value):
        encoded=json.dumps(value,ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Content-Length',str(len(encoded)))
        self.end_headers();self.wfile.write(encoded)

    def do_POST(self):
        if urlsplit(self.path).path != '/api/ask':self.reply(404, {'error':'not found'});return
        if self.headers.get('X-EEMON-Consent') != 'yes':self.reply(403, {'error':'explicit opt-in required'});return
        if not remote_enabled():self.reply(503, {'error':'remote model disabled'});return
        size=self.headers.get('Content-Length','')
        if not size.isdigit() or not 1<=int(size)<=1000:self.reply(413, {'error':'invalid size'});return
        try:
            payload=json.loads(self.rfile.read(int(size)))
            question=payload.get('question')
            if not isinstance(question,str) or not 1<=len(question.strip())<=240:
                self.reply(400, {'error':'invalid question'});return
        except (ValueError,AttributeError,UnicodeError):self.reply(400, {'error':'invalid JSON'});return
        # local preview guardrail, not public reverse-proxy production authorization
        now=time.monotonic();bucket=_calls[self.client_address[0]]
        while bucket and now-bucket[0]>3600:bucket.popleft()
        if len(bucket)>=RATE_LIMIT:self.reply(429, {'error':'hourly limit reached'});return
        bucket.append(now)
        try:
            self.reply(200, {'answer':generate_remote(question), 'provider':'Gemini', 'verified_price':False})
        except (ValueError,URLError,RuntimeError,TimeoutError,KeyError) as exc:
            self.reply(502, {'error':'provider unavailable'})


if __name__=='__main__':
    host=os.environ.get('EEMON_HOST','127.0.0.1')
    if host not in ('127.0.0.1','localhost','::1'):
        raise SystemExit('Refusing to bind publicly: production requires auth, CSRF and rate-limit infrastructure')
    port=int(os.environ.get('EEMON_PORT','8765'))
    print(f'EEMON local preview: http://{host}:{port} (remote_ai={remote_enabled()})')
    ThreadingHTTPServer((host,port),Handler).serve_forever()