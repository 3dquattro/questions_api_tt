import datetime
import json
from unittest.mock import patch, Mock
import pytest
from app.app import Questions
from app.app import app as app


# Mock результата выполнения запроса через urllib
class MockResponseResult:
    def __init__(self, result):
        self.result = result
        self.count = 0

    def read(self):
        result_to_return = bytes(
            str(json.dumps(self.result[self.count])).encode("utf-8")
        )
        self.count = self.count + 1 if self.count + 1 < len(self.result) else self.count
        return result_to_return


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# Тест с заведомо неверным запросом
def test_wrong_input(client):
    payload = {"question_num": "ЫЫ"}
    response = client.post("/test_method/", json=payload)
    assert response.status_code == 400


# Тест с корректным ответом и пустой базой
def test_correct_input(client):
    mocked_response = [
        [
            {
                "question": "Sample question",
                "answer": "Sample answer",
                "created_at": "2023-05-25T00:00:00.000Z",
            }
        ]
    ]
    mocked_result = MockResponseResult(mocked_response)
    get_lq_mock_response = {}
    # Сам запрос, попросим записать один вопрос
    payload = {"question_num": 1}
    session = Mock()
    session.add.side_effect = None
    session.commit.side_effect = None
    with (
        patch("urllib.request.urlopen", return_value=mocked_result),
        patch("app.app.get_last_question", return_value=get_lq_mock_response),
        patch("app.app.db.session", session),
        patch("app.app.check_for_unique", return_value=True),
    ):
        response = client.post("/test_method/", json=payload)

    # Проверим код ответа
    assert response.status_code == 200
    assert session.add.call_count == 1
    # И результат должен быть пустой
    assert response.json == {}


# Тест с наличием дублей в базе
def test_retry_query(client):
    payload = {"question_num": 1}
    # Сымитируем сессию базы данных
    session = Mock()
    session.add.side_effect = None
    session.commit.side_effect = None

    mock_question_in_db = Questions(
        id=1,
        text="What is unittest?",
        answer="Unittest is unittest. You just should do it. This is The Way.",
        date=datetime.datetime.now(),
    ).serialize()

    mocked_result = [
        [
            {
                "question": "What is unittest?",
                "answer": "Unittest is unittest. You just should do it. This is The Way.",
                "created_at": "2023-05-25T00:00:00.000Z",
            }
        ]
    ]
    mocked_result = MockResponseResult(mocked_result)
    urllib = Mock()
    urllib.urlopen.return_value = mocked_result
    with (
        # Красивый возврат, для 200 кода
        patch("app.app.get_last_question", return_value=mock_question_in_db),
        # Дальше предположим, что первый вопрос совпал, следовательно, приложение должно его перезапросить
        # ...а дальше делаем вид, что вопрос не нашелся
        patch("app.app.check_for_unique", side_effect=[False, True]),
        patch("app.app.db.session", session),
        patch("urllib.request", urllib),
    ):
        response = client.post("/test_method/", json=payload)
        # Запросить вовне скрипт должен дважды
        assert urllib.urlopen.call_count == 2
        # А вот записать единожды
        assert session.add.call_count == 1
        assert response.status_code == 200
        assert response.get_json()["text"] == mock_question_in_db["text"]
    pass
