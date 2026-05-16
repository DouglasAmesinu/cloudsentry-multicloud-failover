import requests
import logging

def check_health(url: str, timeout: int) -> bool:
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        logging.debug(f"Connection refused: {url}")
        return False
    except requests.exceptions.Timeout:
        logging.debug(f"Timeout ({timeout}s): {url}")
        return False
    except Exception as e:
        logging.debug(f"Unexpected error for {url}: {e}")
        return False
