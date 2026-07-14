import random
from locust import HttpUser, task, between

class LingofyUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        # Every locust user will just hit public endpoints to avoid creating thousands of fake users
        pass

    @task(3)
    def check_health(self):
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed! Status code: {response.status_code}")

    @task(1)
    def fetch_lyrics(self):
        # Hit lyrics with some random tracks
        tracks = [("Bohemian Rhapsody", "Queen"), ("Shape of You", "Ed Sheeran"), ("Blinding Lights", "The Weeknd")]
        track, artist = random.choice(tracks)
        with self.client.get(f"/lyrics?track={track}&artist={artist}", catch_response=True) as response:
            if response.status_code in [200, 429, 502]:
                response.success()
            else:
                response.failure(f"Failed! Status code: {response.status_code}")
