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
        self.database_name = os.environ['DBTEST_NAME']
        self.database_path = 'postgresql://{}:{}@{}/{}'.format(os.environ['DB_USER'], os.environ['DB_PASSWORD'], os.environ['DB_HOST'], self.database_name)

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
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
    
    def test_get_categories_failure(self):
        res = self.client().get("/categories/1")
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 404)
        self.assertFalse(data["success"])

    def test_get_all_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))

    def test_get_valid_questions_pagination(self):
        res = self.client().get("/questions?page=2")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))

    def test_get_invalid_questions_pagination(self):
        res = self.client().get("/questions?page=100")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")

    def test_delete_valid_question(self):
        get_question = Question.query.first()
        self.assertNotEqual(get_question, None)
        res = self.client().delete("/questions/"+
        str(get_question.id))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])

    def test_delete_invalid_question(self):
        res = self.client().delete("/questions/12032")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_create_question_with_valid_details(self):
        add_question = {"question": "new questions", "answer": "Yes","difficulty": "3", "category": "5"}
        res = self.client().post("/questions", json=add_question)
        data = json.loads(res.data)

        post_new_question = Question.query.all()
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(data["new_question"])
        self.assertTrue(data["total_questions"])

    def test_create_question_invalid_details(self):
        new_question = {"answer": "answer", "difficulty": 7, "category": 9}
        res = self.client().post("/questions", json=new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertFalse(data["success"])

    def test_search_existing_question_(self):
        res = self.client().post("/questions", json={"search": "getdata"})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))

    def test_search_non_existing_question(self):
        res = self.client().post("/questions", json={"search": "notvalidsearch"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))

    def test_get_questions_by_category_id(self):
        res = self.client().get("/categories/5/questions")  # science category
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(data["questions"])
    
    def test_get_questions_by_category_invalid_id(self):
        res = self.client().get("/categories/55/questions")
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 422)
        self.assertFalse(data["success"])
        self.assertEqual(data["message"], "unprocessable")
        
    def test_play_new_quiz(self):
        res = self.client().post('/quizzes',
        json={'previous_questions': [], 'quiz_category': {'type': 'Geography', 'id': "3"}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        # self.assertEqual(data['question'], json=quiz)

    def test_play_new_quiz_failed(self):
        res = self.client().post('/quizzes')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 400)
        self.assertEqual(data['message'], 'Bad request')



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()