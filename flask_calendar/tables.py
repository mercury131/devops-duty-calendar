from flask_table import Table, Col, LinkCol
class Results(Table):
    id = Col('Id', show=False)
    name = Col('name')
    project = Col('project')
    phone = Col('phone')
    email = Col('email')
    edit = LinkCol('Edit', 'edit', url_kwargs=dict(id='id'))
    delete = LinkCol('Delete', 'delete', url_kwargs=dict(id='id'))

class Apitable(Table):
    id = Col('Id', show=False)
    project = Col('project')
    api = Col('api')
    edit = LinkCol('Edit', 'edit_api_mapping', url_kwargs=dict(id='id'))
    delete = LinkCol('Delete', 'delete_api_mapping', url_kwargs=dict(id='id'))