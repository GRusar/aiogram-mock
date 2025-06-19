import itertools
from datetime import datetime
from typing import Callable, Optional, Sequence, Union

from aiogram import Bot, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import DEFAULT_DESTINY, BaseStorage, StorageKey
from aiogram.methods import AnswerCallbackQuery
from aiogram.types import (
    CallbackQuery,
    Chat,
    ChatMemberUpdated,
    Contact,
    InlineKeyboardButton,
    Message,
    Update,
    User,
)
from aiogram.utils.magic_filter import MagicFilter

from aiogram_mock.tg_state import ChatMemberType, TgState, UserState


class TgControl:
    def __init__(
        self,
        dispatcher: Dispatcher,
        bot: Bot,
        tg_state: TgState,
    ):
        self._dispatcher = dispatcher
        self._bot = bot
        self._tg_state = tg_state

    def messages(self, chat_id: int) -> Sequence[Message]:
        return self._tg_state.chat_history(chat_id)

    def last_message(self, chat_id: int) -> Message:
        return self._tg_state.chat_history(chat_id)[-1]

    def user_state(self, *, chat_id: int, user_id: int) -> UserState:
        return self._tg_state.get_user_state(chat_id=chat_id, user_id=user_id)

    def chat_member(self, *, chat_id: int, user_id: int) -> ChatMemberType:
        return self._tg_state.get_chat_member(chat_id, user_id)

    async def _send_message(self, message: Message) -> None:
        await self._dispatcher.feed_update(
            self._bot,
            Update(
                update_id=self._tg_state.increment_update_id(),
                message=self._tg_state.add_message(message),
            ),
        )

    async def send(self, from_user: User, chat: Chat, text: str) -> None:
        await self._send_message(
            Message(
                message_id=self._tg_state.next_message_id(chat.id),
                date=datetime.utcnow(),
                from_user=from_user,
                chat=chat,
                text=text,
            ),
        )

    async def send_contact(self, from_user: User, chat: Chat, contact: Contact) -> None:
        await self._send_message(
            Message(
                message_id=self._tg_state.next_message_id(chat.id),
                date=datetime.utcnow(),
                from_user=from_user,
                chat=chat,
                contact=contact,
            ),
        )

    async def click(
        self,
        selector: Union[Callable[[InlineKeyboardButton], bool], MagicFilter],
        message: Message,
        user: User,
    ) -> AnswerCallbackQuery:
        if message.reply_markup is None:
            raise ValueError("Message has no inline keyboard")
        if isinstance(selector, MagicFilter):
            selector = selector.resolve

        buttons = itertools.chain.from_iterable(message.reply_markup.inline_keyboard)
        selected_buttons = [button for button in buttons if selector(button)]
        if len(selected_buttons) == 0:
            raise ValueError("selector skip all buttons")
        if len(selected_buttons) > 1:
            raise ValueError("selector selects more than one button")
        button = selected_buttons[0]

        callback_query_id = self._tg_state.next_callback_query_id()
        await self._dispatcher.feed_update(
            self._bot,
            Update(
                update_id=self._tg_state.increment_update_id(),
                callback_query=CallbackQuery(
                    id=callback_query_id,
                    data=button.callback_data,
                    chat_instance=str(
                        message.chat.id
                    ),  # message.chat.id contains local id
                    from_user=user,
                    message=message,
                ),
            ),
        )
        return self._tg_state.get_answer_callback_query(callback_query_id)

    async def update_chat_member(
        self,
        *,
        chat: Chat,
        from_user: User,
        old_member: ChatMemberType,
        new_member: ChatMemberType,
        my: bool = False,
    ) -> None:
        self._tg_state.set_chat_member(chat.id, new_member)
        update = ChatMemberUpdated(
            chat=chat,
            from_user=from_user,
            date=datetime.utcnow(),
            old_chat_member=old_member,
            new_chat_member=new_member,
        )
        await self._dispatcher.feed_update(
            self._bot,
            Update(
                update_id=self._tg_state.increment_update_id(),
                **({"my_chat_member": update} if my else {"chat_member": update}),  # type: ignore
            ),
        )

    @property
    def bot(self) -> Bot:
        return self._bot

    @property
    def storage(self) -> BaseStorage:
        return self._dispatcher.storage


class PrivateChatTgControl:
    def __init__(self, tg_control: TgControl, chat: Chat, user: User):
        self._tg_control = tg_control
        self._chat = chat
        self._user = user
        self._validate()

    def _validate(self) -> None:
        if self._chat.id != self._user.id:
            raise ValueError("chat.id and user.id must be equal")

    def state(self, destiny: str = DEFAULT_DESTINY) -> FSMContext:
        return FSMContext(
            storage=self._tg_control.storage,
            key=StorageKey(
                bot_id=self.bot.id,
                chat_id=self._chat.id,
                user_id=self._user.id,
                destiny=destiny,
            ),
        )

    @property
    def messages(self) -> Sequence[Message]:
        return self._tg_control.messages(self._chat.id)

    @property
    def last_message(self) -> Message:
        return self._tg_control.last_message(self._chat.id)

    @property
    def user_state(self) -> UserState:
        return self._tg_control.user_state(chat_id=self._chat.id, user_id=self._user.id)

    @property
    def member(self) -> ChatMemberType:
        return self._tg_control.chat_member(
            chat_id=self._chat.id, user_id=self._user.id
        )

    @property
    def bot(self) -> Bot:
        return self._tg_control.bot

    @property
    def user(self) -> User:
        return self._user

    @property
    def chat(self) -> Chat:
        return self._chat

    async def send(
        self, text: str, user: Optional[User] = None, chat: Optional[Chat] = None
    ) -> None:
        return await self._tg_control.send(
            from_user=user or self._user,
            chat=chat or self._chat,
            text=text,
        )

    async def send_contact(self, contact: Contact) -> None:
        await self._tg_control.send_contact(
            from_user=self._user,
            chat=self._chat,
            contact=contact,
        )

    async def click(
        self,
        selector: Union[Callable[[InlineKeyboardButton], bool], MagicFilter],
        message: Optional[Message] = None,
    ) -> AnswerCallbackQuery:
        if message is None:
            message = self.last_message
        return await self._tg_control.click(selector, message, self._user)

    async def update_member(
        self,
        new_member: ChatMemberType,
        *,
        from_user: Optional[User] = None,
        old_member: Optional[ChatMemberType] = None,
        my: bool = False,
    ) -> None:
        await self._tg_control.update_chat_member(
            chat=self._chat,
            from_user=from_user or self._user,
            old_member=old_member or self.member,
            new_member=new_member,
            my=my,
        )
