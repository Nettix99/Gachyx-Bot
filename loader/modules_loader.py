from handlers import start, profile, card, bonus, inventory, top, group
from admin import admin_panel

def register_all(dp):
    start.register(dp)
    profile.register(dp)
    card.register(dp)
    bonus.register(dp)
    inventory.register(dp)
    top.register(dp)
    group.register(dp)

    admin_panel.register(dp)
