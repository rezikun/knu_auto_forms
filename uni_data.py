
import requests
from functools import reduce


class Caller:
    def __init__(self):
        self.base_url = "https://api.mytimetable.live/rest"

    def merge_two_dicts(self, x, y):
        z = x.copy()  # start with keys and values of x
        z.update(y)  # modifies z with keys and values of y
        return z

    def call_timetable_api(self, suffix):
        return requests.get(self.base_url + suffix).json()

    def call_api(self, suffix):
        initial_response = requests.get(self.base_url + suffix)
        responses = [initial_response.json()["results"]]
        if "next" in initial_response.json():
            while initial_response.json()["next"] is not None:
                initial_response = requests.get(initial_response.json()["next"])
                responses.append(initial_response.json()["results"])
            return reduce(lambda json1, json2: json1 + json2, responses, [])
        else:
            return initial_response.json()["results"]


class Subject:
    def __init__(self, name):
        self.name = name
        self.lecturers = set()
        self.lab_professors = set()

    def add_lecturer(self, lecturer):
        self.lecturers.add(lecturer)

    def add_lab_professor(self, lab_professor):
        self.lab_professors.add(lab_professor)


class Group:
    def __init__(self, group_id, group_name, course, degree, specialty_name):
        lecture_type_id = 0
        self.caller = Caller()
        self.id = group_id
        self.name = group_name
        self.degree = degree
        self.course = course
        self.specialty_name = specialty_name
        self.timetable = self.caller.call_timetable_api(f"/timetable/?group={self.id}")
        self.subjects = dict()
        for lesson in self.timetable["lessons"]:
            subject_name = lesson["name_full"]
            if subject_name not in self.subjects:
                self.subjects[subject_name] = Subject(subject_name)
            if lesson["format"] == lecture_type_id:
                for teacher in lesson["teachers"]:
                    self.subjects[subject_name].add_lecturer(teacher["full_name"])
            if lesson["format"] != lecture_type_id:
                for teacher in lesson["teachers"]:
                    self.subjects[subject_name].add_lab_professor(teacher["full_name"])
        self.subjects = list(self.subjects.values())


class UniversityData:
    def __init__(self, faculty_id=1):
        degree = {
            0: "Бакалавр",
            1: "Магістр",
            2: "Спеціаліст",
            3: "Інше"
        }
        self.caller = Caller()
        # CSC id is 1
        self.faculty_id = faculty_id
        self.group_data = self.caller.call_api(f"/groups/?faculty={self.faculty_id}")
        self.courses = self.caller.call_api("/courses")
        self.specialties = self.caller.call_api("/specialties")
        self.groups = [Group(group["id"],
                             group["name"],
                             group["course_name"],
                             degree[self.find_by_id(self.courses, group["course"])["degree"]],
                             self.find_by_id(self.specialties,
                                             self.find_by_id(self.courses, group["course"])["specialty"])["name"])
                       for group in self.group_data]
        print("Success")

    def find_by_id(self, results, id_lookup):
        for result in results:
            if result["id"] == id_lookup:
                return result
        assert False
