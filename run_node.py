import argparse
from app import create_app, db
from app.models.user import User

app = create_app()

def init_db():
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run a BueroChain node')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the node on')
    args = parser.parse_args()

    init_db()
    app.run(host='0.0.0.0', port=args.port) 