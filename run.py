from backend import create_app

app = create_app()

print("✅ App created:", app.url_map)

if __name__ == '__main__':
    app.run()
