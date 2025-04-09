from app import create_app, db

app = create_app()

# This makes sure we create tables with the correct DB config
if __name__ != '__main__':
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    app.run()
