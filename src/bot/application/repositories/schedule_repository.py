from datetime import datetime
from typing import list


class ScheduleRepository:
    def __init__(self, mongo_db):
        self.collection = mongo_db.db['schedule']

    async def get_schedule(self) -> dict:
        """
        Получает расписание (документ с active_inspectors и free_inspectors)
        """
        schedule = self.collection.find_one({})
        if not schedule:
            # Создаём расписание если его нет
            result = self.collection.insert_one({
                "active_inspectors": [],
                "free_inspectors": []
            })
            schedule = self.collection.find_one({"_id": result.inserted_id})
        schedule["_id"] = str(schedule["_id"])
        return schedule

    async def add_active_inspection(self, data: dict) -> dict:
        """
        Добавляет активную инспекцию в расписание
        data: {
            "date": datetime.now(),
            "area": 1,
            "cleaner_id": "cleaner_123",
            "inspector_id": "inspector_456",
            "checklist_id": "checklist_789",
            "status": "planned"
        }
        """
        inspection = {
            "date": data.get("date", datetime.now()), #!!!
            "area": data.get("area"),
            "cleaner_id": data.get("cleaner_id"),
            "inspector_id": data.get("inspector_id"),
            "checklist_id": data.get("checklist_id"),
            "status": data.get("status", "planned"),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }

        result = self.collection.find_one_and_update(
            {},
            {"$push": {"active_inspectors": inspection}},
            return_document=True,
            upsert=True
        )
        result["_id"] = str(result["_id"])
        return result

    async def get_active_inspections(self) -> list:
        """
        Получает все активные инспекции
        """
        schedule = self.collection.find_one({})
        if not schedule:
            return []
        return schedule.get("active_inspectors", [])

    async def get_active_inspections_by_area(self, area: int) -> list:
        """
        Получает активные инспекции по области
        """
        inspections = await self.get_active_inspections()
        return [insp for insp in inspections if insp.get("area") == area]

    async def get_active_inspections_by_status(self, status: str) -> list:
        """
        Получает активные инспекции по статусу (planned/completed)
        """
        inspections = await self.get_active_inspections()
        return [insp for insp in inspections if insp.get("status") == status]

    async def get_active_inspections_by_inspector(self, inspector_id: str) -> list:
        """
        Получает активные инспекции по инспектору
        """
        inspections = await self.get_active_inspections()
        return [insp for insp in inspections if insp.get("inspector_id") == inspector_id]

    async def get_active_inspections_by_cleaner(self, cleaner_id: str) -> list:
        """
        Получает активные инспекции по уборщику
        """
        inspections = await self.get_active_inspections()
        return [insp for insp in inspections if insp.get("cleaner_id") == cleaner_id]

    async def update_inspection_status(self, checklist_id: str, status: str) -> dict:
        """
        Обновляет статус инспекции (planned -> completed)
        """
        result = self.collection.find_one_and_update(
            {"active_inspectors.checklist_id": checklist_id},
            {
                "$set": {
                    "active_inspectors.$.status": status,
                    "active_inspectors.$.updated_at": datetime.now()
                }
            },
            return_document=True
        )
        if not result:
            raise ValueError(f"Инспекция с checklist_id={checklist_id} не найдена")
        result["_id"] = str(result["_id"])
        return result

    async def remove_active_inspection(self, checklist_id: str) -> dict:
        """
        Удаляет активную инспекцию из расписания
        """
        result = self.collection.find_one_and_update(
            {},
            {"$pull": {"active_inspectors": {"checklist_id": checklist_id}}},
            return_document=True
        )
        if not result:
            raise ValueError(f"Инспекция с checklist_id={checklist_id} не найдена")
        result["_id"] = str(result["_id"])
        return result

    async def add_free_inspector(self, inspector_id: str) -> dict:
        """
        Добавляет свободного инспектора
        """
        result = self.collection.find_one_and_update(
            {},
            {"$addToSet": {"free_inspectors": inspector_id}},
            return_document=True,
            upsert=True
        )
        result["_id"] = str(result["_id"])
        return result

    async def get_free_inspectors(self) -> list:
        """
        Получает список свободных инспекторов
        """
        schedule = self.collection.find_one({})
        if not schedule:
            return []
        return schedule.get("free_inspectors", [])

    async def remove_free_inspector(self, inspector_id: str) -> dict:
        """
        Удаляет инспектора из списка свободных
        """
        result = self.collection.find_one_and_update(
            {},
            {"$pull": {"free_inspectors": inspector_id}},
            return_document=True
        )
        if not result:
            raise ValueError(f"Свободный инспектор {inspector_id} не найден")
        result["_id"] = str(result["_id"])
        return result

    async def move_inspection_to_free(self, checklist_id: str) -> dict:
        """
        Перемещает инспекцию из активных и добавляет инспектора в свободные
        """
        # Получаем инспекцию
        schedule = self.collection.find_one(
            {"active_inspectors.checklist_id": checklist_id}
        )
        if not schedule:
            raise ValueError(f"Инспекция с checklist_id={checklist_id} не найдена")

        # Находим инспектора
        active_inspections = schedule.get("active_inspectors", [])
        inspector_id = None
        for insp in active_inspections:
            if insp.get("checklist_id") == checklist_id:
                inspector_id = insp.get("inspector_id")
                break

        # Удаляем из активных
        await self.remove_active_inspection(checklist_id)

        # Добавляем в свободные
        if inspector_id:
            await self.add_free_inspector(inspector_id)

        return await self.get_schedule()

    async def get_inspection_by_checklist_id(self, checklist_id: str) -> dict:
        """
        Получает инспекцию по checklist_id
        """
        schedule = self.collection.find_one(
            {"active_inspectors.checklist_id": checklist_id}
        )
        if not schedule:
            raise ValueError(f"Инспекция с checklist_id={checklist_id} не найдена")

        for insp in schedule.get("active_inspectors", []):
            if insp.get("checklist_id") == checklist_id:
                return insp

        raise ValueError(f"Инспекция с checklist_id={checklist_id} не найдена")
