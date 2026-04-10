import argparse
import os
from app import create_app, db
from app.models.user import User
from config import Config

app = create_app()

def init_db():
    with app.app_context():
        db.create_all()
        # Add columns introduced after initial deployment (safe no-op if they exist)
        try:
            from sqlalchemy import text
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE nfts ADD COLUMN image_filename TEXT"))
                conn.commit()
        except Exception:
            pass  # Column already exists

    # Ensure upload directory exists
    upload_dir = os.path.join(app.root_path, 'static', 'nft_images')
    os.makedirs(upload_dir, exist_ok=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run a BueroChain node')
    parser.add_argument('--port', type=int, default=Config.NODE_PORT, help='Port to run the node on')
    args = parser.parse_args()

    init_db()
    app.run(host='0.0.0.0', port=args.port) 