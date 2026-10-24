from concurrent.futures import ThreadPoolExecutor
import json
import os
import requests

API_URL = "https://sumit-jwt-xi.vercel.app/token"
JSON_FILE = "account_ind(p).json"
BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = os.environ.get("ADMIN_ID")


def fetch_token(item):
    uid = item.get("uid")
    password = item.get("password")
    if not uid or not password:
        return {"uid": uid, "password": password, "token": "INVALID_DATA"}
    try:
        url = f"{API_URL}?uid={uid}&password={password}"
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            token_val = data.get("token", "")
            return {
                "uid": uid,
                "password": password,
                "token": token_val if token_val else "EMPTY_TOKEN",
            }
        else:
            return {
                "uid": uid,
                "password": password,
                "token": f"HTTP_{response.status_code}",
            }
    except Exception as e:
        return {"uid": uid, "password": password, "token": "ERROR"}


def main():
    if not os.path.exists(JSON_FILE):
        print(f"❌ {JSON_FILE} file nahi mili!")
        return

    with open(JSON_FILE, "r", encoding="utf-8") as f:
        try:
            data_list = json.load(f)
        except Exception as e:
            print("❌ JSON file read karne me error aayi:", e)
            return

    if not isinstance(data_list, list) or len(data_list) == 0:
        print("❌ JSON data empty hai.")
        return

    print(f"⚡ Total {len(data_list)} accounts par process shuru...")

    with ThreadPoolExecutor(max_workers=10) as executor:
        updated_data = list(executor.map(fetch_token, data_list))

    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(updated_data, f, indent=2)

    print("✅ Tokens successfully updated in file!")

    if BOT_TOKEN and ADMIN_ID:
        msg = f"✅ GitHub Action: {JSON_FILE} ke tokens automatically update ho chuke hain!"
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": ADMIN_ID, "text": msg},
        )


if __name__ == "__main__":
    main()
  
