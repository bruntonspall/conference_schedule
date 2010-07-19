from google.appengine.ext import db
import time

class Event(db.Model):
    id = db.StringProperty()
    start_time = db.DateTimeProperty()
    day = db.DateProperty()
    duration = db.IntegerProperty() #In Minutes
    location = db.StringProperty()
    speaker = db.StringProperty()
    title = db.StringProperty()
    abstract = db.TextProperty()
    
    def to_dict(self):
        return {
        'id':self.id,
        'start_time':long(time.mktime(self.start_time.timetuple())*1000),
        'date':self.day.toordinal(),
        'duration':self.duration,
        'location':self.location,
        'speaker':self.speaker,
        'title':self.title,
        'abstract': self.abstract,
        }