from flask_admin.contrib.sqla import ModelView
from flask_security import current_user
from flask import render_template, abort



class UserModelView(ModelView):
    column_list = ('username', 'email', 'active_role', 'active', 'interventions')
    column_labels = {'username': 'Username', 'email': 'Email Address', 'active_role': 'Role', 'active' : 'Active' , 'interventions' : 'Interventions'}
    column_filters = ('username', 'email', 'active_role.name', 'active', 'interventions.type')
  
    def is_accessible(self):
        if current_user.is_authenticated and current_user.active_role.name == 'Admin':
            return True
        else: 
            return abort(404)
        
    def _handle_view(self, name):
        if not self.is_accessible():
            return render_template('404.html')
