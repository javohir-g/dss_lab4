# Lab 4A. Task 6 - Duplicates after the nightly import
# Student: Javohir Gayratov
#
# 6.1 Question: Explain the first bug: what do == and hash() compare when a class defines
#     neither of them?
#     Answer: Then they come from object and compare identity: a == b is the same as a is b,
#     and hash() is made from id(). Two Student objects from the same CSV row are two
#     different objects, so the set keeps both.
#
# 6.2 Question: Explain the second bug: what does Python do with __hash__ when a class defines
#     only __eq__?
#     Answer: Python sets __hash__ = None, because the old hash (from id) would not agree with
#     the new ==. The objects become unhashable and set.add() raises
#     TypeError: unhashable type: 'Student'.
#
# 6.3 Question: Decide what makes two Student objects "the same student". A student moved from
#     SE-31 to SE-32 and the CSV now has the new group: is it the same student? Implement
#     __eq__ and __hash__ that agree with your decision.
#     Answer: Same student = same student_id. The registrar gives it once and it never changes.
#     A student who moved to SE-32 is the same person, so name and group are not part of it.
#     __eq__ and __hash__ both use only student_id, and student_id is read-only, so the hash
#     of a student can not change while it is in a set.
#
# 6.4 Question: A teammate makes the hash depend on group. Write four lines that put a student
#     into a set, change s.group to 'SE-32', and show that s in seen is now False.
#     Answer: When the group changes, the hash changes too and the set looks in the wrong place:
#         s = TeammateStudent("U2310045", "Ali Valiyev", "SE-31")
#         seen = {s}
#         s.group = "SE-32"
#         print(s in seen)    # False
#
# 6.5 Question: Why is a plain @dataclass(frozen=True) not the right fix here? Think about
#     which fields it compares and about the group change.
#     Answer: It compares and hashes all fields (id, name, group). After a group change the new
#     CSV row is not equal to the old one, so we get a duplicate again. Also frozen does not
#     let us change the group of an existing student.
#
# 6.6 Question: Add __repr__ so that the log shows
#     Student(student_id='U2310045', group='SE-31').
#     Answer: Done, __repr__ shows only student_id and group.


class Student:
    def __init__(self, student_id, full_name, group):
        self._student_id = student_id
        self.full_name = full_name
        self.group = group

    @property
    def student_id(self):
        return self._student_id

    def __eq__(self, other):
        if not isinstance(other, Student):
            return NotImplemented
        return self.student_id == other.student_id

    def __hash__(self):
        return hash(self.student_id)

    def __repr__(self):
        return f"Student(student_id={self.student_id!r}, group={self.group!r})"


def import_students(rows):
    seen = set()
    for row in rows:
        seen.add(Student(*row))
    return seen


# teammate's version from 6.4 (hash depends on group)
class TeammateStudent:

    def __init__(self, student_id, full_name, group):
        self.student_id, self.full_name, self.group = student_id, full_name, group

    def __eq__(self, other):
        return isinstance(other, TeammateStudent) and \
            (self.student_id, self.group) == (other.student_id, other.group)

    def __hash__(self):
        return hash((self.student_id, self.group))


ROWS = [("U2310045", "Ali Valiyev", "SE-31"),
        ("U2310045", "Ali Valiyev", "SE-31")]


def test_bug_1_identity_compare():
    class OldStudent:
        def __init__(self, student_id, full_name, group):
            self.student_id, self.full_name, self.group = student_id, full_name, group

    a, b = OldStudent(*ROWS[0]), OldStudent(*ROWS[1])
    assert a != b and len({a, b}) == 2


def test_bug_2_eq_without_hash():
    class QuickFixStudent:
        def __init__(self, student_id):
            self.student_id = student_id

        def __eq__(self, other):
            return self.student_id == other.student_id

    assert QuickFixStudent.__hash__ is None
    try:
        {QuickFixStudent("U2310045")}
    except TypeError as error:
        assert "unhashable type" in str(error)
    else:
        raise AssertionError("expected TypeError")


def test_loop_prints_one():
    assert len(import_students(ROWS)) == 1


def test_found_after_group_change():
    seen = import_students(ROWS)
    s = next(iter(seen))
    s.group = "SE-32"
    assert s in seen
    assert Student("U2310045", "Ali Valiyev", "SE-32") in seen


def test_equal_objects_have_equal_hashes():
    a = Student("U2310045", "Ali Valiyev", "SE-31")
    b = Student("U2310045", "Ali Valiyev (fixed name)", "SE-32")
    c = Student("U2310046", "Ali Valiyev", "SE-31")
    assert a == b and hash(a) == hash(b)
    assert a != c
    assert a != "U2310045"


def test_hash_on_group_loses_the_student():
    s = TeammateStudent("U2310045", "Ali Valiyev", "SE-31")
    seen = {s}
    s.group = "SE-32"
    assert (s in seen) is False


def test_repr_for_the_log():
    s = Student("U2310045", "Ali Valiyev", "SE-31")
    assert repr(s) == "Student(student_id='U2310045', group='SE-31')"


if __name__ == "__main__":
    print(len(import_students(ROWS)))
