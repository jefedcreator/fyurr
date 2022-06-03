#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from sre_parse import State
import sys
from unicodedata import name
import dateutil.parser
import babel
from flask import Flask, jsonify, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy import ForeignKey, true
from forms import *
from flask_migrate import Migrate
import collections
collections.Callable = collections.abc.Callable
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app,db)


# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:hemid8th@localhost:5432/fyurr'

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable = False)
    city = db.Column(db.String(120), nullable =False)
    state = db.Column(db.String(120),nullable =False)
    address = db.Column(db.String(120),nullable =False)
    phone = db.Column(db.String(120),nullable =False)
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120), nullable = False)
    talent = db.Column(db.Boolean, default=False)
    description = db.Column(db.String(200))
    shows = db.relationship('Shows', backref='venue', lazy=False)

    def __repr__(self):
       return f"id {self.id},name{self.name},city{self.city} state{self.state} addres{self.address}phone{self.phone} image{self.image_link}facebook{self.facebook_link}"

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable =False)
    city = db.Column(db.String(120), nullable =False)
    state = db.Column(db.String(120),nullable =False)
    phone = db.Column(db.String(120), nullable =False)
    genres = db.Column(db.String(120), nullable =False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120), nullable = False)
    venue = db.Column(db.Boolean, default=False)
    description = db.Column(db.String(200))
    shows = db.relationship('Shows', backref='artist', lazy=False)

    def __repr__(self):
       return f"id {self.id},name{self.name},city{self.city} state{self.state} phone{self.phone} image{self.image_link}facebook{self.facebook_link}"

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Shows(db.Model):
  __tablename__ = "show"
  id = db.Column(db.Integer,primary_key = True)
  date = db.Column(db.DateTime, nullable = False)
  venue_id = db.Column(db.Integer, db.ForeignKey("venue.id"), nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey("artist.id"), nullable = False)

  def __repr__(self):
    return f"id {self.id},date{self.date},venue{self.venue} artist{self.artist}"

