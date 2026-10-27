# Lab 4A. Task 9 - Splitting the god class
# Student: Javohir Gayratov
#
# 9.1 Question: For each method, write which attributes it uses. Group the methods that use the
#     same data.
#     Answer:
#     - add_student: students
#     - record_score: students (is the id known?), scores, submitted_at
#     - late_penalty: scores, submitted_at, deadlines
#     - final_grade: scores, weights, and late_penalty (so also submitted_at and deadlines)
#     - letter: only the number from final_grade
#     - export_csv: students, final_grade and letter of every student
#     - email_results: students, final_grade and letter, smtp_host
#     Groups: scores + submitted_at + deadlines go together (one submission and how late it
#     is); weights + final_grade + letter are the grading scheme; students is the list of
#     students; export_csv and email_results only read the results, smtp_host is only for
#     e-mail.
#
# 9.2 Question: Propose new classes and write a CRC card for each one. Hint: in the lecture,
#     Loan is an event with data that owns the fine rule. What is the event with data in a
#     gradebook?
#     Answer: The event with data is the Submission: a student hands in an assessment at some
#     moment and gets a score, like a Loan in the library. CRC cards
#     (class | responsibilities | collaborators):
#     - Assessment | knows its name, weight and deadline | -
#     - Submission | knows student, assessment, score and submitted_at; calculates the late
#       penalty; gives the score after the penalty | Assessment
#     - GradingScheme | knows the assessments and the letter limits; calculates the final grade
#       from the submissions of a student; turns a grade into a letter | Assessment, Submission
#     - Gradebook | keeps the students; records submissions (one per student and assessment);
#       gives the submissions of one student | Student, Submission
#     - Student | knows student_id and name | -
#     - GradeCsvExporter | writes id, name, final grade and letter to a CSV file |
#       Gradebook, GradingScheme
#     - ResultsMailer | builds the result e-mail for every student; sends it through an SMTP
#       client given from outside | Gradebook, GradingScheme, SmtpClient
#     Now three developers can work in parallel: grade rules (Assessment, Submission,
#     GradingScheme), storage (Gradebook, Student) and output (GradeCsvExporter, ResultsMailer).
#
# 9.3 Question: Which class calculates the late penalty? Which class calculates the final
#     grade? Which classes are only used and not stored (dependencies)?
#     Answer: Submission calculates the late penalty: it has the score and submitted_at, and
#     its Assessment has the deadline. GradingScheme calculates the final grade, because it has
#     the weights. Only used, not stored: GradingScheme gets the Submission objects only as a
#     parameter of final_grade(); GradeCsvExporter uses the file and csv.writer only inside
#     export(); ResultsMailer uses the e-mail message objects only inside one method.
#
# 9.4 Question: Implement the class that owns the late-penalty rule and test it for four
#     submissions: on time, 1 minute late, 1 day and 1 minute late, and 6 days late.
#     Answer: Assessment and Submission are below (with GradingScheme and Gradebook). Results
#     for a score of 80: on time 0 %, 1 minute late 10 % (8 points), 1 day and 1 minute late
#     20 % (16 points), 6 days late 50 % (40 points, because 60 % is more than the 50 % limit).
import math
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import ClassVar

import pytest

ONE_DAY = timedelta(days=1)


@dataclass(frozen=True)
class Student:
    student_id: str
    name: str


@dataclass(frozen=True)
class Assessment:
    name: str
    weight: float          # part of the final grade, e.g. 0.3
    deadline: datetime


