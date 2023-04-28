from webapp import app
import webapp.database as db
# General API file


@app.route('/api/get_users')
def get_users():
    return db.get_users()
