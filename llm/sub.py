# Kết nối tới Redis bằng cấu hình bạn đang dùng.
import redis
from getpass import getpass
r = redis.Redis(host=input("Redis host: "), port=6379, password=getpass("Redis password: "), decode_responses=True)
r.ping()

# Đăng ký nghe channel thử nghiệm.
sub = r.pubsub()
sub.subscribe("practice")

# Chờ và in các thông báo nhận được.
for message in sub.listen():
    if message["type"] == "message":
        # Use the published job ID to retrieve its stored answer.
        job_id = message["data"]
        answer = r.get(f"response:{job_id}")
        print(job_id, answer)
