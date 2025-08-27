from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Annotated, List

app = FastAPI()

# database in-memory
database = []
users = []

# schemas

class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    role: str
    user_pk: int
    
    
class BaseVacancy(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    title: str
    description: str
    company: str
    created_at: datetime
    updated_at: datetime
    user_pk: int
    stack: list[str]


class CreateVacancy(BaseModel):
    title: str
    description: str
    company: str
    user_pk: int
    stack: list[str]


class ResponseVacancy(BaseVacancy):
    pk: int
    

class Reply(BaseModel):
    pass


# utils

async def get_data_vacancies(limit: int, offset: int):
    data_sorted = sorted(
        database,
        key=lambda x: (x.created_at, x.updated_at),
        reverse=True
    )
    return data_sorted[offset:offset + limit]
    

async def create_vacancy(obj: CreateVacancy):
    if not database:
        new_pk = 1
    else:
        data_sorted = sorted(database, key=lambda x: x.pk)
        new_pk = data_sorted[-1].pk + 1
    
    now = datetime.now()
    vacancy_data = obj.model_dump()
    vacancy_data.update({
        "pk": new_pk,
        "created_at": now,
        "updated_at": now
    })
    
    new_vacancy = ResponseVacancy(**vacancy_data)
    database.append(new_vacancy)
    return new_vacancy
    

async def get_user(user_pk: int):
    for user in users:
        if user.user_pk == user_pk:
            return user
    raise HTTPException(status_code=401, detail="Пользователь не найден")


async def get_hr_user(user: User = Depends(get_user)):
    if user.role != 'HR':
        raise HTTPException(status_code=403, detail="Стопе, создавать вакансию ты не можешь. Сорри")
    return user
    

async def send_reply(pk_vacancy: int):
    print(f'Отклик на вакансию {pk_vacancy} отправлен')

# view

@app.get('/vacancies', response_model=List[ResponseVacancy])
async def get_vacancies(limit: int = 5, offset: int = 0):
    return await get_data_vacancies(limit, offset)


@app.post('/reply/{vacancy_pk}')
async def reply(vacancy_pk: int):
    await send_reply(vacancy_pk)
    return {'status': 'OK'}


@app.post('/create-vacancy/{user_pk}')
async def create_record(
    user_pk: int, 
    record: CreateVacancy,
    user: Annotated[User, Depends(get_hr_user)]
):
    if user_pk != user.user_pk:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    await create_vacancy(record)
    return {'status': 'Success'}
    

if __name__ == '__main__':
    import uvicorn 
    
    uvicorn.run(app='main:app')
