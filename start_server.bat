@echo off
echo ==============================================
echo  MOBIL HR ^& Sotiuvlar loyihasi Backend Serveri
echo ==============================================
echo.
echo Database: SQLite (sql_app.db)
echo FastAPI serveri (Uvicorn) ishga tushirilmoqda...
echo.

:: Agar VENV ishlamasa Global python da ishga turish
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
pause
