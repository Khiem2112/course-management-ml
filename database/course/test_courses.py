from database.course.courses_logic import CoursesLogic

if __name__ == "__main__":
    code_module = input("Nhập mã khóa học (vd: AAA): ")

    # student
    students = CoursesLogic.get_students_by_course(code_module)
    print(f"\n-- DANH SÁCH SINH VIÊN ({code_module}) --")
    print(f"Tổng số sinh viên: {len(students)}")
    for s in students[:10]:
        print(s)

    # assessments
    assessments = CoursesLogic.get_assessments_by_course(code_module)
    print(f"\n-- DANH SÁCH ASSESSMENTS ({code_module}) --")
    print(f"Tổng số bài đánh giá: {len(assessments)}")
    for a in assessments:
        print(a)
    #result
    print("Students:", CoursesLogic.get_students_by_course(code_module))
    print("Assessments:", CoursesLogic.get_assessments_by_course(code_module))
    print("Stats:", CoursesLogic.get_course_statistics(code_module))
    print("Top 5:", CoursesLogic.get_top5_students_by_score(code_module))
    print("Rate:", CoursesLogic.get_unregistration_rate(code_module))
