## Final Project for Electronic Engineering 

Web application in process for final engineering project.

## Documentation

## HOW TO RUN THE APLICATION

#### CLONE

To run the project you have to clone the GitHub repository using HTTPS:

``https://github.com/pitulujan/proyecto.git``


Clone the repository inside a blank folder in a path you have friendly access.

#### REQUIREMENTS

Install virtual environment `python3 -m venv venv` and then activate it using `source venv/bin/activate`

You then have to install all the application requirements before you can run it using `pip install -r requirements.txt`

Comment line  `<script src="{{bootstrap_find_resource('jquery.js', cdn='jquery')}}"></script>` from `~/proyecto/venv/lib/python3.6/site-packages/flask_bootstrap/templates/bootstrap`

#### TO RUN

Go to `.../venv/lib/python3.X/site-packages/flask_bootstrap/templates/bootstrap/base.html` and comment the following line : `<script src="{{bootstrap_find_resource('jquery.js', cdn='jquery')}}"></script>`

To run the application `python proyecto.py` 

User : Admin

Password : admin

Note : The application is being desing to run on mobile devices, we still need to fix the views for a more friendly experience on larger screens.

