from aiogram.fsm.state import State, StatesGroup


class ListingSG(StatesGroup):
    filling = State()
    preview = State()


class AdminSG(StatesGroup):
    add_dest = State()
    del_dest = State()
    add_sub = State()
    del_sub = State()
    reject_reason = State()
    edit_listing = State()
    add_admin = State()
    bc_content = State()
    bc_confirm = State()
