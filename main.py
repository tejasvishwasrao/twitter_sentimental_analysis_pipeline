
##import packages
from flask import render_template, Flask

##create an instance of flask class for our app.
app = Flask(__name__)

#creates url
@app.route('/')

##Function to create first welcome page of TT.
def index():
    return "Welcome"

##run the application on local deployment server.
if __name__ == "__main__":
    app.run(host='0.0.0.0')
