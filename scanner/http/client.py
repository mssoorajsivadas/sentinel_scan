import requests
import time

class HTTPClient:

    def __init__(self, timeout=8, delay=0.2):
        self.timeout = timeout
        self.delay = delay
        self.session = requests.Session()

        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        })

    def get(self, url):
        if self.delay > 0:
            time.sleep(self.delay)
            
        response = self.session.get(
            url,
            timeout=self.timeout,
            allow_redirects=False,
        )

        return response