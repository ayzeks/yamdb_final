# Проект YaMDb
---
![Django-app workflow](https://github.com/ayzeks/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)
---
## Об авторе

Юлмухаметов Азат Хадиевич, студент Яндекс Практикума 36 когорта.
<a href='https://github.com/ayzeks'>Git провиль</a>

---
## Стек

python, Django, Pillow, pytest, django Rest framework, Docker, Ngenix, PostgreSQL

---
## О проекте

Проект YaMDb собирает отзывы *(Review)* пользователей на произведения *(Titles)*. 

Произведения делятся на категории: 

- «Книги»

- «Фильмы»

- «Музыка»

Список категорий *(Category)* может быть расширен администратором (например, можно добавить категорию «Изобразительное искусство» или «Ювелирка»).
Сами произведения в YaMDb не хранятся, здесь нельзя посмотреть фильм или послушать музыку.


В каждой категории есть произведения: книги, фильмы или музыка. Например, в категории «Книги» могут быть произведения «Винни-Пух и все-все-все» и «Марсианские хроники», а в категории «Музыка» — песня «Давеча» группы «Насекомые» и вторая сюита Баха.
Произведению может быть присвоен жанр *(Genre)* из списка предустановленных (например, «Сказка», «Рок» или «Артхаус»). 

Новые жанры может создавать только администратор.


Благодарные или возмущённые пользователи оставляют к произведениям текстовые отзывы *(Review)* и ставят произведению оценку в диапазоне от одного до десяти (целое число); из пользовательских оценок формируется усреднённая оценка произведения — рейтинг (целое число). На одно произведение пользователь может оставить только один отзыв.


---
## Как запустить проект
#### 1. Клонировать репозиторий. Переходим в дерикторию infra:

> <sub> git@github.com:ayzeks/infra_sp2.git </sub>
> <sub> cd infra/ </sub>

### 2. Cоздать и активировать виртуальное окружение:

> <sub> python3 -m venv env </sub>
> <sub> source env/Scripts/activate </sub>

### 3. Запустить приложение в контейнерах:

> <sub> docker-compose up -d --build </sub>

#### 4. Выполнить миграции:

> <sub> docker-compose exec web python manage.py migrate </sub> 

#### 5. Создать суперпользователя:

> <sub> docker-compose exec web python manage.py createsuperuser </sub> 

#### 6. Собрать статику:

> <sub> docker-compose exec web python manage.py collectstatic --no-input </sub> 

## Остановить проект:

> <sub> docker-compose down -v </sub> 
---
### Полная документация проекта:

> http://localhost/redoc

### Адрес сервера

> <sub> azik.ddns.net </sub>
