from database.execute_service import DBExecuteService as db
from utils.logger import get_class_logger

logger = get_class_logger(__name__, "StudentsLogic")


class StudentsLogic:
    @staticmethod
    def get_student_score_per_course():
        query = """
            SELECT stu_info.id_student, 
                   courses.code_module, 
                   courses.code_presentation, 
                   AVG(stu_assess.score) AS avg_score
            FROM courses
                JOIN assessments assess 
                    ON courses.code_module = assess.code_module 
                    AND courses.code_presentation = assess.code_presentation
                JOIN studentAssessment stu_assess 
                    ON assess.id_assessment = stu_assess.id_assessment
                JOIN studentInfo stu_info  
                    ON stu_info.id_student = stu_assess.id_student
            GROUP BY stu_info.id_student, courses.code_module, courses.code_presentation;
        """
        data = db.fetch_all(query)
        logger.info(f"Fetched {len(data)} student scores per course.")
        return data

    @staticmethod
    def get_top_5_highest_score_student():
        query = """
            SELECT stu_info.id_student, 
                   courses.code_module, 
                   courses.code_presentation, 
                   AVG(stu_assess.score) AS avg_score
            FROM courses
                JOIN assessments assess 
                    ON courses.code_module = assess.code_module 
                    AND courses.code_presentation = assess.code_presentation
                JOIN studentAssessment stu_assess 
                    ON assess.id_assessment = stu_assess.id_assessment
                JOIN studentInfo stu_info  
                    ON stu_info.id_student = stu_assess.id_student
            GROUP BY stu_info.id_student, courses.code_module, courses.code_presentation
            ORDER BY avg_score DESC
            LIMIT 5;
        """
        data = db.fetch_all(query)
        logger.info("Fetched top 5 students with highest average scores.")
        return data

    @staticmethod
    def get_all_students(code_module=None, keyword=None):
        query = """
            SELECT code_module, code_presentation, id_student, gender
            FROM studentInfo
        """
        conditions = []
        params = []

        if code_module and code_module != "All":
            conditions.append("code_module = %s")
            params.append(code_module)

        if keyword:
            conditions.append("(id_student LIKE %s OR gender LIKE %s)")
            params.extend([f"%{keyword}%", f"%{keyword}%"])

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        data = db.fetch_all(query, params)
        logger.info(f"Fetched {len(data)} students with filters: {code_module=}, {keyword=}.")
        return data
    
    @staticmethod 
    def get_student_per_course(code_module:str, code_presentation: str) -> list[dict]:
        data = db.fetch_all("""
        SELECT
        name_student,
        (CASE gender
        WHEN 'M' THEN 'Male'
        WHEN 'F' THEN 'Female'
        END) AS gender, -- Added END and an alias
        region,
        highest_education,
        imd_band
        FROM studentInfo
        WHERE
        code_module = %s
        AND code_presentation = %s;
                            """, params=(code_module,code_presentation))
        return data
    
    @staticmethod
    def get_all_clusters():
        query = """
        SELECT
    count(id_student) AS total_student,
    CASE
        WHEN cluster_id IS NULL THEN 'not clustered'
        ELSE CAST(cluster_id AS CHAR) -- Convert the cluster_id (assuming it's a number) to a string for consistency
    END AS cluster_id
FROM
    studentInfo
GROUP BY
    cluster_id;
        """
        data = db.fetch_all(query)
        return data