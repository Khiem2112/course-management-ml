from course_management_ml.database.execute_service import DBExecuteService as db
from course_management_ml.utils.logger import get_class_logger

logger = get_class_logger(__name__, "CoursesLogic")

class CoursesLogic:
    @staticmethod
    def get_all_courses(limit=100):
        query = "SELECT code_module, code_presentation FROM courses LIMIT %s;"
        data = db.fetch_all(query, (limit,))
        logger.info(f"Fetched {len(data)} courses.")
        return data

    @staticmethod
    def get_top_students_by_score(code_module, code_presentation, n=5):
        query = """
        SELECT sa.id_student, AVG(sa.score) AS avg_score
        FROM studentAssessment sa
            JOIN assessments a ON sa.id_assessment = a.id_assessment
        WHERE a.code_module = %s AND a.code_presentation = %s
        GROUP BY sa.id_student
        ORDER BY avg_score DESC
        LIMIT %s;
        """
        data = db.fetch_all(query, (code_module, code_presentation, n))
        logger.info(f"Fetched top {n} students for {code_module}-{code_presentation}.")
        return data

    @staticmethod
    def get_dropout_percentage(code_module, code_presentation):
        query = """
        SELECT
            COUNT(CASE WHEN date_unregistration IS NOT NULL THEN 1 END) * 100.0 / COUNT(*) AS dropout,
            COUNT(CASE WHEN date_unregistration IS NULL THEN 1 END) * 100.0 / COUNT(*) AS retention
        FROM studentRegistration
        WHERE code_module = %s AND code_presentation = %s;
        """
        data = db.fetch_one(query, (code_module, code_presentation))
        logger.info(f"Dropout percentage for {code_module}-{code_presentation}: {data}")
        return data

    @staticmethod
    def get_student_score_statistic(code_module, code_presentation):
        query = """
        WITH student_score AS (
            SELECT AVG(score) as avg_score
            FROM studentAssessment sa
            JOIN assessments a ON sa.id_assessment = a.id_assessment
            WHERE a.code_module = %s AND a.code_presentation = %s
            GROUP BY sa.id_student
        )
        SELECT 
            MIN(avg_score) as min_score,
            MAX(avg_score) as max_score,
            AVG(avg_score) as mean_score,
            (
                SELECT avg_score
                FROM student_score
                GROUP BY avg_score
                ORDER BY COUNT(*) DESC, avg_score ASC
                LIMIT 1
            ) as mode_score
        FROM student_score;
        """
        data = db.fetch_one(query, (code_module, code_presentation))
        logger.info(f"Score stats for {code_module}-{code_presentation}: {data}")
        return data
