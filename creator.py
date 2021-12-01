from apiclient import discovery
from httplib2 import Http
from oauth2client import client
from oauth2client import file
from oauth2client import tools
from uni_data import *

questions_subject = [
    {"required": True,
     "rowQuestion": {
         "title": "Дисципліна вписується у структуру Освітньої програми"
     }
     },
    {
        "required": True,
        "rowQuestion": {
            "title": "Дає можливість набути практичних навичок та вмінь"
        }
    },
    {
        "required": True,
        "rowQuestion": {
            "title": "Потрібна для майбітньої професійної діяльності"
        }
    },
    {
        "required": True,
        "rowQuestion": {
            "title": "Розширює світогляд"
        }
    },
    {
        "required": True,
        "rowQuestion": {
            "title": "Дає наві знання"
        }
    },
    {
        "required": True,
        "rowQuestion": {
            "title": "Насичена сучасними та актуальними науковим/науково-практичним матеріалом"
        }
    },
    {
        "required": True,
        "rowQuestion": {
            "title": "Добре забезпечена навчально-науковою літературою та методичними матеріалами"
        }
    },
    {
        "required": True,
        "rowQuestion": {
            "title": "Добре забезпечена необхідними методичними ресурсами/посібниками для організації самостійної роботи здобувачів освіти"
        }
    },
    {
        "required": True,
        "rowQuestion": {
            "title": "Має прийнятний рівень складності"
        }
    },
    {
        "required": True,
        "rowQuestion": {
            "title": "Лекції тісно пов'язані з іншими формами занять (семінарськими, практичними, лабораторними, тощо)"
        }
    },
    {
        "required": True,
        "rowQuestion": {
            "title": "Кількість годин аудиторних навчальних занять і самостійної рообти збалансована"
        }
    }
]

questions_teachers = [
    {
        "required": True,
        "rowQuestion": {
            "title": "Вміє зацікавити студентів своєю дисципліною"
        }
    },
    {
        "required": True,
        "rowQuestion": {
            "title": "Стимулює активність, творчість та самостійну роботу студентів"
        }
    },
    {
        "required": True,
        "rowQuestion": {
            "title": "Вільно володіє матеріалом з дисципліни"
        }
    },
    {
        "required": True,
        "rowQuestion": {
            "title": "Проводить заняття професійною, виразною та чіткою мовою"
        }
    },
    {
        "required": True,
        "rowQuestion": {
            "title": "Вміє доступно викласти матеріал дисципліни"
        }
    },
    {
        "required": True,
        "rowQuestion": {
            "title": "Висуває чіткі та несуперечливі вимоги до студентів"
        }
    },
    {
        "required": True,
        "rowQuestion": {
            "title": "Об'єктивно оцінює рівень знань студентів"
        }
    },
    {
        "required": True,
        "rowQuestion": {
            "title": "Поважає студентів, є тактовним"
        }
    },
    {
        "required": True,
        "rowQuestion": {
            "title": "Зацікавлений в успіхах студента"
        }
    },
    {
        "required": True,
        "rowQuestion": {
            "title": "Вміє урізноманітнити зміст лекцій фактами, прикладами, порівняннями, що активізують його сприйняття"
        }
    }
]

options_teachers = [
    {
        "value": "Не можу оцінити"
    },
    {
        "value": "Зовсім не погоджуюсь"
    },
    {
        "value": "Переважно не погоджуюсь"
    },
    {
        "value": "Частково погоджуюсь, частково не погоджуюсь"
    },
    {
        "value": "Переважно погоджуюсь"
    },
    {
        "value": "Повністю погоджуюсь"
    }
]

options_subject = [
    {
        "value": "Не можу оцінити"
    },
    {
        "value": "Зовсім не погоджуюсь"
    },
    {
        "value": "Переважно не погоджуюсь"
    },
    {
        "value": "Частково погоджуюсь, частково не погоджуюсь"
    },
    {
        "value": "Переважно погоджуюсь"
    },
    {
        "value": "Повністю погоджуюсь"
    }
]

