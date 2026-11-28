# FaceRecognitionAttendance

Система автоматической проверки посещаемости учащихся с помощью компьютерного зрения и распознавания лиц.

## Установка

Клонируйте репозиторий:

```bash
git clone https://github.com/Nikolay-L21/SchoolProject.git
cd SchoolProject
```

Создайте виртуальное окружение:

```bash
python -m venv .venv
```

Активируйте его в Windows:

```powershell
.venv\Scripts\activate
```

Установите зависимости:

```bash
pip install -r requirements.txt
```

## Запуск

**Запускать из корневой папки проекта (`SchoolProject`):**

```bash
python -m streamlit run web/app.py
```

После запуска приложение будет доступно по адресу:

http://localhost:8501

> Не запускайте `app.py` напрямую через `python web/app.py`. Это может привести к ошибке `ModuleNotFoundError: No module named 'web'`.

## Технологии

- Python
- OpenCV
- YuNet
- SFace
- SQLite
- Streamlit
