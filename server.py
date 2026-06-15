"""
Soul Compass — 로컬 데이터 수집 서버
======================================
실행 방법:
    python3 server.py

그러면 브라우저에서 http://localhost:8080 으로 접속하면 됩니다.
설문 결과가 나올 때마다 soul-compass-data.csv 에 자동 누적됩니다.

필요 라이브러리: Python 표준 라이브러리만 사용 (별도 설치 불필요)
"""

import http.server
import json
import csv
import os
from datetime import datetime

# ── 설정 ──────────────────────────────────────────────
PORT     = 8080
CSV_FILE = 'soul-compass-data.csv'
CSV_HEADER = [
    '저장시간',
    '육_1순위', '육_1순위%', '육_2순위', '육_2순위%',
    '혼_1순위', '혼_1순위%', '혼_2순위', '혼_2순위%',
    '영_1순위', '영_1순위%', '영_2순위', '영_2순위%',
]
# ──────────────────────────────────────────────────────


def ensure_csv():
    """CSV 파일이 없으면 헤더와 함께 생성"""
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='', encoding='utf-8-sig') as f:
            csv.writer(f).writerow(CSV_HEADER)
        print(f"[초기화] {CSV_FILE} 파일을 생성했습니다.")


def append_row(data: dict):
    """결과 데이터를 CSV에 한 줄 추가"""
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def layer(key):
        obj = data.get(key, {})
        return [
            obj.get('first', ''),
            obj.get('firstPct', ''),
            obj.get('second', ''),
            obj.get('secondPct', ''),
        ]

    row = [now] + layer('body') + layer('soul') + layer('spirit')

    with open(CSV_FILE, 'a', newline='', encoding='utf-8-sig') as f:
        csv.writer(f).writerow(row)

    print(f"[저장] {now} | "
          f"육({row[1]} {row[2]}%, {row[3]} {row[4]}%) | "
          f"혼({row[5]} {row[6]}%, {row[7]} {row[8]}%) | "
          f"영({row[9]} {row[10]}%, {row[11]} {row[12]}%)")


class Handler(http.server.SimpleHTTPRequestHandler):

    def do_OPTIONS(self):
        """CORS preflight"""
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_POST(self):
        if self.path == '/save':
            try:
                length = int(self.headers.get('Content-Length', 0))
                body   = self.rfile.read(length)
                data   = json.loads(body)
                append_row(data)
                self.send_response(200)
                self._cors()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"ok":true}')
            except Exception as e:
                print(f"[오류] {e}")
                self.send_response(500)
                self._cors()
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin',  '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def log_message(self, fmt, *args):
        # /save 외 일반 파일 요청은 간결하게 출력
        if '/save' not in (args[0] if args else ''):
            pass  # 정적 파일 로그 생략 (필요 시 주석 해제)
        # print(f"[{self.address_string()}] {fmt % args}")


if __name__ == '__main__':
    ensure_csv()
    server = http.server.HTTPServer(('', PORT), Handler)
    print("=" * 50)
    print(f"  Soul Compass 서버 시작")
    print(f"  브라우저 접속: http://localhost:{PORT}/soul-compass.html")
    print(f"  데이터 저장:   {os.path.abspath(CSV_FILE)}")
    print(f"  종료:          Ctrl+C")
    print("=" * 50)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[종료] 서버를 종료합니다.")
