from app import create_app  # make sure you have a create_app function

app = create_app()

if __name__ == "__main__":
    app.run(debug=False)
