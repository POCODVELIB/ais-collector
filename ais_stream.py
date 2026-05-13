


import asyncio
import websockets
import json
import os
import tempfile
from snowflake_config import get_connection

API_KEY = os.environ["AISSTREAM_API_KEY"]

BOUNDING_BOXES = [
    [[48.5, -2.5], [51.5,  2.5]],
    [[46.5, -5.5], [48.5, -1.5]],
    [[44.5, -3.0], [46.5, -1.0]],
    [[43.0, -2.5], [44.5, -1.0]],
]

BATCH_SIZE = 100
TMP_FILE   = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ais_batch.json")

def decode(raw) -> str:
    return raw.decode("utf-8") if isinstance(raw, bytes) else str(raw)

def flush(cursor, batch: list):
    with open(TMP_FILE, "w", encoding="utf-8") as f:
        f.writelines(r + "\n" for r in batch)

    snowflake_path = TMP_FILE.replace("\\", "/")

    try:
        cursor.execute(f"PUT 'file://{snowflake_path}' @%AIS_RAW AUTO_COMPRESS=TRUE OVERWRITE=TRUE")
        cursor.execute("""
            COPY INTO AIS_RAW (RAW_JSON)
            FROM (SELECT PARSE_JSON($1) FROM @%AIS_RAW)
            FILE_FORMAT = (TYPE='JSON')
            PURGE = TRUE
        """)
    finally:
        if os.path.exists(TMP_FILE):
            os.remove(TMP_FILE)

async def run():
    conn   = get_connection()
    cursor = conn.cursor()
    batch  = []
    count  = 0
    print("Connecte a Snowflake ✅")

    async with websockets.connect("wss://stream.aisstream.io/v0/stream") as ws:
        await ws.send(json.dumps({
            "APIKey"            : API_KEY,
            "BoundingBoxes"     : BOUNDING_BOXES,
            "FilterMessageTypes": ["PositionReport"],
        }))
        print("Connected to AISStream ✅\n")

        async for raw in ws:
            try:
                raw_str = decode(raw)
                message = json.loads(raw_str)

                if "error" in message:
                    print(f"Erreur API : {message['error']}")
                    break

                if message.get("MessageType") != "PositionReport":
                    continue

                batch.append(raw_str)

                if len(batch) >= BATCH_SIZE:
                    flush(cursor, batch)
                    count += len(batch)
                    batch.clear()
                    print(f"  Batch flush — total : {count}")

            except Exception as e:
                print(f"Erreur ignoree : {e}")

    # Flush du reste si le stream se coupe avant d'atteindre BATCH_SIZE
    if batch:
        flush(cursor, batch)
        count += len(batch)
        print(f"  Flush final — total : {count}")

if __name__ == "__main__":
    asyncio.run(run())
