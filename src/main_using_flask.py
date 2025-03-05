from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crm.db'
db = SQLAlchemy(app)

def create_case_id(length=8) -> str:
    return str(uuid.uuid4())[:length]

class Case(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.String(20), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    main_reaction = db.Column(db.String(50), nullable=True)
    main_response = db.Column(db.String(50), nullable=True)
    call_count = db.Column(db.Integer, default=0)
    comments = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/display_cases', methods=['GET'])
def get_cases():
    cases = Case.query.all()  # Fetch all cases from the database
    return render_template('display_cases.html', cases=cases)  # Pass the cases to the template

@app.route('/case/<case_id>', methods=['GET'])
def get_case(case_id):
    case = Case.query.filter_by(case_id=case_id).first()
    if case:
        return jsonify({
            'case_id': case.case_id,
            'phone_number': case.phone_number,
            'email': case.email,
            'main_reaction': case.main_reaction,
            'main_response': case.main_response,
            'call_count': case.call_count,
            'comments': case.comments,
            'timestamp': case.timestamp
        })
    return jsonify({'message': 'Case not found'}), 404

# Route to display the form
@app.route('/create_case', methods=['GET'])
def create_case_form():
    return render_template('create_case.html')

# Route to handle form submission (POST request)
@app.route('/create_case', methods=['POST'])
def create_case():

    try:
        # Get data from the form
        phone_number = request.form['phone_number']
        email = request.form['email']
        main_reaction = request.form['main_reaction']
        main_response = request.form['main_response']
        comments = request.form['comments']

        # Enforce character limits in Flask code
        if len(phone_number) > 50:
            return jsonify({'error': 'Phone number exceeds maximum length of 50 characters'}), 400
        if len(email) > 50:
            return jsonify({'error': 'Email exceeds maximum length of 50 characters'}), 400

        # Create a new case object
        new_case = Case(
            case_id=create_case_id(),
            phone_number=phone_number,
            email=email,
            main_reaction=main_reaction,
            main_response=main_response,
            comments=comments
        )

        # Add to the database
        db.session.add(new_case)
        db.session.commit()

        # Redirect to a confirmation page or back to the form
        return redirect(url_for('home'))

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/delete_case', methods=['GET'])
def delete_case_form():
    return render_template('delete_case.html')

@app.route('/case/<case_id>', methods=['DELETE'])
def delete_case(case_id):
    case = Case.query.filter_by(case_id=case_id).first()
    if case:
        db.session.delete(case)
        db.session.commit()
        return jsonify({'message': 'Case deleted successfully'})
    return jsonify({'message': 'Case not found'}), 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)


