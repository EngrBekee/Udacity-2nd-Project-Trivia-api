import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    
    questions = [question.format() for question in selection]
    current_questions = questions[start:end]
    
    return current_questions

def pages(page, request, paginate_next_page):
    if paginate_next_page < page:
        nextpage = request.args.get('page', 1, type=int) + 1
        return str(request.url_root + 'questions?page=') + str(nextpage)
    else:
        return str(request.url_root + 'questions?page=1')
    
def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={r"*":{"origins":"*"}})
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers",
            "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods",
            "GET,PUT,PATCH,POST,DELETE,OPTIONS"
        )
        return response
    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route("/categories", methods=["GET"])
    def get_categories():
        try:
            categories = Category.query.order_by(Category.id).all()
            formatted_categories = {category.id:category.type for category in categories}
            if len(formatted_categories) == 0:
                abort(404)

            return jsonify({
                "success" : True,
                "status_code": 200,
                "categories":formatted_categories,
                "total_categories":len(Category.query.all()) 
            })
        except:
            abort(405)
    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions', methods=['GET'])
    def get_questions():
        try:
            questions = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, questions)

            categories = Category.query.order_by(Category.type).all()
            formatted_category = {category.id: category.type for category in categories}
            next_paginate = len(questions) % QUESTIONS_PER_PAGE

            if len(current_questions) == 0:
                abort(404)
            return jsonify({
                'success': True,
                'questions': current_questions,
                'categories': formatted_category,
                'next_page': pages(len(current_questions), request, next_paginate),
                'total_questions': len(questions),
                })
        except:
                abort(422)

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.filter(Question.id == question_id).one_or_none()
        if question is None:
            abort(404)
        else:
            question.delete()
            questions = question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, questions)
        try:
            return jsonify({
                'success': True,
                'deleted_question' : question.question,
                'deleted_question_id' : question.id,
                'current_questions': current_questions,
            })
        except:
            abort(422)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def add_a_question():
        body = request.get_json(Question)

        try:
            if body is not None:
                post_new_question = Question(question=body.get("question", None), 
                                         category=body.get("category", None), 
                                         difficulty=body.get("difficulty", None), 
                                         answer=body.get("answer", None))
            post_new_question.insert()

            new_que = Question.query.order_by(Question.id).all()
            all_questions = paginate_questions(request, new_que)

            return jsonify({
                "success" : True,
                "new_question" : post_new_question.question,
                "questions" : all_questions,
                "total_questions" : len(Question.query.all()),
            })
        except:
            abort(422)

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/questions/search', methods=['POST'])
    def questions_search():
      
        get_search = request.args.get("search", None)
        try:
            if get_search is not None:
                value = Question.query.order_by(Question.id).filter(
                Question.question.ilike("%{}%".format(get_search))
                )
                searched_items = [search.format() for search in value]
                return jsonify(
                    {
                        "success": True,
                        "questions": searched_items,
                        "total_searched_items" : len(searched_items),
                    }
                )
            else:
                abort(404)
        except:
            abort(422)
    
    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def search_based_on_category(category_id):
        try:
            questions = Question.query.filter_by(category=category_id).all()
            formatted_questions = [question.format() for question in questions]
            if len(formatted_questions) == 0:
                abort(404)
            return jsonify({
                'success': True,
                'questions': formatted_questions,
                'total_questions': len(formatted_questions),
                'current_category': category_id
            })
        except:
            abort(422)
 
    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def play():
        body = request.get_json()
        try:
            get_prev_que = body.get('previous_questions')

            get_quiz_category = body.get('quiz_category')['id']

            return filter_quiz(get_prev_que, get_quiz_category)

        except:
            abort(400)

    def filter_quiz(get_prev_que, get_quiz_category):
        trivia_questions = []
        if get_quiz_category == 0:
            trivia_questions = Question.query.filter(
                    Question.id.notin_(get_prev_que)).all()
        else:
            trivia_questions = get_filtered_quiz(get_prev_que, get_quiz_category)
        retrieved_question = None
        if len(trivia_questions) > 0:
            rand_quiz = random.randrange(0, len(trivia_questions))
            retrieved_question = trivia_questions[rand_quiz].format()
        return jsonify({
                'success': True,
                'question': retrieved_question,
                'total_questions': len(trivia_questions)
            })

    def get_filtered_quiz(get_prev_que, get_quiz_category):
        category = Category.query.get(get_quiz_category)
        if category is None:
            abort(404)
        trivia_questions = Question.query.filter(Question.id.notin_(
                    get_prev_que), Question.category == get_quiz_category).all()

        return trivia_questions


    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad request"
        }), 400

    @app.errorhandler(405)
    def method_not_allow(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "Method not allow"
        }), 405
    return app

