"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/

This file creates your application.
"""

import json
import jwt
import os

from cryptography.x509 import load_pem_x509_certificate
from cryptography.hazmat.backends import default_backend

from flask import Flask, jsonify, abort, make_response, render_template, request, redirect, url_for
from flask_restful import Api

app = Flask(__name__)
api = Api(app)

from resources import RecordListResource
from resources import RecordResource

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'this_should_be_configured')

api.add_resource(RecordListResource, '/api/v1.0/records', endpoint='records')
api.add_resource(RecordResource, '/api/v1.0/records/<string:id>', endpoint='record')


FIREBASE_CERTS = [
"""-----BEGIN CERTIFICATE-----
MIIDHDCCAgSgAwIBAgIIK0ck42rCDQgwDQYJKoZIhvcNAQEFBQAwMTEvMC0GA1UE
AxMmc2VjdXJldG9rZW4uc3lzdGVtLmdzZXJ2aWNlYWNjb3VudC5jb20wHhcNMTcw
MTIzMDA0NTI2WhcNMTcwMTI2MDExNTI2WjAxMS8wLQYDVQQDEyZzZWN1cmV0b2tl
bi5zeXN0ZW0uZ3NlcnZpY2VhY2NvdW50LmNvbTCCASIwDQYJKoZIhvcNAQEBBQAD
ggEPADCCAQoCggEBALfpEll9QLmYHcpkGtr738I6BDyLR0ErFLuoKFmDEheSdma7
gbDyEY8FKgTclpswyE+fUoncNDzkEUbRefW77a/SHennUEyMAa1/YNbpwKB6g8tG
XSHJGm4MCsdJIIrPRNAibpLa2Ux3vqvIwMZlW1OxzrgpfhNkgGc8KIJbqbcRZfUB
Y+CfnvVzMFG5Ihnt7qFrXrjnqCMfR0NzO4pEFyx9RJc1uRqZHn90IFKZWw4YObrL
lVzlYxxpBXA9bRIJXo4PeaRi9cX/TOJ9TlJvxFazInU3Jfii6IWZZDsidqGoMGBU
CxzUNAxD0/xxCSQcW4C+RYAGacDwWBKAZd9X4kkCAwEAAaM4MDYwDAYDVR0TAQH/
BAIwADAOBgNVHQ8BAf8EBAMCB4AwFgYDVR0lAQH/BAwwCgYIKwYBBQUHAwIwDQYJ
KoZIhvcNAQEFBQADggEBAHVkDRWN5BUcAS4d+GSM6GGHFfbtYNF4OMLMLK/TFB+t
Ax8RyIfRgB2KSTZzGdHWN7eXNKAiQ3dFYsmEA+RYfHHgeunRgfirRDNplq7gguVO
ecsPDt8L5X4UURAg7jD+0107/3GxVDmgWgSf0aWhCKVlTHwBQ524MmgPHejrntkK
C1kQxKJKeXuYwGrRmrd5V2oSYI9Sip0A+ZYDMNy1M+I1fyzBN49+fyyVQ8cH4Y8U
jujyhg1IneI/GT2ZzBxTD95To/PpFW+vf6j4BzkyvLsEPy5a0AtYVlnrS1ntkhv5
BXP1ptUlsnwXNK0rHCO7Nc5D+tAtfnSI9+Ud+xJJfNM=
-----END CERTIFICATE-----
""",
"""-----BEGIN CERTIFICATE-----
MIIDHDCCAgSgAwIBAgIIfvLNDQFmu7YwDQYJKoZIhvcNAQEFBQAwMTEvMC0GA1UE
AxMmc2VjdXJldG9rZW4uc3lzdGVtLmdzZXJ2aWNlYWNjb3VudC5jb20wHhcNMTcw
MTI0MDA0NTI2WhcNMTcwMTI3MDExNTI2WjAxMS8wLQYDVQQDEyZzZWN1cmV0b2tl
bi5zeXN0ZW0uZ3NlcnZpY2VhY2NvdW50LmNvbTCCASIwDQYJKoZIhvcNAQEBBQAD
ggEPADCCAQoCggEBAPuVVWOP5HQNda/IDjkn9Hy1ttZUbuGLoop50iiyX4SlZGEQ
R5SIYFdlO4L3ahybGsivdNCRq/bhHybKbMotaC7Wywe9x8N76+Qvneva+IRZv+cY
gH2dRmQPB151h5IUgt3a+l+qRkaw5P/9cmAn8JVojKfWPjupcinx+OtPbJ/Yaqnt
PIzbUu3PLJrmnRL3ir0Rv61g1EmDqlWFvgmw6c40aPIsrj8fhXLOVxMPm1TPAbha
01A5/BDPXbF2nqexggXzciQiiVkOgSkGwu6tScu+IVbFtOuZav5APRiPrE57nNKk
+C7camznMluRlejf7f4rMo8TML4K5/9XeA4EMBcCAwEAAaM4MDYwDAYDVR0TAQH/
BAIwADAOBgNVHQ8BAf8EBAMCB4AwFgYDVR0lAQH/BAwwCgYIKwYBBQUHAwIwDQYJ
KoZIhvcNAQEFBQADggEBAH1LZp620SEBiLAwS7IgyC+hBRg0cAZ9V5VwVpAsrWcD
rDyR9ivhNttbX+W01LLocu8ZqbeZOaCJ0Y8atIKWNWgwrQK4iwoq0N0//qm/blZE
EupwNsNlpHAN1K44nwvuOurQMnWF5WfNRO14YDBRxPP9kn3z20TsUDLzmIEx5UEI
hmDin4NXeOwf830/UBZmhWNbtcCjNLgnaMpVLUKgr/CkvwpXBheUeYhbNwNKqxfL
iJTwBqBUoLG2q5Ui9dL4OEcj4kaHougAv4saUVDFZaMnKbKCtJXkO9FyptGi2Z0b
vQ6BwtV7XU6Qn9SIbks7WzCzeIig3e8mcbF21kfKb+E=
-----END CERTIFICATE-----
""",
"""-----BEGIN CERTIFICATE-----
MIIDHDCCAgSgAwIBAgIIU55h/c+ecaIwDQYJKoZIhvcNAQEFBQAwMTEvMC0GA1UE
AxMmc2VjdXJldG9rZW4uc3lzdGVtLmdzZXJ2aWNlYWNjb3VudC5jb20wHhcNMTcw
MTIyMDA0NTI2WhcNMTcwMTI1MDExNTI2WjAxMS8wLQYDVQQDEyZzZWN1cmV0b2tl
bi5zeXN0ZW0uZ3NlcnZpY2VhY2NvdW50LmNvbTCCASIwDQYJKoZIhvcNAQEBBQAD
ggEPADCCAQoCggEBAOTj/M4NC1KH2VZK0MXmktMQcEPvH+IdpG9B32DLewJyuME4
AJQKKUlNQw0WqM5Z1MsOuoa6H3OovHcQ3N1fxE/C7ukwKCf9fLbQWQcfYSj63OUO
XHhrjUbwa56h/T2rOQlwzaJtFVyePeX67kj71IUIU/sav6uORmW8GrcaMueKrcRK
EpdZEg6sO+uvmhDkBh0LXs+eOe0IcBj+z4T2AXRtzSqezA/9+/k/dvwLsNNDumEi
APXVnv2gatGtWddIXsRyC01gXmGL2dcXZRdtGCt/xNuuTD+NDYQRdNBQ7q5ko4Q4
f33kYHp7Cl51WB4QP69oqQW+5OtLkiMammXFntECAwEAAaM4MDYwDAYDVR0TAQH/
BAIwADAOBgNVHQ8BAf8EBAMCB4AwFgYDVR0lAQH/BAwwCgYIKwYBBQUHAwIwDQYJ
KoZIhvcNAQEFBQADggEBAJM66Szrg0k1QqxAtIl2SwobVfKu+ArJiCWtWHSk+zNV
1S4u8iLqixdnf0QYNk9A0Q8mkbL+CmZxHltZZQDbbtSPvbJVVtSW2otHQOkttDBe
ghB+X3PuONuxlSk/3AUu/Pld1fy09nCQpgr3k6lQ6RegUUGBKzxJAmxVTo9SIz6+
52VNa8++5Izl93orHCmhQ7UCBGFnW6IxemmdP0rpemCrkPRz8P/5VD99bQZHIuvz
Qy1mohjl/03gY5RG25QZyDk2X+RQhsr8gOXcGKBQ3YwVGUz0DQR7ecTLy8k+anIu
+2w9fdnorvl/P1in3NFvPFwYKw0NTu/7XvE3NT/0KF8=
-----END CERTIFICATE-----
""",
]
AUDIENCE = 'yb-splasher-7465c'


###
# Routing for your application.
###

@app.route('/')
def home():
     """Render website's home page."""
     return render_template('home.html')

