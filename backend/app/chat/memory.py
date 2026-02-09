import json
from redis import Redis
from app.settings import settings

redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)

def redis_key(user_id: int, conversation_id: int) -> str:
    return f"chat:tenant:default:user:{user_id}:conv:{conversation_id}"

def load_state(user_id: int, conversation_id: int) -> dict:
    raw = redis_client.get(redis_key(user_id, conversation_id))
    return json.loads(raw) if raw else {}

def save_state(user_id: int, conversation_id: int, state: dict) -> None:
    redis_client.set(redis_key(user_id, conversation_id), json.dumps(state), ex=60 * 60 * 24)
