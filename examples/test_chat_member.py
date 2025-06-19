import pytest
from aiogram import Bot, Dispatcher
from aiogram.types import ChatMemberUpdated, ChatMemberLeft

from aiogram_mock.facade_factory import private_chat_tg_control
from aiogram_mock.tg_control import PrivateChatTgControl


async def on_member(update: ChatMemberUpdated):
    on_member.data = update


def create_bot_and_dispatcher():
    bot = Bot(token='123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11')
    dispatcher = Dispatcher()
    dispatcher.chat_member.register(on_member)
    return bot, dispatcher


@pytest.fixture()
def tg_control() -> PrivateChatTgControl:
    bot, dispatcher = create_bot_and_dispatcher()
    with private_chat_tg_control(bot=bot, dispatcher=dispatcher) as tg:
        yield tg


async def test_member_update(tg_control: PrivateChatTgControl):
    new_member = ChatMemberLeft(user=tg_control.user)
    await tg_control.update_member(new_member)
    assert isinstance(tg_control.member, ChatMemberLeft)
    result = await tg_control.bot.get_chat_member(tg_control.chat.id, tg_control.user.id)
    assert isinstance(result, ChatMemberLeft)
    assert isinstance(on_member.data.new_chat_member, ChatMemberLeft)
