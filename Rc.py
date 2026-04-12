import requests
import uuid
import json
import time
import random

# A list of common User-Agents to help disguise the requests
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1"
]

def get_free_proxies() -> list:
    """Fetches a live list of free HTTP proxies from a public repository."""
    print("[*] Fetching live free proxies...")
    url = "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        # Split the text by newlines and return the list
        proxies = response.text.strip().split('\n')
        print(f"[*] Successfully loaded {len(proxies)} free proxies.")
        return proxies
    except Exception as e:
        print(f"[!] Failed to fetch proxies: {e}")
        return []

def rc_lookup(rc_number: str, proxy_list: list) -> dict:
    if not rc_number.strip():
        return {"status": "error", "message": "No RC number"}

    session_id = f"{uuid.uuid4()}-{uuid.uuid4()}"
    payload = {
        "regNo": rc_number.strip().upper(),
        "sessionid": session_id
    }

    # We will try up to 10 different free proxies before giving up
    max_attempts = 10 
    
    for attempt in range(1, max_attempts + 1):
        # Pick a random proxy from the list
        proxy_address = random.choice(proxy_list) if proxy_list else None
        proxies = {"http": f"http://{proxy_address}", "https": f"http://{proxy_address}"} if proxy_address else None
        
        print(f"[-] Attempt {attempt}/{max_attempts} | Using Proxy: {proxy_address or 'Direct Connection'}")

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://www.91wheels.com",
            "Referer": "https://www.91wheels.com/",
            "User-Agent": random.choice(USER_AGENTS)
        }

        try:
            # Short timeout because free proxies often hang indefinitely
            response = requests.post(
                "https://api1.91wheels.com/api/v1/third/rc-detail",
                headers=headers,
                data=json.dumps(payload),
                proxies=proxies,
                timeout=8 
            )

            # Check for IP limit (429) or Cloudflare blocks (403)
            if response.status_code in [429, 403] or "limit" in response.text.lower():
                print(f"[!] Proxy {proxy_address} is blocked. Rotating...")
                continue 

            response.raise_for_status()
            print("[+] Success!")
            return response.json()

        except requests.exceptions.RequestException as e:
            # Free proxies frequently drop connections or timeout
            print(f"[!] Proxy {proxy_address} failed ({type(e).name}). Rotating...")
            continue

    return {"status": "error", "message": "Failed to get data after trying multiple proxies."}

if name == "main":
    rc = input("Enter RC Number: ").strip()
    
    # 1. Fetch the list of free proxies
    free_proxies = get_free_proxies()
    
    # 2. Run the lookup using the proxy list
    result = rc_lookup(rc, proxy_list=free_proxies)
    
    # 3. Print results
    output = json.dumps(result, indent=2)
    print("\n--- RESULTS ---")
    print(output)