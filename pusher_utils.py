import pusher
from config import Config

def trigger_pusher(channel, event, message):
    pusher_client = pusher.Pusher(
        app_id=Config.PUSHER_APP_ID,
        key=Config.PUSHER_KEY,
        secret=Config.PUSHER_SECRET,
        cluster=Config.PUSHER_CLUSTER,
        ssl=True
    )
    pusher_client.trigger(channel, event, {"message": message})
