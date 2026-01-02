from flask import Flask, request, redirect, jsonify
import string
import random

# Create Flask app first
app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Now import db and initialize it with the app
from models import db, URL
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()

def generate_short_code(length=6):
    #Generates a random short code
    characters = string.ascii_letters + string.digits # a-z, A-Z, 0-9
    while True: # keeps generating until we find unused code
        short_code = ''.join(random.choice(characters) for _ in range(length)) # picks 6 random characters and joins them together "P7b9xL"

        if not URL.query.filter_by(short_code=short_code).first(): # checks the code if it already exists throughout the database
            return short_code
        
@app.route('/shorten', methods = ['POST']) # when someone sends a POST request to run the function
def shorten_url(): # creates the shorten url
    data = request.get_json() # get's JSON data from request body

    # Validate input
    if not data or 'url' not in data:
        return jsonify({'error': 'URL is required'}), 400
    
    original_url = data['url']

    # Basic URl validation
    if not original_url.startswith(('https://', 'https://')):
        return jsonify({'error': 'Invalid URL format'}), 400
    
    # Check if URL already exists
    existing_url = URL.query.filter_by(original_url = original_url).first() #checks if we already shortened this URL
    if existing_url:
        return jsonify({
            'short_code' : existing_url.short_code,
            'short_url' : f'https://localhost:5000/{existing_url.short_code}',
            'original_url': original_url
        }), 200
    
    # Generate short code and create URL entry

    short_code = generate_short_code()
    new_url = URL(original_url = original_url, short_code=short_code)

    db.session.add(new_url) # Stages this new entry to be added
    db.session.commit() # actually saves it in the database

    return jsonify({ # returns with 201 status code meaning it worked!
        'short_code': short_code,
        'short_url': f'http://localhost:5000/{short_code}',
        'original_url': original_url
    }), 201

@app.route('/<short_code>') # short_code is a var, 
def redirect_to_url(short_code):
    """Redirect to the original URL"""
    url_entry = URL.query.filter_by(short_code=short_code).first() # look up short code in the database
    
    if not url_entry:
        return jsonify({'error': 'Short URL not found'}), 404 # return a 404 error if not found
    
    # Increment click count
    url_entry.click_count += 1
    db.session.commit() # save the updated click counter
    
    return redirect(url_entry.original_url) # redirects user's browser to the og URL


@app.route('/stats/<short_code>')
def get_stats(short_code):
    """Get statistics for a shortened URL"""
    url_entry = URL.query.filter_by(short_code=short_code).first()
    
    if not url_entry:
        return jsonify({'error': 'Short URL not found'}), 404
    
    return jsonify({
        'short_code': url_entry.short_code,
        'original_url': url_entry.original_url,
        'created_at': url_entry.created_at.isoformat(), # converts datetime to a string format that JSON can handle
        'click_count': url_entry.click_count
    }), 200



if __name__ == '__main__': # only runs if you execute this file directly
    app.run(debug=True) #enables debug mode,