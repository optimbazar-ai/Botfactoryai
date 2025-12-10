from app import app

if __name__ == '__main__':
    # use_reloader=False - Flask debugger reloaderini o'chirish
    # Bu bot polling ikki marta ishga tushishini oldini oladi
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
