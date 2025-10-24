from database.course.courses_logic import CoursesLogic

if __name__ == "__main__":
    courses = CoursesLogic.get_all_courses()

    all_courses_data = {}

    for c in courses:
        code_module = c['code_module']
        print(f"\n-- KHÓA HỌC: {code_module} --")

        # Lấy dữ liệu từng course
        students = CoursesLogic.get_students_by_course(code_module)
        assessments = CoursesLogic.get_assessments_by_course(code_module)
        stats = CoursesLogic.get_course_statistics(code_module)
        top5 = CoursesLogic.get_top5_students_by_score(code_module)
        rate = CoursesLogic.get_unregistration_rate(code_module)

        # Lưu vào dict
        all_courses_data[code_module] = {
            'students': students,
            'assessments': assessments,
            'stats': stats,
            'top5': top5,
            'rate': rate
        }

    # In dữ liệu
    for code, data in all_courses_data.items():
        print(f"\n>>> KHÓA HỌC {code} <<<")
        print(f"Sinh viên ({len(data['students'])}):")
        for s in data['students'][:5]:  # chỉ in 5 dòng đầu
            print(s)
        print(f"Assessment ({len(data['assessments'])}):")
        for a in data['assessments']:
            print(a)
        print("Stats:", data['stats'])
        print("Top 5:", data['top5'])
        print("Rate:", data['rate'])
