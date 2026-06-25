"""
Запуск сервера и ботов кафе.
    python run.py          — запустить всё вместе
    python run.py server   — только веб-сервер
    python run.py customer — только клиентский бот
    python run.py worker   — только бот-работник
"""
import sys
import threading
from multiprocessing import Process

def run_server():
    from database import init_db
    from server import app
    init_db()
    print("🌐 Сервер запущен на http://0.0.0.0:8000")
    app.run(host="0.0.0.0", port=8000, debug=False, use_reloader=False)

def run_customer_bot():
    from bot_customer import main as customer_main
    print("☕ Клиентский бот запущен")
    customer_main()

def run_worker_bot():
    from bot_worker import main as worker_main
    print("🧑‍🍳 Бот-работник запущен")
    worker_main()

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"

    procs = []

    if mode in ("all", "server"):
        procs.append(Process(target=run_server, daemon=True))
    if mode in ("all", "customer"):
        procs.append(Process(target=run_customer_bot, daemon=True))
    if mode in ("all", "worker"):
        procs.append(Process(target=run_worker_bot, daemon=True))

    for p in procs:
        p.start()

    print(f"\n✅ Запущено процессов: {len(procs)}")
    print("Нажмите Ctrl+C для остановки\n")

    try:
        for p in procs:
            p.join()
    except KeyboardInterrupt:
        print("\n⏹ Остановка...")
        for p in procs:
            p.terminate()
