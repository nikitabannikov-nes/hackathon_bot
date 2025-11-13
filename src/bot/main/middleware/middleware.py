from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from typing import Callable, Dict, Any, Awaitable
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy import select
from aiogram.dispatcher.middlewares import CancelHandler

class UserExistsMiddleware(BaseMiddleware):
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        
        
        # Получаем ID пользователя из события
        user_id = self._get_user_id(event)
        if not user_id:
            await self._handle_no_user_id(event)
            raise CancelHandler()
        
        async with async_sessionmaker():
            user_role = await self._check_user_role(session, user_id)
        
        if user_role == None or user_role not in ["admin", "checker", ]:
            await self._handle_user_not_found(event, user_id)
            raise CancelHandler()
        
        # Пользователь найден - передаем ID в data для хэндлеров
        data["user_id"] = user_id
        data["user_exists"] = True
        
        return await handler(event, data)
    
    def _get_user_id(self, event: TelegramObject) -> int | None:
        """Извлекает ID пользователя из события"""
        if hasattr(event, 'from_user') and event.from_user:
            return event.from_user.id
        return None
    
    async def _check_user_exists(self, session: AsyncSession, user_id: int) -> bool:
        """Проверяет существование пользователя в БД по ID"""
        from your_models import User  # Импортируйте вашу модель
        
        try:
            stmt = select(User.id).where(User.id == user_id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none() is not None
        except Exception as e:
            print(f"Ошибка при проверке пользователя: {e}")
            return False
    
    async def _handle_user_not_found(self, event: TelegramObject, user_id: int):
        """Обрабатывает случай, когда пользователь не найден"""
        if hasattr(event, 'answer'):
            await event.answer("❌ Вы не зарегистрированы в системе!")
    
    async def _handle_no_user_id(self, event: TelegramObject):
        """Обрабатывает случай, когда не удалось извлечь ID пользователя"""
        if hasattr(event, 'answer'):
            await event.answer("❌ Не удалось идентифицировать пользователя")