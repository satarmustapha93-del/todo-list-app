# Little List

A small personal to-do list. Tasks, completion status, order, reminders, and timers are saved in `backend/todo.db` (SQLite).

## Start the app

1. Install **Python 3.11 or newer** from [python.org](https://www.python.org/downloads/). During setup, check **Add Python to PATH**.
2. Install the **Node.js LTS** version from [nodejs.org](https://nodejs.org/).
3. Close and reopen PowerShell (or restart your computer if Windows asks).
4. In File Explorer, double-click `start.ps1`. If Windows asks, choose **Run with PowerShell**. The first run installs the app's libraries, then opens the app in your browser.

If double-clicking is blocked, open PowerShell in this folder and run `.\start.ps1`.

The website runs at `http://localhost:5173`; its FastAPI service runs in the background at `http://localhost:8000`. Keep the two server windows open while using the app. Closing them stops the app; run `start.ps1` again to restart it. Your list remains in the SQLite database.

## Included

- Add, complete, delete, and reorder tasks
- Filter the list by all, to-do, and done
- Set a date and time reminder or a countdown timer for a task
- Local browser notifications for reminders while the app is open (the browser must allow notifications)
- FastAPI JSON API at `/api/tasks`
