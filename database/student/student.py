from database.execute_service import DBExecuteService as db

def get_student_score_per_course():
  data = db.fetch_all(query="""
               select stu_info.id_student, courses.code_module, courses.code_presentation, avg(stu_assess.score) as avg_score from 
              courses join assessments assess on courses.code_module = assess.code_module and courses.code_presentation = assess.code_presentation 
              join studentAssessment stu_assess on assess.id_assessment = stu_assess.id_assessment
              join studentInfo stu_info  on stu_info.id_student = stu_assess.id_student
              group by  stu_info.id_student, courses.code_module, courses.code_presentation
               """)
  return data

def get_top_5_highest_score_student():
  data = db.fetch_all(query="""
                      select stu_info.id_student, courses.code_module, courses.code_presentation, avg(stu_assess.score) as avg_score from 

  courses join assessments assess on courses.code_module = assess.code_module and courses.code_presentation = assess.code_presentation 
  join studentAssessment stu_assess on assess.id_assessment = stu_assess.id_assessment
  join studentInfo stu_info  on stu_info.id_student = stu_assess.id_student
  group by  stu_info.id_student, courses.code_module, courses.code_presentation
  ORDER by avg_score DESC
  limit 5""")
  return data

