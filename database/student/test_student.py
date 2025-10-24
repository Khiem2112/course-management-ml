from database.student.student import get_top_5_highest_score_student, get_student_score_per_course

if __name__ == "__main__":
    from pprint import pprint

    print(" TẤT CẢ ĐIỂM TRUNG BÌNH MỖI KHÓA ")
    pprint(get_student_score_per_course())

    print("\n TOP 5 SINH VIÊN CÓ ĐIỂM CAO NHẤT ")
    pprint(get_top_5_highest_score_student())
