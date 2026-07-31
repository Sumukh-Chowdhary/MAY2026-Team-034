from app import create_app
from app.utils.seed import seed_database

app = create_app()

if __name__ == '__main__':
    seed_database(app)
    app.run(host='127.0.0.1', port=5000, debug=True)
