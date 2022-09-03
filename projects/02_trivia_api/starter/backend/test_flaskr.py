import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format("caryn", "caryn", "localhost:5432", self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {"question": "New Question?", "answer": "The answer", "difficulty": 9000, "category": 4}

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    Positive Testing
    """
    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["categories"]))
        self.assertTrue(data["total_categories"])

    def test_get_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data["questions"]))
        self.assertTrue(data["totalQuestions"])
        self.assertTrue(len(data["categories"]))

    def test_get_category_questions(self):
        res = self.client().get("/questions/2/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data["questions"]))
        self.assertTrue(data["totalQuestions"])
        self.assertTrue(data["currentCategory"])
        
    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get("/questions?page=300")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource Not Found")

    def test_get_category_questions(self):
        res = self.client().get("/questions/2000/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource Not Found")

    def test_create_new_question(self):
        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_delete_question(self):
        res = self.client().delete("/questions/26")
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == 26).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(question, None)

    def test_create_quizz_questions(self):
        res = self.client().post("/quizzes", json={"previous_questions": [1,2,3],"quiz_category":{"type":"click","id":0}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["question"])


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()