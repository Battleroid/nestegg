from nestegg import db, app

app.config.from_object('config.Development')
db.drop_all()
db.create_all()