@dataclass(frozen=True)
class Submission:
    PENALTY_PER_DAY: ClassVar[int] = 10   # percent of the score
    MAX_PENALTY: ClassVar[int] = 50

    student_id: str
    assessment: Assessment
    score: int             # 0..100, before the penalty
    submitted_at: datetime

    def __post_init__(self):
        if not 0 <= self.score <= 100:
            raise ValueError(f"score must be 0..100, got {self.score}")

    def days_late(self) -> int:
        late = self.submitted_at - self.assessment.deadline
        if late <= timedelta(0):
            return 0
        return -(-late // ONE_DAY)        # every started day counts

    def penalty_percent(self) -> int:
        return min(self.days_late() * self.PENALTY_PER_DAY, self.MAX_PENALTY)

    def late_penalty(self) -> float:
        return self.score * self.penalty_percent() / 100

    def final_score(self) -> float:
        return self.score - self.late_penalty()


class GradingScheme:
    LETTERS = ((90, "A"), (80, "B"), (70, "C"), (60, "D"))

    def __init__(self, assessments):
        self._assessments = {a.name: a for a in assessments}
        if not math.isclose(sum(a.weight for a in assessments), 1.0):
            raise ValueError("the weights must add up to 1")

    def final_grade(self, submissions) -> float:
        best = {s.assessment.name: s.final_score() for s in submissions}
        grade = sum(a.weight * best.get(name, 0) for name, a in self._assessments.items())
        return round(grade, 2)

    def letter(self, grade) -> str:
        for limit, letter in self.LETTERS:
            if grade >= limit:
                return letter
        return "F"


class Gradebook:
    def __init__(self):
        self._students = {}
        self._submissions = {}   # (student_id, assessment name) -> Submission

    def add_student(self, student):
        self._students[student.student_id] = student

    def record(self, submission):
        if submission.student_id not in self._students:
            raise KeyError(f"unknown student {submission.student_id}")
        self._submissions[(submission.student_id, submission.assessment.name)] = submission

    def submissions_of(self, student_id):
        return tuple(s for (sid, _), s in self._submissions.items() if sid == student_id)

    @property
    def students(self):
        return tuple(self._students.values())


# tests
DEADLINE = datetime(2026, 11, 10, 23, 59)
MIDTERM = Assessment("midterm", 0.3, DEADLINE)
FINAL = Assessment("final", 0.5, DEADLINE + timedelta(days=30))
LABS = Assessment("labs", 0.2, DEADLINE + timedelta(days=20))


@pytest.mark.parametrize("submitted_at, percent, points", [
    (DEADLINE - timedelta(hours=2), 0, 0),                      # on time
    (DEADLINE, 0, 0),                                           # exactly at the deadline
    (DEADLINE + timedelta(minutes=1), 10, 8),                   # 1 minute late
    (DEADLINE + timedelta(days=1, minutes=1), 20, 16),          # 1 day and 1 minute late
    (DEADLINE + timedelta(days=6), 50, 40),                     # 6 days late, 60 % capped
])
def test_late_penalty(submitted_at, percent, points):
    submission = Submission("U1", MIDTERM, 80, submitted_at)
    assert submission.penalty_percent() == percent
    assert submission.late_penalty() == points
    assert submission.final_score() == 80 - points


def test_score_must_be_0_to_100():
    with pytest.raises(ValueError):
        Submission("U1", MIDTERM, 101, DEADLINE)


def test_final_grade_and_letter_use_penalties():
    book = Gradebook()
    book.add_student(Student("U1", "Ali Valiyev"))
    book.record(Submission("U1", MIDTERM, 80, DEADLINE + timedelta(minutes=1)))   # 72
    book.record(Submission("U1", FINAL, 90, FINAL.deadline))                      # 90
    book.record(Submission("U1", LABS, 100, LABS.deadline))                       # 100
    scheme = GradingScheme([MIDTERM, FINAL, LABS])
    grade = scheme.final_grade(book.submissions_of("U1"))
    assert grade == 86.6                   # 0.3*72 + 0.5*90 + 0.2*100
    assert scheme.letter(grade) == "B"


def test_missing_submission_counts_as_zero():
    scheme = GradingScheme([MIDTERM, FINAL, LABS])
    only_final = [Submission("U1", FINAL, 100, FINAL.deadline)]
    assert scheme.final_grade(only_final) == 50
    assert scheme.letter(50) == "F"


def test_unknown_student_is_rejected():
    with pytest.raises(KeyError):
        Gradebook().record(Submission("U9", MIDTERM, 50, DEADLINE))
