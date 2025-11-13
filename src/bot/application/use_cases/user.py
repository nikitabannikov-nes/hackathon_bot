from src.bot.main.keyboards.keyboards import get_admin_kb, get_inspector_kb, get_user_kb
from src.bot.domain.entities.user import User
from src.bot.infrastructure.db.postgra_client import postgra_session



class UserUseCases():
    def __init__(self, user_repository):
        self._user_repository = user_repository


    async def start_comand(self, message):

        user_id = message.from_user.id

        async with postgra_session as session:     
            welcome_text = "Добро пожаловать! Ваша роль: "

            if not self._user_repository.exists(session, user_id):
                return message.answer(text="Попросите администратора добавить вас в базу данных сотрудников")
            user_role = self._user_repository.get_user_role(session, user_id)
        
            if user_role == 'admin':
                await message.answer(
                    f"{welcome_text} Администратор", 
                    reply_markup=get_admin_kb()
                )
            elif user_role == 'checker':
                await message.answer(
                    f"{welcome_text} Проверяющий", 
                    reply_markup=get_inspector_kb()
                )
            elif user_role == 'user':
                await message.answer(
                    f"{welcome_text} Пользователь", 
                    reply_markup=get_user_kb()
                )  
            else:
                message.answer(text="Ошибка доступа")    



    async def create_user(self, id: str):
        async with postgra_session as session:     
            if not self._user_repository.exists(session, id) or self._user_repository.get_user_role(session, id) != "admin":
                return "Ошибка доступа"
            else: ...
                

            


    async def delete_user(): ...

    async def send_schedul(): ...

    async def add_check_list(): ...

    async def get_my_analitic(): ...