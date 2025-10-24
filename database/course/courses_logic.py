from database.execute_service import DBExecuteService as db
from utils.logger import get_class_logger

logger = get_class_logger(__name__, "CoursesLogic")

class CoursesLogic:
    @staticmethod
    def get_all_courses(limit=100):
        if limit:
            query = "SELECT code_module, code_presentation FROM courses LIMIT %s;"
            data = db.fetch_all(query, (limit,))
        else:
            query = "SELECT code_module, code_presentation FROM courses;"
            data = db.fetch_all(query)
        logger.info(f"Fetched {len(data)} courses.")
        return data
    @staticmethod
    def get_students_by_course(code_module):
        """
        Lấy danh sách sinh viên trong một khóa học,
        gồm: id_student, date_registration, date_unregistration, id_assessment, score.
        """
        query = """
        SELECT 
            stu_reg.id_student,
            stu_reg.date_registration,
            stu_reg.date_unregistration,
            stu_assess.id_assessment,
            stu_assess.score
        FROM courses AS c
            JOIN studentRegistration AS stu_reg 
                ON c.code_module = stu_reg.code_module 
                AND c.code_presentation = stu_reg.code_presentation
            JOIN studentAssessment AS stu_assess 
                ON stu_reg.id_student = stu_assess.id_student
            JOIN studentInfo AS stu_info 
                ON stu_reg.id_student = stu_info.id_student
        WHERE c.code_module = %s
        LIMIT 100;
        """
        data = db.fetch_all(query, (code_module,))
        logger.info(f"Fetched {len(data)} students for course {code_module}.")
        return data

    @staticmethod
    def get_assessments_by_course(code_module):
        """
        Lấy danh sách bài đánh giá của khóa học,
        gồm: id_assessment, assessment_type, date, weight.
        """
        query = """
        SELECT 
            id_assessment,
            assessment_type,
            date,
            weight
        FROM assessments
        WHERE code_module = %s
        LIMIT 100;
        """
        data = db.fetch_all(query, (code_module,))
        logger.info(f"Fetched {len(data)} assessments for course {code_module}.")
        return data

    @staticmethod
    def get_course_statistics(code_module):
        """
        Lấy thống kê điểm số cho khóa học:
        Min, Max, Mean, Mode.
        """
        query = """
        SELECT
            MIN(stu_assess.score) AS min_score,
            MAX(stu_assess.score) AS max_score,
            AVG(stu_assess.score) AS mean_score,
            (
                SELECT sa.score
                FROM studentAssessment AS sa
                    JOIN assessments AS a ON sa.id_assessment = a.id_assessment
                WHERE a.code_module = %s
                GROUP BY sa.score
                ORDER BY COUNT(*) DESC
                LIMIT 1
            ) AS mode_score
        FROM studentAssessment AS stu_assess
            JOIN assessments AS assess ON stu_assess.id_assessment = assess.id_assessment
        WHERE assess.code_module = %s;
        """
        data = db.fetch_one(query, (code_module, code_module))
        logger.info(f"Statistics fetched for course {code_module}: {data}")
        return data

    @staticmethod
    def get_top5_students_by_score(code_module):
        """
        Lấy top 5 sinh viên có điểm trung bình cao nhất trong khóa học.
        """
        query_top5 = """
        SELECT 
            sa.id_student,
            AVG(sa.score) AS avg_score
        FROM studentAssessment sa
            JOIN assessments a ON sa.id_assessment = a.id_assessment
        WHERE a.code_module = %s
        GROUP BY sa.id_student
        ORDER BY avg_score DESC
        LIMIT 5;
        """
        top5 = db.fetch_all(query_top5, (code_module,))
        logger.info(f"Fetched top 5 students for {code_module}.")
        return top5

    @staticmethod
    def get_unregistration_rate(code_module):
        """
        Tính tỉ lệ sinh viên unregistration trong khóa học.
        """
        query = """
        SELECT
            COUNT(CASE WHEN date_unregistration IS NOT NULL THEN 1 END) * 100.0 / COUNT(*) AS unregistration_rate,
            COUNT(CASE WHEN date_unregistration IS NULL THEN 1 END) * 100.0 / COUNT(*) AS registration_rate
        FROM studentRegistration
        WHERE code_module = %s;
        """
        data = db.fetch_one(query, (code_module,))
        logger.info(f"Unregistration rate fetched for course {code_module}: {data}")
        return data
