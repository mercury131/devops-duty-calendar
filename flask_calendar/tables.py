from flask_table import Table, Col, LinkCol
class Results(Table):
    classes = ['customTable']
    id = Col('Id', show=False)
    name = Col('name')
    project = Col('project')
    phone = Col('phone')
    email = Col('email')
    edit = LinkCol('Edit', 'edit', url_kwargs=dict(id='id'))
    delete = LinkCol('Delete', 'delete', url_kwargs=dict(id='id'))

class Apitable(Table):
    classes = ['customTable']
    id = Col('Id', show=False)
    project = Col('project')
    api = Col('api')
    edit = LinkCol('Edit', 'edit_api_mapping', url_kwargs=dict(id='id'))
    delete = LinkCol('Delete', 'delete_api_mapping', url_kwargs=dict(id='id'))

class PMtable(Table):
    classes = ['customTable']
    id = Col('Id', show=False)
    manager = Col('manager')
    project = Col('project')
    email = Col('email')
    edit = LinkCol('Edit', 'edit_pm', url_kwargs=dict(id='id'))
    delete = LinkCol('Delete', 'delete_pm', url_kwargs=dict(id='id'))