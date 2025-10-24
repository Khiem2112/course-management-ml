from database.execute_service import DBExecuteService as db

def get_all_course():
  data = db.fetch_all(query="""
               select stu_info.id_student, courses.code_module, courses.code_presentation, avg(stu_assess.score) as avg_score from 
              courses join assessments assess on courses.code_module = assess.code_module and courses.code_presentation = assess.code_presentation 
              join studentAssessment stu_assess on assess.id_assessment = stu_assess.id_assessment
              join studentInfo stu_info  on stu_info.id_student = stu_assess.id_student
              group by  stu_info.id_student, courses.code_module, courses.code_presentation
               """)
  return data

def get_n_highest_score_student(code_module: str, code_presentation: str, n:int):
  data = db.fetch_all(query="""
                      select id_student, courses.code_module, courses.code_presentation, AVG(score) as avg_student_score  from courses 
                      join assessments on courses.code_module = assessments.code_module and courses.code_presentation = assessments.code_presentation
                      join studentAssessment stu_assessment on stu_assessment.id_assessment = assessments.id_assessment
                      WHERE assessments.code_module = %s and courses.code_presentation = %s
                      group by stu_assessment.id_student
                      ORDER BY avg_student_score DESC
                      limit %s
""", params=(code_module,code_presentation,n))
  return data
def get_dropout_percentage(code_module: str, code_presentation: str):
  data= db.fetch_one(query="""
                     SELECT
                    SUM(CASE WHEN date_unregistration IS NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS Dropout,
                    SUM(CASE WHEN date_unregistration IS NULL THEN 0 ELSE 1 END) * 100.0 / COUNT(*) AS Retention
                FROM
                    studentRegistration;
                    where code_module =%s and code_presentation = %s

                     """,params=(code_module,code_presentation))
  return data

def get_student_score_statistic(code_module: str, code_presentation: str)-> dict:
  data = db.fetch_one(query="""
                      WITH student_score AS (
    SELECT AVG(score) as avg_score
    FROM studentAssessment stu_assess 
    JOIN assessments ON stu_assess.id_assessment = assessments.id_assessment
    WHERE code_module =%s AND code_presentation = %s
    GROUP BY id_student
)
SELECT 
    MIN(avg_score) as min_score,
    MAX(avg_score) as max_score,
    AVG(avg_score) as mean_score,
    (
        SELECT avg_score
        FROM student_score
        GROUP BY avg_score
        ORDER BY COUNT(*) DESC, avg_score ASC -- Order by frequency, then value to break ties
        LIMIT 1
    ) as mode_score
FROM 
    student_score;
                      """, params=(code_module,code_presentation))
  return data