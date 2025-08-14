from flask import Blueprint, render_template, session, current_app

# Define the CMS blueprint
cms_blueprint = Blueprint('cms', __name__)

@cms_blueprint.route('')
def cms_home():
    current_lang = session.get('lang', current_app.config['BABEL_DEFAULT_LOCALE'])
    return render_template('index.html', current_lang=current_lang)

@cms_blueprint.route('/status')
def cms_status():
    return "CMS Status Page"
