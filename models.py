# mongoengine database module
from mongoengine import *
from flask.ext.mongoengine.wtf import model_form

from datetime import datetime
import logging

class Comment(EmbeddedDocument):
	
	comment = StringField()
	timestamp = DateTimeField(default=datetime.now())
	
class Idea(Document):

	
	title = StringField(max_length=50, required=True)
	
	idea = StringField(required=True, verbose_name="VENT HERE")

	# Category is a list of Strings
	categories = StringField(max_length=50)
	

	# Comments is a list of Document type 'Comments' defined above
	comments = ListField( EmbeddedDocumentField(Comment) )

	# Timestamp will record the date and time idea was created.
	timestamp = DateTimeField(default=datetime.now())

# Create a Validation Form from the Idea model
IdeaForm = model_form(Idea)










