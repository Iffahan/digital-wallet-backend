from . import users
from . import items
from . import merchants
from . import authentication
from . import wallets
from . import transactions
from . import root
def init_router(app):
    app.include_router(root.router)
    app.include_router(users.router)
    app.include_router(authentication.router)
    app.include_router(items.router)
    app.include_router(merchants.router)
    app.include_router(wallets.router)
    app.include_router(transactions.router)


