import os, datetime
import re
from flask import Flask, request, render_template, redirect, abort, flash, json

from unidecode import unidecode

# mongoengine database module
from flask.ext.mongoengine import MongoEngine


app = Flask(__name__) # create our flask app
app.config['CSRF_ENABLED'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')




# --------- Database Connection ---------
# MongoDB connection to MongoLab's database
app.config['MONGODB_SETTINGS'] = {'HOST':os.environ.get('MONGOLAB_URI'),'DB': 'venthere'}
app.logger.debug("Connecting to MongoLabs")
db = MongoEngine(app) # connect MongoEngine with Flask App

# import data models
import models

# hardcoded categories for the checkboxes on the form
categories = ['PEOPLE','NYC','THE_WAY_THINGS_ARE_NOW','SHIT_IS_FUCKED_UP_AND_BULLSHIT']

# --------- Routes ----------
# this is our main pagex

@app.route("/", methods =['GET', 'POST'])
def index():

	idea_form = models.IdeaForm(request.form)
	# render the template
	if request.method == "POST":

		idea = models.Idea()
		idea.title = request.form.get('title','no title')
		idea.idea = request.form.get('idea','')
		idea.categories = request.form.get('categories')

		idea.save() # save it

		# redirect to the new idea page
		#return redirect('/ideas/%s' % idea.slug)
		return redirect('/')

	else:

		if request.method=="POST" and request.form.getlist('categories'):
			for c in request.form.getlist('categories'):
				idea_form.categories.append_entry(c)


		# render the template
		templateData = {
			'ideas' : models.Idea.objects(),
			'categories' : categories,
			'form' : idea_form
		}
		
		# app.logger.debug(templateData)

		return render_template("all_vents.html", **templateData)

# TRYING THIS OUT
# TRYING THIS OUT
# TRYING THIS OUT
# @app.route("/all_vents", methods=['GET','POST'])
# def addvent():

# 	idea_form = models.IdeaForm(request.form)

# 	# if form was submitted and it is valid...
# 	if request.method == "POST" and idea_form.validate():
	
# 		# if request.form['submit'] =="Test":
# 		# get form data - create new idea
# 		idea = models.Idea()
		
# 		idea.title = request.form.get('title','no title')
		
# 		idea.idea = request.form.get('idea','')
# 		idea.categories = request.form.get('categories')

		
# 		idea.save() # save it

# 		# redirect to the new idea page
# 		#return redirect('/ideas/%s' % idea.slug)
# 		return redirect('/')

# 	else:

# 		# for form management, checkboxes are weird (in wtforms)
# 		# prepare checklist items for form
# 		# you'll need to take the form checkboxes submitted
# 		# and idea_form.categories list needs to be populated.
# 		if request.method=="POST" and request.form.getlist('categories'):
# 			for c in request.form.getlist('categories'):
# 				idea_form.categories.append_entry(c)


# 		# render the template
# 		templateData = {
# 			'ideas' : models.Idea.objects(),
# 			'categories' : categories,
# 			'form' : idea_form
# 		}
		
# 		# app.logger.debug(templateData)

# 		return render_template("add_vent.html", **templateData)
# ENDING THIS TRY HERE


# CAN I ADD ALLVENTS here to apply as a second route?
@app.route("/addvent", methods=['GET','POST'])
def addvent():

	idea_form = models.IdeaForm(request.form)



	# if form was submitted and it is valid...
	if request.method == "POST" and idea_form.validate():
	
		# if request.form['submit'] =="Test":
		# get form data - create new idea
		idea = models.Idea()
		
		idea.title = request.form.get('title','no title')
		
		idea.idea = request.form.get('idea','')
		idea.categories = request.form.get('categories')

		
		idea.save() # save it

		# redirect to the new idea page
		#return redirect('/ideas/%s' % idea.slug)
		return redirect('/')

	else:

		# for form management, checkboxes are weird (in wtforms)
		# prepare checklist items for form
		# you'll need to take the form checkboxes submitted
		# and idea_form.categories list needs to be populated.
		if request.method=="POST" and request.form.getlist('categories'):
			for c in request.form.getlist('categories'):
				idea_form.categories.append_entry(c)


		# render the template
		templateData = {
			'ideas' : models.Idea.objects(),
			'categories' : categories,
			'form' : idea_form
		}
		
		# app.logger.debug(templateData)

		return render_template("add_vent.html", **templateData)

# Display all ideas for a specific category
@app.route("/category/<cat_name>")
def by_category(cat_name):

	# try and get ideas where cat_name is inside the categories list
	try:
		ideas = models.Idea.objects(categories=cat_name)

		for idea in ideas:
			app.logger.debug(idea.title)

	# not found, abort w/ 404 page
	except:
		abort(404)

	# prepare data for template
	templateData = {
		'current_category' : {
			
			'name' : cat_name.replace('_',' ')
		},
		'ideas' : ideas,
		'categories' : categories
	}

	# render and return template
	return render_template('category_listing.html', **templateData)


@app.route("/ideas/<idea_id>")
def idea_display(idea_id):

	# get idea by idea_id
	try:
		ideasList = models.Idea.objects(id=idea_id)
	except:
		abort(404)

	# prepare template data
	templateData = {
		'idea' : ideasList[0]
	}

	# render and return the template
	return render_template('idea_entry.html', **templateData)

@app.route("/ideas/edit/<idea_id>", methods=['GET','POST'])
def idea_edit(idea_id):

	if request.method == 'POST':
		try:
			idea = models.Idea.objects.get(id=idea_id)
		except:
			abort(404)

		# populate the IdeaForm with incoming form data
		ideaForm = models.IdeaForm(request.form)

		if ideaForm.validate():
			updateData = {
				'set__title' : request.form.get('title'),
				# 'set__creator' : request.form.get('creator'),
				'set__idea' : request.form.get('idea'),
				'set__categories' : request.form.getlist('categories')
			}
			idea.update(**updateData) # update the idea
			
			# flash message
			flash('Idea was updated')

			# redirect to the GET method of the current page
			return redirect('/ideas/edit/%s' % idea.id )

		else:

			# error display form with errors
			templateData = {
				'idea_id' : idea.id,
				'form' : ideaForm,
				'categories' : categories
			}

			return render_template('idea_edit.html', **templateData)

	else:
		# get the idea convert it to the model form, this prepopulates the form
		try:
			idea = models.Idea.objects.get(id=idea_id)
			ideaForm = models.IdeaForm(obj=idea)

		except:
			abort(404)

		templateData = {
			'idea_id' : idea.id,
			'form' : ideaForm,
			'categories' : categories
		}

		return render_template('idea_edit.html', **templateData)

# This route is from the jinja template

@app.route("/ideas/<idea_id>/comment", methods=['POST'])
def idea_comment(idea_id):

	# name = request.form.get('name')
	comment = request.form.get('comment')

	if  comment == '':
		# no  comment, return to page
		return redirect(request.referrer)


	#get the idea by id
	try:
		idea = models.Idea.objects.get(id=idea_id)
	except:
		# error, return to where you came from
		return redirect(request.referrer)


	# create comment
	comment = models.Comment()
	# comment.name = request.form.get('name')
	comment.comment = request.form.get('comment')
	
	# append comment to idea
	idea.comments.append(comment)

	# save it
	idea.save()

	return redirect('/ideas/%s' % idea.id)

from flask import jsonify


@app.route('/data/ideas')
def data_ideas():

	# query for the ideas - return oldest first, limit 10
	ideas = models.Idea.objects().order_by('+timestamp').limit(10)

	if ideas:

		# list to hold ideas
		public_ideas = []

		#prep data for json
		for i in ideas:
			tmpIdea = ideaToDict(i)
			
			# insert idea dictionary into public_ideas list
			public_ideas.append( tmpIdea )

		# prepare dictionary for JSON return
		data = {
			'status' : 'OK',
			'ideas' : public_ideas
		}

		# jsonify (imported from Flask above)
		# will convert 'data' dictionary and set mime type to 'application/json'
		return jsonify(data)

	else:
		error = {
			'status' : 'error',
			'msg' : 'unable to retrieve ideas'
		}
		return jsonify(error)

@app.route('/data/ideas/<id>')
def data_idea(id):
		

	# query for the ideas - return oldest first, limit 10
	try:
		idea = models.Idea.objects.get(id=id)
		if idea:
			tmpIdea = ideaToDict(idea)
			
			# prepare dictionary for JSON return
			data = {
				'status' : 'OK',
				'idea' : tmpIdea
			}

			# jsonify (imported from Flask above)
			# will convert 'data' dictionary and set mime type to 'application/json'
			return jsonify(data)

	except:
		error = {
			'status' : 'error',
			'msg' : 'unable to retrieve ideas'
		}
		return jsonify(error)





#SEARCH FUNCTION APP
# @app.route('/search', methods=['GET','POST'])
# def search():

	# Put this below 'try:' - ideas = models.Idea.objects(title__icontains='')
# This was lifted from data_idea app.route //this was on line 401 return jsonify(data)

# 999999999999999999999999999
# 999999999999999999999999999


# @app.route('/search', methods=['GET','POST'])
# def search(user_search):




# 	try:
		
# 		ideas = models.Idea.objects(title__icontains=request.form.get('dummy'))
		
# 		if ideas:
# 			tmpIdea = ideaToDict(idea)
			
# 			# prepare dictionary for JSON return
# 			data = {
# 				'status' : 'OK',
# 				'idea' : tmpIdea
# 			}

# 			# jsonify (imported from Flask above)
# 			# will convert 'data' dictionary and set mime type to 'application/json'
			
# 			# render the template
# 		templateData = {
# 			'ideas' : models.Idea.objects()
# 			#,
# 			# 'categories' : categories,
# 			# 'form' : idea_form
# 		}
		
# 		# app.logger.debug(templateData)

# 		return render_template("search.html", **templateData)

# 			# return redirect('/search/%s' % idea.id)
# 	except:
# 		error = {
# 			'status' : 'error',
# 			'msg' : 'unable to retrieve ideas'
# 		}
# 		return jsonify(error)

# 99999999999
# 99999999999
@app.route("/search", methods=['POST','GET'])
def search():
	templateData = {}
	if request.method == 'POST' :
	# print request.form
	# get idea by idea_id 
		try:
			query = request.form.get("query")
			#ideasList = models.Idea.objects(Q(title__icontains=query) | Q(idea__icontains=query)) # doesn't work
			#ideasList = models.Idea.objects(title__icontains=query)
			#ideasList = models.Idea.objects(idea__icontains=query)
			#ideasList.extend(models.Idea.objects())
			ideasSet1 = set(models.Idea.objects(title__icontains=query))
			ideasSet2 = set(models.Idea.objects(idea__icontains=query))
			ideasSet = ideasSet1 | ideasSet2
		except:
			abort(404)

		# prepare template data
		templateData = {
			'ideas' : ideasSet
		}	
		# render and return the template
		return render_template('search.html', **templateData)

	else: 
		return render_template('search_info.html', **templateData)










@app.route('/about')
def about():

	return render_template('about.html'), 404

@app.route('/contact')
def contact():

	return render_template('contact.html'),404



@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


def ideaToDict(idea):
	# create a dictionary
	tmpIdea = {
		'id' : str(idea.id),
		# 'creator' : idea.creator,
		'title' : idea.title,
		'idea' : idea.idea,
		'timestamp' : str( idea.timestamp )
	}

	# comments / our embedded documents
	tmpIdea['comments'] = [] # list - will hold all comment dictionaries
	
	# loop through idea comments
	for c in idea.comments:
		comment_dict = {
			'name' : c.name,
			'comment' : c.comment,
			'timestamp' : str( c.timestamp )
		}

		# append comment_dict to ['comments']
		tmpIdea['comments'].append(comment_dict)

	return tmpIdea


# slugify the title 
# via http://flask.pocoo.org/snippets/5/
_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')
def slugify(text, delim=u'-'):
	"""Generates an ASCII-only slug."""
	result = []
	for word in _punct_re.split(text.lower()):
		result.extend(unidecode(word).split())
	return unicode(delim.join(result))



# --------- Server On ----------
# start the webserver
if __name__ == "__main__":
	app.debug = True
	
	port = int(os.environ.get('PORT', 5000)) # locally PORT 5000, Heroku will assign its own port
	app.run(host='0.0.0.0', port=port)





	