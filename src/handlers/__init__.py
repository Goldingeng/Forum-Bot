from .menu_handler import menu_router
from .help_handler import help_router
from .admin_handler import admin_router



all_routers = []

for var in globals().copy():
    if not var.endswith("router"):
        continue

    all_routers.append(globals()[var])