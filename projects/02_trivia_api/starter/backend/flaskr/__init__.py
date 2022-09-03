from ast import Return
from operator import and_
import os
from re import search
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

def randomQuestion(prev_lst,all_lst):
    if len(all_lst) != 0:
      rand = random.choice(all_lst)
      if rand in prev_lst and rand in all_lst:
          all_lst.remove(rand)
          randomQuestion(prev_lst,all_lst)
      else:
          return rand
    return 0

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app)

  # CORS Headers
  @app.after_request
  def after_request(response):
      response.headers.add(
          "Access-Control-Allow-Origin", "*"
      )
      return response

  @app.route("/categories")
  def retrieve_categories():
      selection = Category.query.order_by(Category.id).all()
      categories = {}
      for category in selection:
        categories[category.id] = category.type

      if len(categories) == 0:
          abort(404)

      return jsonify(
          {
              "success": True,
              "categories": categories,
              "total_categories": len(Category.query.all()),
          }
      )

  @app.route("/questions")
  def retrieve_questions():
      selection = Question.query.order_by(Question.id).all()
      questions = paginate(request,selection)
      selection = Category.query.order_by(Category.id).all()
      categories = {}
      for category in selection:
        categories[category.id] = category.type

      if len(questions) == 0:
          abort(404)

      return jsonify(
          {
              "questions": questions,
              "totalQuestions": len(Question.query.all()),
              "categories":categories,
              "currentCategory": None  #Mayi clarity on this
          }
      )


  @app.route("/questions/<int:question_id>", methods=["DELETE"])
  def delete_question(question_id):
      try:
          question = Question.query.filter(Question.id == question_id).one_or_none()

          if question is None:
              abort(404)

          question.delete()

          return jsonify({"success": True})

      except:
          abort(422)

  @app.route("/questions", methods=["POST"])
  def create_question():
      body = request.get_json()

      question = body.get("question", None)
      answer = body.get("answer", None)
      difficulty = body.get("difficulty", 1)
      category = body.get("category", None)
      search_term = body.get("searchTerm", None)

      try:
          if search_term:
              selection = Question.query.filter(
                  Question.question.ilike("%{}%".format(search_term))
                )

              questions = paginate(request,selection)
              if len(questions) == 0:
                  abort(404)

              return jsonify(
                  {
                      "questions": questions,
                      "totalQuestions": len(questions),
                      "currentCategory": None  #Mayi fix this
                  }
              )
          else:
            question = Question(question=question, answer=answer, category=category, difficulty=difficulty)
            question.insert()

            return jsonify({"success": True})

      except:
          abort(422)

  @app.route("/categories/<int:category_id>/questions")
  def retrieve_categoryquestions(category_id):
      selection = Question.query.filter(Question.category == category_id).all()
      questions = paginate(request,selection)
      category = Category.query.filter(Category.id == category_id).one_or_none()
      
      if category is not None:
        currentCategory = category.type

      if len(questions) == 0:
          abort(404)

      return jsonify(
          {
              "questions": questions,
              "totalQuestions": len(Question.query.filter(Question.category == category_id).all()),
              "currentCategory": currentCategory  
          }
      )

  @app.route("/quizzes", methods=["POST"])
  def retrieve_quiz_questions():
      body = request.get_json()

      previous_questions = body.get("previous_questions", None)
      quiz_category = body.get("quiz_category", None)
      all_questions = []

      try:
          if quiz_category['type'] == 'click':
            selection = Question.query.all()
          else:
            selection = Question.query.filter(Question.category == quiz_category['id']).all()

          for question in selection:
            all_questions.append(question.id)

          question_id = randomQuestion(previous_questions,all_questions)
          question = Question.query.filter(Question.id == question_id).one_or_none()

          if question is None:
              ret = {}
          else:
              ret = jsonify(
              {
                  "question": question.format()
              }
          )

          return ret

      except:
          abort(422)

  @app.errorhandler(404)
  def not_found(error):
      return (
          jsonify({"success": False, "error": 404, "message": "Resource Not Found"}),
          404,
      )

  @app.errorhandler(422)
  def unprocessable(error):
      return (
          jsonify({"success": False, "error": 422, "message": "Unprocessable"}),
          422,
      )

  @app.errorhandler(400)
  def bad_request(error):
      return jsonify({"success": False, "error": 400, "message": "Bad Request"}), 400
  
  return app

    