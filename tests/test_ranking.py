"""Unit tests for question ranking and deduplication."""

from stackoverflow_mcp.ranking import rank_and_dedupe_questions


def test_question_deduplication():
    questions = [
        {"question_id": 101, "title": "First Question", "score": 10},
        {"question_id": 101, "title": "Duplicate Question", "score": 10},
        {"question_id": 102, "title": "Second Question", "score": 5},
    ]

    result = rank_and_dedupe_questions(questions)
    assert len(result) == 2
    ids = [q["question_id"] for q in result]
    assert ids == [101, 102]


def test_accepted_answers_sort_first():
    questions = [
        {
            "question_id": 1,
            "title": "High score but not accepted",
            "score": 150,
            "is_answered": False,
            "accepted_answer_id": None,
        },
        {
            "question_id": 2,
            "title": "Lower score but accepted answer",
            "score": 20,
            "is_answered": True,
            "accepted_answer_id": 999,
        },
    ]

    result = rank_and_dedupe_questions(questions)
    assert result[0]["question_id"] == 2
    assert result[1]["question_id"] == 1


def test_score_sorting_at_equal_accepted_status():
    questions = [
        {"question_id": 1, "title": "Low Score", "score": 5, "is_answered": False},
        {"question_id": 2, "title": "High Score", "score": 45, "is_answered": False},
        {"question_id": 3, "title": "Medium Score", "score": 20, "is_answered": False},
    ]

    result = rank_and_dedupe_questions(questions)
    scores = [q["score"] for q in result]
    assert scores == [45, 20, 5]


def test_empty_list():
    assert rank_and_dedupe_questions([]) == []
