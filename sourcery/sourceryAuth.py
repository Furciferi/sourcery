"""

Based on: https://github.com/cherrypy/tools/blob/master/AuthenticationAndAccessRestrictions

"""
import base64
import re
import cherrypy 
import urllib
from passlib.hash import pbkdf2_sha256
import IPython

SESSION_KEY = '_sourcery_username'

def checkCredentials(username, password, usersList, contactStr = ""):
    """Verifies credentials for username and password.
    Returns None on success or a string describing the error on failure"""
    if usersList == None:
        return None
    for userDict in usersList:
        if username == userDict['name'] and pbkdf2_sha256.verify(password, userDict['hash']) == True:
            return None
    return u"Incorrect username or password. %s" % (contactStr)
    

def setEditPermissions(username, usersList):
    """Checks if the user is in the group that can edit pages.
    
    """
    if usersList == None:
        cherrypy.session['editPermission']=False
    else:
        foundUser=False
        for userDict in usersList:
            if username == userDict['name'] and userDict['role'] in ['editor']:
                cherrypy.session['editPermission']=True
                foundUser=True
        if foundUser == False:
            cherrypy.session['editPermission']=False
    
    
def check_auth(*args, **kwargs):
    """A tool that looks in config for 'auth.require'. If found and it
    is not None, a login is required and the entry is evaluated as a list of
    conditions that the user must fulfill"""
    conditions = cherrypy.request.config.get('auth.require', None)
    if conditions is not None:
        username = cherrypy.session.get(SESSION_KEY)
        if username:
            cherrypy.request.login = username
            for condition in conditions:
                # A condition is just a callable that returns true or false
                if not condition():
                    raise cherrypy.HTTPRedirect(cherrypy.request.script_name+"/login")
        else:
            raise cherrypy.HTTPRedirect(cherrypy.request.script_name+"/login")

####
#def check_auth(*args, **kwargs):
    #"""A tool that looks in config for 'auth.require'. If found and it
    #is not None, a login is required and the entry is evaluated as alist of
    #conditions that the user must fulfill"""
    #conditions = cherrypy.request.config.get('auth.require', None)
    ## format GET params
    #get_parmas = urllib.quote(cherrypy.request.request_line.split()[1])
    #if conditions is not None:
        #username = cherrypy.session.get(SESSION_KEY)
        #if username:
            #cherrypy.request.login = username
            #for condition in conditions:
                ## A condition is just a callable that returns true orfalse
                #if not condition():
                    ## Send old page as from_page parameter
                    #raise cherrypy.HTTPRedirect("/auth/login?from_page=%s" % get_parmas)
        #else:
            ## Send old page as from_page parameter
            #raise cherrypy.HTTPRedirect("/auth/login?from_page=%s" %get_parmas) 


####

cherrypy.tools.auth = cherrypy.Tool('before_handler', check_auth)

def require(*conditions):
    """A decorator that appends conditions to the auth.require config
    variable."""
    def decorate(f):
        if not hasattr(f, '_cp_config'):
            f._cp_config = dict()
        if 'auth.require' not in f._cp_config:
            f._cp_config['auth.require'] = []
        f._cp_config['auth.require'].extend(conditions)
        return f
    return decorate

# Conditions are callables that return True
# if the user fulfills the conditions they define, False otherwise
#
# They can access the current username as cherrypy.request.login
#
# Define those at will however suits the application.

def member_of(groupname):
    def check():
        # replace with actual check if <username> is in <groupname>
        return cherrypy.request.login == 'joe' and groupname == 'admin'
    return check

def name_is(reqd_username):
    return lambda: reqd_username == cherrypy.request.login

# These might be handy

def any_of(*conditions):
    """Returns True if any of the conditions match"""
    def check():
        for c in conditions:
            if c():
                return True
        return False
    return check

# By default all conditions are required, but this might still be
# needed if you want to use it inside of an any_of(...) condition
def all_of(*conditions):
    """Returns True if all of the conditions match"""
    def check():
        for c in conditions:
            if not c():
                return False
        return True
    return check


# Controller to provide login and logout actions

#class AuthController(object):
    
    #def on_login(self, username):
        #"""Called on successful login"""
    
    #def on_logout(self, username):
        #"""Called on logout"""
    
    #def get_loginform(self, username, msg="Enter login information", from_page="/"):
        #return """<html><body>
            #<form method="post" action="/auth/login">
            #<input type="hidden" name="from_page" value="%(from_page)s" />
            #%(msg)s<br />
            #Username: <input type="text" name="username" value="%(username)s" /><br />
            #Password: <input type="password" name="password" /><br />
            #<input type="submit" value="Log in" />
        #</body></html>""" % locals()
    
    #@cherrypy.expose
    #def login(self, username=None, password=None, from_page="/"):
        #if username is None or password is None:
            #return self.get_loginform("", from_page=from_page)
        
        #error_msg = check_credentials(username, password)
        #if error_msg:
            #return self.get_loginform(username, error_msg, from_page)
        #else:
            #cherrypy.session[SESSION_KEY] = cherrypy.request.login = username
            #self.on_login(username)
        #raise cherrypy.HTTPRedirect(from_page or "/")
    
    #@cherrypy.expose
    #def logout(self, from_page="/"):
        #sess = cherrypy.session
        #username = sess.get(SESSION_KEY, None)
        #sess[SESSION_KEY] = None
        #if username:
            #cherrypy.request.login = None
            #self.on_logout(username)
        #raise cherrypy.HTTPRedirect(from_page or "/")
    