@app.route('/firebase')
def firebase_index():
     """Render website's home page."""
     return render_template('firebase.html')

@app.route('/echo', methods=['POST'])
def echo():
  token = request.form['token']
  if not token:
    abort(401)
  for cert_str in FIREBASE_CERTS:
    cert_obj = load_pem_x509_certificate(cert_str, default_backend())
    public_key = cert_obj.public_key()
    try:
      payload = jwt.decode(token, public_key, audience=AUDIENCE)
      return json.dumps(payload)
    except Exception:
      pass
  abort(401)
    
  

# @app.route('/about/')
# def about():
#     """Render the website's about page."""
#     return render_template('about.html')


###
# The functions below should be applicable to all Flask apps.
###

# @app.route('/<file_name>.txt')
# def send_text_file(file_name):
#     """Send your static text file."""
#     file_dot_text = file_name + '.txt'
#     return app.send_static_file(file_dot_text)


# @app.after_request
# def add_header(response):
#     """
#     Add headers to both force latest IE rendering engine or Chrome Frame,
#     and also to cache the rendered page for 10 minutes.
#     """
#     response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
#     response.headers['Cache-Control'] = 'public, max-age=600'
#     return response


# @app.errorhandler(404)
# def page_not_found(error):
#     """Custom 404 page."""
#    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
