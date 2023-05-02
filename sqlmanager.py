import sqlite3
from hhparser import Vacancy, Company

def __connect() -> sqlite3:
    """Connects to a database"""
    try:
        db = sqlite3.connect('./db.sql')
    except Exception as e:
        print("Error while connecting to a database: " + str(e))
        exit(-1)

    return db


def get_company_data(company_name):
    db = __connect()
    try:
        data = db.execute(f"SELECT rating FROM COMPANY WHERE name = '{company_name}'").fetchall()
    except:
        exit(-1)
    db.close()
    return data


def manage_data(parsed_vacancy_data: Vacancy, parsed_company_data: Company):
    db = __connect()
    added_vacancies = []
    added_companies = []
    deleted_vacancies = []
    deleted_companies = []

    try:
        db.execute('SELECT * FROM COMPANY').fetchall()
    except sqlite3.OperationalError as e:
        db.execute("""
            CREATE TABLE COMPANY(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                has_awards BOOLEAN DEFAULT(FALSE),
                is_verified BOOLEAN DEFAULT(FALSE),
                is_accredited BOOLEAN DEFAULT(FALSE),
                rating DECIMAL,
                review_count INTEGER
            );""")

    try:
        db.execute('SELECT * FROM VACANCY')
    except:
        db.execute("""CREATE TABLE VACANCY(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                wage INTEGER,
                company_name TEXT
            );""")

    company = 'INSERT INTO COMPANY (name, has_awards, is_verified, is_accredited, rating, review_count) VALUES '
    db_data = db.execute('SELECT * FROM COMPANY').fetchall()
    db_company_data = [Company(item[1], item[2], item[3], item[4],
                               item[5] if item[5] is not None else 'NULL',
                               item[6] if item[6] is not None else 'NULL') for item in
                               db_data]
    delete_script = 'DELETE FROM COMPANY WHERE '
    delete_flag = False

    add_flag = False
    for item in parsed_company_data:
        if item not in db_company_data:
            add_flag = True
            company += f"('{item.name}', {item.has_awards}, {item.is_verified}, {item.is_accredited}, {item.rating}, {item.review_count}), "
            added_companies.append(item)

    if add_flag:
        company = company[:-2] + ';'
        db.execute(company)

    for db_company in db_company_data:
        if db_company not in parsed_company_data:
            delete_flag = True
            delete_script += f"""(name='{db_company.name}' AND
            has_awards={db_company.has_awards} AND
            is_verified={db_company.is_verified} AND
            is_accredited={db_company.is_accredited} AND
            rating='{db_company.rating}' AND
            review_count='{db_company.review_count}') OR """
            deleted_companies.append(db_company)

    if delete_flag:
        delete_script = delete_script[:-4] + ";"
        db.execute(delete_script)

    vacancy = 'INSERT INTO VACANCY (title, wage, company_name) VALUES '
    db_vacancy_data = [Vacancy(item[1], item[2] if item[2] is not None else 'NULL', item[3]) for item in
                       db.execute('SELECT * FROM VACANCY').fetchall()]

    delete_script = 'DELETE FROM VACANCY WHERE '
    delete_flag = False
    for db_vacancy in db_vacancy_data:
        if db_vacancy not in parsed_vacancy_data:
            delete_flag = True
            delete_script += f"""(title='{db_vacancy.title}' AND
            wage={db_vacancy.wage} AND
            company_name='{db_vacancy.company_name}') OR """
            deleted_vacancies.append(db_vacancy)

    if delete_flag:
        delete_script = delete_script[:-4] + ';'
        db.execute(delete_script)

    add_flag = False
    for item in parsed_vacancy_data:
        if item not in db_vacancy_data:
            add_flag = True
            vacancy += f"('{item.title}', {item.wage}, '{item.company_name}'), "
            added_vacancies.append(item)

    if add_flag:
        vacancy = vacancy[:-2] + ';'
        db.execute(vacancy)

    db.commit()
    db.close()
    return (added_vacancies, added_companies, deleted_vacancies, deleted_companies)
