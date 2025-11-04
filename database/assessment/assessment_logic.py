from database.execute_service import DBExecuteService as db

class AssessmentLogic:
  @staticmethod
  def get_all_assessments_per_course(code_module: str,
                                     code_presentation:str):
    data = db.fetch_all("""
                        SELECT 
    assessment_type AS "Type",
    weight AS "Weight",
    date AS "Deadline Duration (in Days)" 
FROM 
    assessments assess 
JOIN 
    courses c 
    ON assess.code_module = c.code_module 
    AND assess.code_presentation = c.code_presentation
WHERE 
    c.code_module = %s
    AND c.code_presentation = %s;
                        """, params=(code_module,code_presentation))
    return data