import os
import json
import hashlib
import hmac
import base64
import threading
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi,
    PushMessageRequest, TextMessage,
    QuickReply, QuickReplyItem, MessageAction,
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent, FollowEvent

from google.oauth2 import service_account
from googleapiclient.discovery import build

app = Flask(__name__)

LINE_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
LINE_SECRET = os.environ["LINE_CHANNEL_SECRET"]
CALENDAR_ID = os.environ.get("CALENDAR_ID", "atp2666@gmail.com")
SA_JSON_ENV = os.environ.get("GOOGLE_CREDENTIALS_JSON")
SA_FILE = os.environ.get(
    "GOOGLE_CREDENTIALS_FILE",
    str(Path(__file__).parent / "service-account.json"),
)
TZ = "Asia/Taipei"

configuration = Configuration(access_token=LINE_TOKEN)
handler = WebhookHandler(LINE_SECRET)


def _calendar_service():
    scopes = ["https://www.googleapis.com/auth/calendar"]
    if SA_JSON_ENV:
        info = json.loads(SA_JSON_ENV)
        creds = service_account.Credentials.from_service_account_info(info, scopes=scopes)
    else:
        creds = service_account.Credentials.from_service_account_file(SA_FILE, scopes=scopes)
    return build("calendar", "v3", credentials=creds, cache_discovery=False)


_sessions = {}

WELCOME = (
    "👋 歡迎蒞臨 Frank 愛車顧問\n\n"
    "可協助您預約試乘、賞車與回答車款問題。\n\n"
    "📌 預約時會蒐集您的姓名與電話，僅用於聯繫確認，不作他用。\n\n"
    "點下方「預約試乘」即可開始。"
)

MAIN_MENU = QuickReply(items=[
    QuickReplyItem(action=MessageAction(label="預約試乘", text="預約試乘")),
    QuickReplyItem(action=MessageAction(label="預約賞車", text="預約賞車")),
    QuickReplyItem(action=MessageAction(label="取消預約", text="取消")),
])


def _reset(user_id):
    _sessions.pop(user_id, None)


def _date_quick_reply():
    items = []
    today = datetime.now()
    for i in range(1, 8):
        d = today + timedelta(days=i)
        label = d.strftime("%m/%d")
        value = d.strftime("%Y-%m-%d")
        items.append(QuickReplyItem(action=MessageAction(label=label, text=value)))
    return QuickReply(items=items)


def _time_quick_reply():
    items = []
    for h in [10, 11, 13, 14, 15, 16, 17]:
        label = f"{h:02d}:00"
        items.append(QuickReplyItem(action=MessageAction(label=label, text=label)))
    return QuickReply(items=items)


def _create_event(user_id, session):
    svc = _calendar_service()
    start = datetime.strptime(f"{session['date']} {session['time']}", "%Y-%m-%d %H:%M")
    end = start + timedelta(hours=1)
    service = session.get("service", "試乘")
    event = {
        "summary": f"[{service}] {session['car']} - {session['name']}",
        "description": (
            f"服務: {service}\n"
            f"車款: {session['car']}\n"
            f"客戶: {session['name']}\n"
            f"電話: {session['phone']}\n"
            f"LINE user_id: {user_id}"
        ),
        "start": {"dateTime": start.isoformat(), "timeZone": TZ},
        "end": {"dateTime": end.isoformat(), "timeZone": TZ},
    }
    created = svc.events().insert(calendarId=CALENDAR_ID, body=event).execute()
    return created.get("htmlLink")


@app.route("/health")
def health():
    return "OK"


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)
    mac = hmac.new(LINE_SECRET.encode(), body.encode(), hashlib.sha256).digest()
    if signature != base64.b64encode(mac).decode():
        abort(400)
    t = threading.Thread(target=_handle_body, args=(body, signature), daemon=True)
    t.start()
    return "OK"


def _handle_body(body, signature):
    try:
        handler.handle(body, signature)
    except Exception:
        pass


@handler.add(FollowEvent)
def on_follow(event):
    user_id = event.source.user_id
    _reset(user_id)
    _push(user_id, WELCOME, quick_reply=MAIN_MENU)


@handler.add(MessageEvent, message=TextMessageContent)
def on_text(event):
    user_id = event.source.user_id
    text = event.message.text.strip()

    if text in {"取消", "重來", "reset", "cancel"}:
        _reset(user_id)
        _push(user_id, "已取消。需要再次預約請點下方按鈕。", quick_reply=MAIN_MENU)
        return

    if text in {"預約賞車", "賞車"}:
        _sessions[user_id] = {"step": "car", "service": "賞車"}
        _push(user_id, "請問想看的車款？（例：330i、X3 等，直接輸入即可）")
        return

    if text in {"預約", "預約試乘", "開始", "試乘"}:
        _sessions[user_id] = {"step": "car", "service": "試乘"}
        _push(user_id, "請問想試乘的車款？（例：330i、X3 等，直接輸入即可）")
        return

    session = _sessions.get(user_id)
    if not session:
        _push(user_id, WELCOME, quick_reply=MAIN_MENU)
        return

    step = session["step"]

    if step == "car":
        session["car"] = text[:40]
        session["step"] = "date"
        _push(user_id, "請選擇希望的日期：", quick_reply=_date_quick_reply())

    elif step == "date":
        try:
            datetime.strptime(text, "%Y-%m-%d")
        except ValueError:
            _push(user_id, "日期格式錯誤，請從下方選單選擇。", quick_reply=_date_quick_reply())
            return
        session["date"] = text
        session["step"] = "time"
        _push(user_id, "請選擇希望的時段（每段 1 小時）：", quick_reply=_time_quick_reply())

    elif step == "time":
        try:
            datetime.strptime(text, "%H:%M")
        except ValueError:
            _push(user_id, "時間格式錯誤，請從下方選單選擇。", quick_reply=_time_quick_reply())
            return
        session["time"] = text
        session["step"] = "name"
        _push(user_id, "最後，請輸入您的姓名與電話，以空格分隔：\n例：王小明 0912345678")

    elif step == "name":
        parts = text.split(None, 1)
        phone_chars = parts[1].replace("-", "").replace(" ", "") if len(parts) == 2 else ""
        if len(parts) != 2 or not phone_chars.isdigit() or len(phone_chars) < 8:
            _push(user_id, "請依格式輸入：姓名 電話（例：王小明 0912345678）")
            return
        session["name"] = parts[0][:20]
        session["phone"] = parts[1][:20]
        try:
            _create_event(user_id, session)
            reply = (
                "✅ 預約完成！\n\n"
                f"服務：{session.get('service', '試乘')}\n"
                f"車款：{session['car']}\n"
                f"時間：{session['date']} {session['time']}\n"
                f"姓名：{session['name']}\n"
                f"電話：{session['phone']}\n\n"
                "顧問會盡快與您聯繫確認。如需取消請輸入「取消」。"
            )
        except Exception as e:
            reply = f"預約建立失敗，請稍後再試或直接聯繫顧問。\n錯誤：{e}"
        finally:
            _reset(user_id)
        _push(user_id, reply, quick_reply=MAIN_MENU)


def _push(user_id, text, quick_reply=None):
    msg = TextMessage(text=text, quick_reply=quick_reply) if quick_reply else TextMessage(text=text)
    with ApiClient(configuration) as api:
        MessagingApi(api).push_message(
            PushMessageRequest(to=user_id, messages=[msg])
        )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
