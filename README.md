# FIRE-WS
FIRE WS coordinator. Backend of the WiFiCalling App. Responsible for interacting with the SIP server, authentication server &amp; billing system to provide to the WiFiCalling App with its backend through a RESTful API.

## General Architecture
The WS architecture is modular and implies a certain number of sub-repositories. It main parts are:
- The **Engine**. This is the main piece of this repository. It contains all the logic that's needed to accomplish the WiFiCalling needs. The first version of the engine is built directly under this repository, but the intention is to export it to a separate repo in the future, so different engines with different logics could be built and plugged.
- The **Configuration**. In order to orchestrate all the pieces of software involved in this architecture, an arbitrarily complex configuration file(s) will be needed. The first version of this config file will contain only a few optional things, defining the special use case that funds this project, but the intention is to complete it with more and more variables that could make the project adaptable to many other situations.
- The **Drivers**. This WS main objective is to coordinate the capabilities of 3 different pieces of software (SIP, auth, billing), but to connect to them, the Engine exposes 3 different interfaces that must be implemented in order to make the Engine work. Talking in Clean Architecture terms, the engine will act as the __domain__, there where all the business logic of the application is happening, while the drivers will act as __repositories__, so as the controllers or external sources of data.
 The **API**. This is the exposed RESTful API to the WiFiCalling App.


## Engine
Will implement the actual usecase of WiFiCalling. Things like:
- Vouchers lifecycle:
  - Generation
  - Activation
  - Depletion
- Users lifecycle:
   - User creation requests
   - User login
   - User profile modification
   - Connexion with SIP account
- SIP parameters definition
- Messaging system

It's also responsibility of the Engine to define the interfaces that the Drivers will implement. So it will contain at least 3 interfaces for SIP, Auth and Billing.


## Configuration
The typical INI or YAML file with different contexts and variables per context

## Drivers
Implementation of the interfaces defined in the Engine

## API
By now, the API is defined in [the MockServer repository](https://github.com/EyeSeeTea/FIRE-MockServer), and will be adapted during the implementation depending on the needs. This API needs to be coordinated with the WiFiCalling implementation.

## Webservice

### Development webservice server

From sources:

```
$ virtualenv --python /usr/bin/python3.6 .env
$ .env/bin/pip install -r requirements.txt
$ PYTHONPATH=. .env/bin/python bin/fire-dev-server -p 5005
$ curl -u USER:PASSWORD http://localhost:5005/users
```

### Run tests

```
$ .env/bin/python setup.py test
```

### Apache install

Add a virtual host to the webservice using a WSGI
gateway ([docs](http://flask.pocoo.org/docs/0.12/deploying/mod_wsgi/)). A template example:

```
<VirtualHost *:80>
  ServerName yourdomain.org

  WSGIPassAuthorization On
  WSGIDaemonProcess \
    fire-ws python-home=/path/to/.firews.env \
    python-path=/path/to/FIRE-WS
  WSGIProcessGroup fire-ws
  WSGIScriptAlias / /path/to/FIRE-WS/fire/api/wsgi.py

  <Directory /path/to/FIRE-WS/fire/api>
    <Files wsgi.py>
      Require all granted
    </Files>
  </Directory>
</VirtualHost>
```
