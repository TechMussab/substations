from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy # type: ignore

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///substations.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Substation(db.Model):
    sr_no = db.Column(db.Integer, primary_key=True)
    substation_name = db.Column(db.String(100), nullable=False)
    full_name = db.Column(db.String(100), nullable=True)
    p_number = db.Column(db.String(50), nullable=True)
    breaker_name = db.Column(db.String(50), unique=True, nullable=False)
    feeding_station_details = db.Column(db.String(150), nullable=False)
    bay_name = db.Column(db.String(50), nullable=False)

# @app.before_first_request
# def init_db():
with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index():
    # init_db()
    substation_name = request.args.get('substation_name')
    breaker_name = request.args.get('breaker_name')
    
    # Base query to get all substations
    query = Substation.query
    
    # Apply filters based on user input
    if substation_name and breaker_name:
        query = query.filter(Substation.substation_name.like(f"%{substation_name}%"), Substation.breaker_name == breaker_name)
    elif substation_name:
        query = query.filter(Substation.substation_name.like(f"%{substation_name}%"))
    elif breaker_name:
        query = query.filter(Substation.breaker_name == breaker_name)

    # Fetch filtered or all records
    substations = query.all()
    
    return render_template('index.html', substations=substations)


@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        substation_name = request.form['substation_name']
        full_name = request.form['full_name']
        p_number = request.form['p_number']
        breaker_name = request.form['breaker_name']
        feeding_station_details = request.form['feeding_station_details']
        bay_name = request.form['bay_name']
        
        new_substation = Substation(
            substation_name=substation_name, 
            full_name=full_name, 
            p_number=p_number, 
            breaker_name=breaker_name, 
            feeding_station_details=feeding_station_details, 
            bay_name=bay_name
        )
        
        db.session.add(new_substation)
        db.session.commit()
        return redirect(url_for('index'))
    
    return render_template('create.html')


@app.route('/<int:sr_no>/edit', methods=('GET', 'POST'))
def edit(sr_no):
    substation = Substation.query.get_or_404(sr_no)
    if request.method == 'POST':
        substation.substation_name = request.form['substation_name']
        substation.full_name = request.form['full_name']
        substation.p_number = request.form['p_number']
        substation.breaker_name = request.form['breaker_name']
        substation.feeding_station_details = request.form['feeding_station_details']
        substation.bay_name = request.form['bay_name']
        
        db.session.commit()
        return redirect(url_for('index'))
    
    return render_template('edit.html', substation=substation)

@app.route('/<int:sr_no>/delete', methods=('POST',))
def delete(sr_no):
    substation = Substation.query.get_or_404(sr_no)
    db.session.delete(substation)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  
    app.run(debug=True)
