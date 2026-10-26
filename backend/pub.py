# Kết nối tới cùng Redis với terminal A.
import redis
from redis import Redis
from dotenv import load_dotenv
import os
from getpass import getpass

# Load ENV variables
load_dotenv()
PASSWORD = os.getenv("PASSWORD")

r = Redis(host="192.168.0.12", port=6379, password=PASSWORD)
r.ping()

# Phát một thông báo lên đúng channel.
print(r.publish("practice", "hello"))
