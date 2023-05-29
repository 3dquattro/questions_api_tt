import urllib.request
import json
from datetime import datetime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields, ValidationError, EXCLUDE
from sqlalchemy.exc import IntegrityError, PendingRollbackError


# region Инициализация приложения
# Инициализация приложения и соединения с БД

db = SQLAlchemy()


def create_app(test_config=None):
    result_app = Flask(__name__)
    if test_config:
        result_app.config.update(test_config)
    else:
        result_app.config[
            "SQLALCHEMY_DATABASE_URI"
        ] = "postgresql://postgres:1@localhost:5432/tt1"
    result_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(result_app)
    if test_config:
        with result_app.app_context():
            db.create_all()
    return result_app, db


app, db = create_app()


def site_map():
    return list(app.url_map.iter_rules())


# endregion

# region Схемы Marshmallow


# Схема Marshmallow для проверки корректности запроса к API
class RequestSchema(Schema):
    question_num = fields.Integer(required=True)


# Схема Marshmallow для ответа с API jservice.io
class QuestionSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    question = fields.String(required=True)
    answer = fields.String(required=True)
    created_at = fields.DateTime(required=True)


# endregion

# region Модели SQLAlchemy


# Модель вопроса
class Questions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(300), unique=True)
    answer = db.Column(db.String(300))
    date = db.Column(db.DateTime)

    def serialize(self):
        return {
            "id": self.id,
            "text": self.text,
            "date": self.date,
            "answer": self.answer,
        }


# endregion

# region Логика приложения


def get_last_question() -> dict:
    last_added_question: Questions = Questions.query.order_by(
        Questions.date.desc()
    ).first()
    result = last_added_question.serialize() if last_added_question is not None else {}
    return result


def check_for_unique(text: str, answer: str) -> bool:
    question = Questions.query.filter_by(text=text, answer=answer).first()
    return False if question is not None else True


# Эндпоинт API
@app.route("/test_method/", methods=["POST"])
def post_data():
    # Валидация запроса
    schema = RequestSchema()
    try:
        validated_input = schema.load(request.get_json())
    except ValidationError as err:
        # Если некорректный запрос, отдаём 400 ошибку
        return jsonify(err.messages), 400
    count: int = int(validated_input["question_num"])
    question_schema: QuestionSchema = QuestionSchema(
        many=True
    )  # Ожидаем массив объектов
    result = get_last_question()
    # Исключение для не положительных чисел
    if count < 1:
        return jsonify("Число запрошенных вопросов <= 0"), 400
    # Запрос к jservice.io
    while count > 0:
        request_count = 100 if count > 100 else count
        url: str = "https://jservice.io/api/random?count={}".format(request_count)
        response = urllib.request.urlopen(url)
        # json.loads потому что тип response.read - bytes
        raw_data: list = json.loads(response.read())
        # Валидация результатов запроса
        try:
            validated_data = question_schema.load(raw_data, many=True)
        except ValidationError:
            # Если что-то пошло не так - сервис вернул не то в ответ на запрос,
            # сделаем вид что всё нормально,
            # но ничего не запишем
            return jsonify(result), 200

        count -= request_count
        # Проверка на дубликат
        for element in validated_data:
            if not check_for_unique(text=element["question"], answer=element["answer"]):
                count += 1
                continue
            question = Questions(
                text=element["question"], answer=element["answer"], date=datetime.now()
            )
            try:
                db.session.add(question)
                db.session.commit()
            except IntegrityError or PendingRollbackError:
                count += 1  # В случае если не получилось записать
                # (по причине неуникальности, если другая сессия записала),
                # пропускаем и прибавляем к счетчику count
                continue
        print("ok")
    # Цикл закончился, в случае успешного успеха запросим последний вопрос
    return jsonify(result), 200


if __name__ == "__main__":
    app.run()
# endregion
