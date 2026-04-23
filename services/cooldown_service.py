import time

cooldowns = {}

def check_cd(user_id, key, delay):
    now = time.time()

    if user_id in cooldowns and key in cooldowns[user_id]:
        last = cooldowns[user_id][key]
        if now - last < delay:
            return False, int(delay - (now - last))

    cooldowns.setdefault(user_id, {})[key] = now
    return True, 0