db.create_all()
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  real_areas = []

  areas = Venue.query.with_entities(Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()

  for area in areas:
    real_venues = []

    venues = Venue.query.filter_by(city=area.city).filter_by(state=area.state).all()

    for venue in venues:
      upcoming_shows = Shows.query.filter(Shows.venue_id == venue.id).filter(Shows.date > datetime.now()).all()

      real_venues.append({
          'id': venue.id,
          'name': venue.name,
          'num_upcoming_shows': len(upcoming_shows)
        })
    
    real_areas.append({
      'city': area.city,
      'state': area.state,
      'venues': real_venues
      })


  return render_template('pages/venues.html', areas=real_areas);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term=request.form.get('search_term')
    search = "%{}%".format(search_term.replace(" ", "\ "))

    real_venues = []

    venues = Venue.query.filter(Venue.name.match(search)).order_by('name').all()

    for venue in venues:
      upcoming_shows = Shows.query.filter(Shows.venue_id == venue.id).filter(Shows.date > datetime.now()).all()

      real_venues.append({
          'id': venue.id,
          'name': venue.name,
          'num_upcoming_shows': len(upcoming_shows)
        })

    response={
      "count": len(venues),
      "data": real_venues
    }

    return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  venue = Venue.query.filter(Venue.id == venue_id).first()

  future_shows = Shows.query.filter(Shows.venue_id == venue_id).filter(Shows.date > datetime.now()).all()

  if len(future_shows) > 0:
    upcoming_shows_arr = []

    for future_show in future_shows:
      artist = Artist.query.filter(Artist.id == future_show.artist).first()

      upcoming_shows_arr.append({
          'artist_id': artist.id,
          'artist_name': artist.name,
          'artist_image_link': artist.image_link,
          'start_time': str(future_show.date) 
        })

      venue.upcoming_shows = upcoming_shows_arr
      venue.upcoming_shows_count = len(upcoming_shows_arr)
    else:
      venue.upcoming_shows = []
      venue.upcoming_shows_count = 0

  past_shows = Shows.query.filter(Shows.venue_id == venue_id).filter(Shows.date < datetime.now()).all()

  if len(past_shows) > 0 :
    past_shows_arr = []

    for past_show in past_shows:
      artist = Artist.query.filter(Artist.id == past_show.artist).first()

      past_shows_arr.append(
        {
          'artist_id': artist.id,
          'artist_name': artist.name,
          'artist_image_link': artist.image_link,
          'start_time': str(future_show.date) 
        }
      )
      venue.upcoming_shows = past_shows_arr
      venue.upcoming_shows_count = len(past_shows_arr)
  else:
      venue.upcoming_shows = []
      venue.upcoming_shows_count = 0

  return render_template('pages/show_venue.html', venue=venue)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  body = {}
  form = VenueForm(request.form)
  name = form.name.data
  city = form.city.data
  state = form.state.data
  address = form.address.data
  phone = form.phone.data
  genres = form.genres.data
  image_link = form.image_link.data
  facebook_link = form.facebook_link.data
  website = form.website_link.data
  talent = form.seeking_talent.data
  description = form.seeking_description.data
  try:
    venue = Venue(
      name=name,
      city=city,
      state=state,
      address=address,
      phone=phone,
      genres=genres,
      image_link=image_link,
      facebook_link=facebook_link,
      website=website,
      talent=talent,
      description=description
    )
    db.session.add(venue)
    db.session.commit()
    body['name'] = venue.name
    body['city'] = venue.city
    body['state'] = venue.state
    body['address'] = venue.address
    body['phone'] = venue.phone
    body['genres'] = venue.genres
    body['image_link'] = venue.image_link
    body['facebook_link'] = venue.facebook_link
    body['talent'] = venue.talent
    body['description'] = venue.description
  except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
  finally:
    db.session.close()
  if error: 
    flash('An error occurred. Venue ' + str(name) + ' could not be listed.')
  if not error:
    flash('Venue ' + str(name) + ' was successfully listed!')

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  error=False
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    error=True
    db.session.rollback()
  finally:
    db.session.close()
  if not error:
    return jsonify({'Success': True})

  return redirect(url_for('pages/home.html'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  data = []
  artists = Artist.query.with_entities(Artist.id, Artist.name).order_by('id').all()

  for artist in artists:
    data.append({
        'id': artist.id,
        'name': artist.name
      })


  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  search_term=request.form.get('search_term')
  search = "%{}%".format(search_term.replace(" ", "\ "))

  artists = Artist.query.filter(Artist.name.match(search)).order_by('name').all()
  data = []
  for artist in artists:

    data.append(
      {
        'id': artist.id,
        'name': artist.name,
        'num_upcoming_shows': len(artist.shows)
      }
    )

  response={
    "count": len(artists),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id

  data = Artist.query.filter(Artist.id == artist_id).first()

  future_shows = Shows.query.filter(Shows.artist_id == artist_id).filter(Shows.date > datetime.now()).all()

  if len(future_shows) > 0:
    future_shows_arr = []

    for future_show in future_shows:
      venue = Venue.query.filter(Venue.id == future_show.venue).first()
      future_shows_arr.append({
        'venue_id': venue.id,
        'venue_name': venue.name,
        'venue_image_link': venue.image_link,
        'start_time': str(future_show.date)
      })
      data.upcoming_shows = future_shows_arr
      data.upcoming_shows_count = len(future_shows_arr)
  else:
      data.upcoming_shows = []
      data.upcoming_shows_count = 0

  past_shows = Shows.query.filter(Shows.artist_id == artist_id).filter(Shows.date < datetime.now()).all()

  if len(past_shows) > 0:
    past_shows_arr = []

    for past_show in past_shows:
      venue = Venue.query.filter(Venue.id == past_show.venue).first()
      past_shows_arr.append({
        'venue_id': venue.id,
        'venue_name': venue.name,
        'venue_image_link': venue.image_link,
        'start_time': str(past_show.date)
      })

      data.past_shows = past_shows_arr
      data.past_shows_count = len(past_shows_arr)
  else:
      data.past_shows = []
      data.past_shows_count = 0

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.filter(Artist.id == artist_id).first()

  form.name.data = artist.name
  form.genres.data = artist.genres
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.website_link.data = artist.website
  form.facebook_link.data = artist.facebook_link
  form.seeking_venue.data = artist.venue
  form.seeking_description.data = artist.description
  form.image_link.data = artist.image_link

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error = False
  try:
    artist = Artist.query.get(artist_id)
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    genres = request.form.getlist('genres')
    image_link = request.form['image_link']
    facebook_link = request.form['facebook_link']
    website = request.form['website']
    seeking_talent = True if 'seeking_talent' in request.form else False
    seeking_description = request.form['seeking_description']
    artist.name = name
    artist.city = city
    artist.state = state
    artist.phone = phone
    artist.genres = genres
    artist.image_link = image_link
    artist.facebook_link = facebook_link
    artist.website = website
    artist.talent = seeking_talent
    artist.description = seeking_description
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.filter(Venue.id == venue_id).first()
  form = VenueForm()
  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.genres.data = venue.genres
  form.image_link.data = venue.image_link
  form.facebook_link.data = venue.facebook_link
  form.website.data = venue.website
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  error = False
  try:
    venue = Venue.query.get(venue_id)
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    genres = request.form.getlist('genres')
    image_link = request.form['image_link']
    facebook_link = request.form['facebook_link']
    website = request.form['website']
    seeking_talent = True if 'seeking_talent' in request.form else False
    seeking_description = request.form['seeking_description']
    venue.name = name
    venue.city = city
    venue.state = state
    venue.phone = phone
    venue.genres = genres
    venue.image_link = image_link
    venue.facebook_link = facebook_link
    venue.website = website
    venue.talent = seeking_talent
    venue.description = seeking_description
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  body = {}
  form = ArtistForm(request.form)
  name = form.name.data
  city = form.city.data
  state = form.state.data
  phone = form.phone.data
  genres = form.genres.data
  image_link = form.image_link.data
  facebook_link = form.facebook_link.data
  website = form.website_link.data
  venue = form.seeking_venue.data
  description = form.seeking_description.data
  try:
    artist = Artist(
      name=name,
      city=city,
      state=state,
      phone=phone,
      genres=genres,
      image_link=image_link,
      facebook_link=facebook_link,
      website=website,
      venue = venue,
      description=description
    )
    db.session.add(artist)
    db.session.commit()
    body['name'] = artist.name
    body['city'] = artist.city
    body['state'] = artist.state
    body['phone'] = artist.phone
    body['genres'] = artist.genres
    body['image_link'] = artist.image_link
    body['facebook_link'] = artist.facebook_link
    body['venue'] = artist.venue
    body['description'] = artist.description
  except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
  finally:
    db.session.close()
  if error: 
    flash('An error occurred. Venue ' + name + ' could not be listed.')
  if not error:
    flash('Artist ' + name + ' was successfully listed!')

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = []
  shows = Shows.query.all()

  for show in shows:
    data.append({
          'venue_name': show.venue.name,
          'artist_name': show.artist.name,
          'artist_image_link': show.artist.image_link,
          'venue_id': show.venue_id,
          'artist_id': show.artist_id,
          'start_time':str(show.date)
    })
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  form = ShowForm(request.form)
  artist = form.artist_id.data
  venue = form.venue_id.data
  date = form.start_time.data
  try:
      shows = Shows(date=date, venue_id=venue, artist_id=artist)
      db.session.add(shows)
      db.session.commit() 
  except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()
  if error:
      flash('An error occurred. Show could not be listed.')
  if not error:
      flash('Show was successfully listed!')

  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
