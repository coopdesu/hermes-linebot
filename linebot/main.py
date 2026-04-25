import os
import json
import base64
import tempfile
import threading
import hashlib
import hmac
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi, MessagingApiBlob,
    ReplyMessageRequest, PushMessageRequest, TextMessage,
)
from linebot.v3.webhooks import MessageEvent, ImageMessageContent
from google import genai as genai_client
from PIL import Image

app = Flask(__name__)

LINE_TOKEN  = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
LINE_SECRET = os.environ["LINE_CHANNEL_SECRET"]
GEMINI_KEY  = os.environ["GEMINI_API_KEY"]

configuration = Configuration(access_token=LINE_TOKEN)
handler = WebhookHandler(LINE_SECRET)
gemini = genai_client.Client(api_key=GEMINI_KEY)

LEATHERS_PATH = Path(__file__).parent.parent / "leathers.json"
with open(LEATHERS_PATH, encoding="utf-8") as f:
    _leathers = json.load(f)

def _leather_ref_line(l):
    parts = [f"- {l['name_jp']} ({l['name_en']}): {l['description_jp']}"]
    if l.get('visual_characteristics'):
        parts.append(f"  視覺特徵: {l['visual_characteristics']}")
    if l.get('how_to_identify'):
        parts.append(f"  辨識重點: {l['how_to_identify']}")
    if l.get('shine_level'):
        parts.append(f"  光澤: {l['shine_level']}")
    return "\n".join(parts)

LEATHER_REF = "\n".join(_leather_ref_line(l) for l in _leathers)

PROMPT = f"""You are a Hermès luxury goods authentication expert. Carefully analyze this photo and identify:

1. **皮革種類 / Leather Type**: Match from the database below using visual characteristics. Give Japanese name + English name.
2. **顏色 / Color**: Use official Hermès color names (e.g. Gold, Noir, Rouge Tomate, Bleu Saphir, Etoupe, Craie, Graphite, etc.)
3. **五金 / Hardware**: PHW (Palladium/銀色) / GHW (Gold/金色) / RGHW (Rose Gold/玫瑰金) / BGHW (Black/黑色)
4. **成色 / Condition**: A (Near Mint/近新) / AB (Excellent/極少使用) / B (Good/正常使用) / BC (Fair/明顯使用) / C (Used/重度使用)
5. **收購建議 / Buying Note**: Market comment on this combination's desirability and collectibility.

CRITICAL - Leather identification rules:
- Epsom: UNIFORM pressed crosshatch/grid pattern, very structured, matte surface — the grid lines are clear and consistent
- Evercolor: fine natural grain (NOT grid), slightly softer than Epsom, subtle sheen — often confused with Epsom but lacks the crosshatch
- Togo: medium ROUND bumpy grain, slightly matte, holds shape
- Clemence: LARGE loose grain, soft/slouchy, waxy sheen — bigger grain than Togo
- Fjord: similar to Togo but slightly coarser grain with slight sheen
- Swift: completely smooth with NO grain, semi-gloss, very prone to scratches
- Box Calf: smooth, HIGH gloss mirror-like finish, develops patina
- Chevre Mysore: very fine DENSE grain, high shine, vivid colors, stiffer
- Ostrich: round QUILL bumps in center panel, very distinctive
- Crocodile (Porosus/Niloticus): rectangular scales, spine line visible, extremely glossy

EASILY CONFUSED PAIRS — when in doubt, say so:
- Epsom ↔ Evercolor: Epsom has clear grid crosshatch; Evercolor has natural irregular grain. Photos often make this hard to distinguish.
- Togo ↔ Clemence: grain size is key — Clemence is noticeably larger and softer
- Togo ↔ Fjord: nearly identical in photos; Fjord has faint sheen
- Swift ↔ Box Calf: Swift is semi-matte smooth; Box Calf has high mirror gloss
- Chevre Mysore ↔ Epsom: both fine and structured; Chevre has higher shine and finer grain

Leather Database (reference):
{LEATHER_REF}

Reply in Traditional Chinese + English bilingual format. Be concise but precise.

IMPORTANT: If two leathers are visually similar in this photo, list BOTH possibilities and note that in-person verification is needed. Use this format when uncertain:
🐄 皮革 Leather: エプソン / Epsom（或 Evercolor，照片難以區分，建議現場觸感確認 / photo ambiguous, in-person verification recommended）

Standard format (when confident):
🐄 皮革 Leather: トゴ / Togo
🎨 顏色 Color: Gold（金棕色）
🔩 五金 Hardware: GHW（金色）
✨ 成色 Condition: AB（極少使用，角落輕微磨損）
💡 收購建議 Note: Togo + Gold + GHW 為最經典組合，市場流通性極高，建議積極收購。"""


@app.route("/health", methods=["GET"])
def health():
    return "OK"


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)

    # Validate signature before spawning thread
    mac = hmac.new(LINE_SECRET.encode("utf-8"), body.encode("utf-8"), hashlib.sha256).digest()
    if signature != base64.b64encode(mac).decode("utf-8"):
        abort(400)

    # Return 200 immediately; process in background to avoid LINE 30s timeout
    t = threading.Thread(target=_handle_body, args=(body, signature), daemon=True)
    t.start()
    return "OK"


def _handle_body(body, signature):
    try:
        handler.handle(body, signature)
    except Exception:
        pass


@handler.add(MessageEvent, message=ImageMessageContent)
def handle_image(event):
    user_id = event.source.user_id
    with ApiClient(configuration) as api_client:
        line_api = MessagingApi(api_client)
        blob_api = MessagingApiBlob(api_client)

        content_response = blob_api.get_message_content(event.message.id)
        img_bytes = content_response
        tmp_path = None

        try:
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                tmp.write(img_bytes)
                tmp_path = tmp.name

            img = Image.open(tmp_path)
            response = gemini.models.generate_content(
                model="gemini-2.5-flash",
                contents=[PROMPT, img],
            )
            reply_text = response.text.strip()
        except Exception as e:
            reply_text = f"辨識失敗 / Analysis failed: {e}"
        finally:
            if tmp_path:
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass

        # Use push message — reply_token may expire during cold start
        line_api.push_message(
            PushMessageRequest(
                to=user_id,
                messages=[TextMessage(text=reply_text[:4900])],
            )
        )


@handler.add(MessageEvent)
def handle_other(event):
    user_id = event.source.user_id
    with ApiClient(configuration) as api_client:
        line_api = MessagingApi(api_client)
        line_api.push_message(
            PushMessageRequest(
                to=user_id,
                messages=[TextMessage(
                    text="👜 請傳送愛馬仕商品圖片\nPlease send a photo of your Hermès item."
                )],
            )
        )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
