from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crm.db'
db = SQLAlchemy(app)

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
    return "Flask CRM API is running! Use the correct endpoints."

@app.route('/cases', methods=['GET'])
def get_cases():
    cases = Case.query.all()
    return jsonify([{ 'case_id': c.case_id, 'phone_number': c.phone_number, 'email': c.email, 'timestamp': c.timestamp } for c in cases])

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

@app.route('/case', methods=['POST'])
def create_case():
    data = request.json
    new_case = Case(
        case_id=data['case_id'],
        phone_number=data['phone_number'],
        email=data['email'],
        main_reaction=data.get('main_reaction'),
        main_response=data.get('main_response'),
        call_count=data.get('call_count', 0),
        comments=data.get('comments')
    )
    db.session.add(new_case)
    db.session.commit()
    return jsonify({'message': 'Case created successfully'}), 201

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
