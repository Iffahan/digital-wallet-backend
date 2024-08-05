from . import items, merchants, wallets

def init_router(app):
    app.include_router(items.router)
    app.include_router(merchants.router)
    app.include_router(wallets.router)
