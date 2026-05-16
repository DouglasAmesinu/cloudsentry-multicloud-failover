import requests
import logging

def update_dns(zone_id: str, record_id: str, api_token: str, ip: str) -> bool:
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "type": "A", "name": "@",
        "content": ip, "ttl": 60, "proxied": False
    }
    try:
        response = requests.patch(url, json=payload, headers=headers, timeout=10)
        result = response.json()
        if result.get("success"):
            logging.info(f"DNS updated successfully to {ip}")
            return True
        else:
            logging.error(f"Cloudflare error: {result.get('errors')}")
            return False
    except Exception as e:
        logging.error(f"DNS update exception: {e}")
        return False

def get_current_ip(zone_id: str, record_id: str, api_token: str) -> str:
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}"
    headers = {"Authorization": f"Bearer {api_token}"}
    response = requests.get(url, headers=headers, timeout=10)
    return response.json()["result"]["content"]