class AutomatedFormCreator:
    def __init__(self):
        self.KEY = "ENTER YOUR API KEY HERE"
        self.SCOPES = "https://www.googleapis.com/auth/drive"
        self.DISCOVERY_DOC = f"https://forms.googleapis.com/$discovery/rest?version=v1beta&key={self.KEY}&labels=FORMS_BETA_TESTERS"
        self.store = file.Storage('credentials.json')
        self.creds = None
        if not self.creds or self.creds.invalid:
            flow = client.flow_from_clientsecrets('client_secrets.json', self.SCOPES)
            self.creds = tools.run_flow(flow, self.store)
        self.form_service = discovery.build('forms', 'v1beta', http=self.creds.authorize(
            Http()), discoveryServiceUrl=self.DISCOVERY_DOC, static_discovery=False)

    def create_forms_for_groups(self, uni_data: UniversityData):
        form_ids = []
        form_ids_to_group_name = dict()
        for group in uni_data.groups:
            form = self.create_form(group)
            res = self.update_form_title_for_group(form, group)
            res = self.add_items_for_group(form, group)
            form_ids.append(form["formId"])
            form_ids_to_group_name[form["formId"]] = group.name
        return form_ids, form_ids_to_group_name

    def update_form_title_for_group(self, form, group):
        title_description = f"Освітньо-професійна програма {group.specialty_name} рівня вищої освіти {group.degree}, {group.course} рік навчання"
        document_title = f"{group.specialty_name} {group.degree}_{group.course}"
        update = {
            "requests": [{
                "updateFormInfo": {
                    "info": {
                        "description": title_description,
                        "documentTitle": document_title
                    },
                    "updateMask": "description"
                }
            }]
        }
        return self.form_service.forms().batchUpdate(formId=form["formId"], body=update).execute()

    def add_items_for_group(self, form, group):
        update = {
            "requests": [{
                "createItem": {
                    "item": {
                        "title": "Шановні студенти ! Факультет комп'ютерних наук та кібернетики проводить щосеместрове опитування здобувачів вищої освіти з метою оцінки якості викладання в аспекті збереження кращих традицій навчання та використання передового міжнародного досвіду стосовно якості надання освітніх послуг. Ваші відповіді допоможуть оцінити якість викладання певної навчальної дисципліни. Опитування є цілком анонімним і його результат будуть використані виключно вузагальненому вигляді. Ваша об'єктивна думка дуже важлива для нас! ",
                        "description": "",
                        "textItem": {},
                    },
                    "location": {
                        "index": 0
                    }
                }
            }
            ]
        }
        index = 1
        for subject in group.subjects:
            lector = '\n'.join(subject.lecturers)
            lab_prof = '\n'.join(subject.lab_professors)
            update["requests"].append({
                "createItem": {
                    "item": {
                        "title": f"Навчальна дисципліна {subject.name}",
                        "description": f"Лектор: {lector}\nЛабораторні заняття: {lab_prof}",
                        "pageBreakItem": {}
                    },
                    "location": {
                        "index": index
                    }
                }
            })
            index += 1
            if len(subject.lecturers) > 0:
                if len(subject.lecturers) > 1:
                    update["requests"].append(
                        self.create_teacher_choice(lecturer=True, teachers=subject.lecturers, index=index))
                    index += 1
                update["requests"].append(self.create_teacher_questions(lectures=True, index=index))
                index += 1
            if len(subject.lab_professors) > 0:
                if len(subject.lab_professors) > 1:
                    update["requests"].append(
                        self.create_teacher_choice(lecturer=False, teachers=subject.lab_professors, index=index))
                    index += 1
                update["requests"].append(self.create_teacher_questions(lectures=False, index=index))
                index += 1
            update["requests"].append(self.create_subject_question(subject.name, index=index))
            index += 1

        return self.form_service.forms().batchUpdate(formId=form["formId"], body=update).execute()

    def create_subject_question(self, subject_name, index):
        return {
            "createItem": {
                "item": {
                    "title": f"Наступні твердження стосуються навчальної дисципліни \"{subject_name}\"",
                    "questionGroupItem": {
                        "questions": questions_subject,
                        "grid": {
                            "columns": {
                                "type": "RADIO",
                                "options": options_subject
                            }
                        }
                    },
                },
                "location": {
                    "index": index
                }
            }
        }

    def create_teacher_choice(self, lecturer: bool, teachers, index):
        if lecturer:
            title = "Оберіть викладача, який проводив лекційні заняття"
        else:
            title = "Оберіть викладача, який проводив лабораторні заняття"
        options = []
        for teacher in teachers:
            options.append({
                "value": teacher
            })
        if len(options) == 0:
            assert False
        assert len(options) > 0
        return {
            "createItem": {
                "item": {
                    "title": title,
                    "questionItem": {
                        "question": {
                            "required": True,
                            "choiceQuestion": {
                                "type": "RADIO",
                                "options": options
                            }
                        }
                    }
                },
                "location": {
                    "index": index
                },
            }
        }

    def create_teacher_questions(self, lectures: bool, index):
        if lectures:
            text = "читає лекції"
        else:
            text = "проводить лабораторні заняття"
        return {
            "createItem": {
                "item": {
                    "title": f"Позначте, будь ласка, якою мірою Ви погоджуетесь із наведеними нижче твердженнями стосовно викладача, який {text}:",
                    "questionGroupItem": {
                        "questions": questions_teachers,
                        "grid": {
                            "columns": {
                                "type": "RADIO",
                                "options": options_teachers,
                            }
                        }
                    }
                },
                "location": {
                    "index": index
                }
            }
        }

    def create_form(self, group):
        title = f"Анонімне опитування студентів {group.course} року навчання ОПП \"{group.specialty_name}\" щодо якості викладання за навчальними дисциплінами"
        form = {
            "info": {
                "title": title,
            },
        }
        # Prints the details of the sample form
        result = self.form_service.forms().create(body=form).execute()
        return result

    def get_form_json(self, form_id):
        return self.form_service.forms().get(formId=form_id).execute()

    def retrieve_form_responses(self, form_id):
        return self.form_service.forms().responses().list(formId=form_id).execute()