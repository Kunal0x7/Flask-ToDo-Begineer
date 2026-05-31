from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ------------------ MODEL (OOP) ------------------ #
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    complete = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "complete": self.complete
        }


# ------------------ ROUTES (REST API) ------------------ #

# Get all tasks
@app.route('/todos', methods=['GET'])
def get_todos():
    try:
        todos = Todo.query.all()
        return jsonify([todo.to_dict() for todo in todos]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Create a new task
@app.route('/todos', methods=['POST'])
def create_todo():
    data = request.get_json()

    # Input validation
    if not data or 'title' not in data:
        return jsonify({"error": "Title is required"}), 400

    if not isinstance(data['title'], str) or data['title'].strip() == "":
        return jsonify({"error": "Invalid title"}), 400

    try:
        new_todo = Todo(title=data['title'])
        db.session.add(new_todo)
        db.session.commit()
        return jsonify(new_todo.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Database error"}), 500


# Update a task
@app.route('/todos/<int:id>', methods=['PUT'])
def update_todo(id):
    data = request.get_json()

    try:
        todo = Todo.query.get(id)
        if not todo:
            return jsonify({"error": "Task not found"}), 404

        if 'title' in data:
            if not isinstance(data['title'], str) or data['title'].strip() == "":
                return jsonify({"error": "Invalid title"}), 400
            todo.title = data['title']

        if 'complete' in data:
            if not isinstance(data['complete'], bool):
                return jsonify({"error": "Invalid status"}), 400
            todo.complete = data['complete']

        db.session.commit()
        return jsonify(todo.to_dict()), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Update failed"}), 500


# Delete a task
@app.route('/todos/<int:id>', methods=['DELETE'])
def delete_todo(id):
    try:
        todo = Todo.query.get(id)
        if not todo:
            return jsonify({"error": "Task not found"}), 404

        db.session.delete(todo)
        db.session.commit()
        return jsonify({"message": "Task deleted"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Delete failed"}), 500


# ------------------ MAIN ------------------ #
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)