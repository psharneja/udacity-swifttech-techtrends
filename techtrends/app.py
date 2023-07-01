import sqlite3
import logging, sys
from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
import __init__

# Function to get a database connection.
# This function connects to database with the name `database.db`

def get_db_connection():
    connection = sqlite3.connect('database.db')
    global db_counter
    db_counter+=1
    connection.row_factory = sqlite3.Row
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      return render_template('404.html'), 404
    else:
        title=post['title']
        s="An existing article is retrieved, titled: {}".format(title)
        logger.info(s)
        return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    logger.info("The \"About Us\" page is retrieved.")
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            s="A new article is created. titled:{}".format(title)
            logger.info(s)
            return redirect(url_for('index'))

    return render_template('create.html')

# Define the healthz endpoint by checking if it connects with DB (with optional suggestions at page 9 )
@app.route('/healthz')
def healthz():
    connection = get_db_connection()
    try: 
        len(connection.execute('SELECT * FROM posts').fetchall())
        connection.close()
        response_message = "OK - healthy"
        response_code=200
    except:
        response_code=500
        response_message = "ERROR - unhealthy"
    return app.response_class(response=json.dumps({"result": response_message}),
                                  status=response_code,
                                  mimetype='application/json')


# Define the metrics endpoint 
@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    posts = len(connection.execute('SELECT * FROM posts').fetchall())
    connection.close()
    return app.response_class(response=json.dumps({"db_connection_count": db_counter, "post_count": posts}),
                                status=200,
                                mimetype= 'application/json')


@app.errorhandler(404)
def not_found(e):
    logger.info("A non-existing article is accessed and a 404 page is returned.")
    return render_template('404.html'), 404


# start the application on port 3111
if __name__ == "__main__":
    db_counter = 0
    logger=logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger_handler=logging.StreamHandler(sys.stdout)
    logger_handler.setLevel(logging.DEBUG)
    logger_formatter=logging.Formatter('%(levelname)s:%(name)s:%(asctime)s %(message)s', datefmt='%m/%d/%Y, %I:%M:%S')
    logger_handler.setFormatter(logger_formatter)
    logger.addHandler(logger_handler)
    logger_error_handler = logging.StreamHandler(sys.stderr)
    logger_error_handler.setLevel(logging.ERROR)
    logger_error_handler.setFormatter(logger_formatter)
    app.run(host='0.0.0.0', port='3112')
