from fastapi import FastAPI, HTTPException,status,Response
from pydantic import BaseModel, HttpUrl
import psycopg2
from psycopg2.extras import RealDictCursor
import time

app = FastAPI()

class Courses(BaseModel):
    course_code: str
    name: str
    coordinator_name: str
    total_sections: int
    credit: int
    lab: bool

while True:
    try:
        conn=psycopg2.connect(
                host="localhost",
                database="CSE",
                user="postgres",
                password= "1234",
                cursor_factory=RealDictCursor
            )
        cursor=conn.cursor()
        print("Database connected successfully!!")
        break
    except Exception as error:
        print("Database connection failed!!")
        print("Error:", error)
        time.sleep(2)

@app.post("/add_course")
def addCourse(post : Courses):
    cursor.execute(
    'INSERT INTO "Courses" VALUES (%s,%s,%s,%s,%s,%s) returning *',
    (post.course_code, post.name, post.coordinator_name, post.total_sections, post.credit, post.lab)
)

    newPost=cursor.fetchall()
    conn.commit()
    return {"Inserted": newPost}

@app.get("/")
def get_courses():
    cursor.execute('select * from "Courses"')
    data= cursor.fetchall()
    return {
        "Data": data
    }


@app.get("/course/{course_code}")
def getName(course_code:str):
    cursor.execute('select * from "Courses" where course_code=%s',(str(course_code),))
    course=cursor.fetchone()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The course {course_code} not found!!"
        )
    return {
        "Course details": course
    }

@app.delete("/course/{course_code}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(course_code: str):
    cursor.execute("""DELETE FROM "Courses" WHERE course_code = %s returning * """, ((str(course_code),)))
    deleted_course = cursor.fetchone()
    conn.commit()
    if deleted_course == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"course with id: {course_code} does not exist")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/course/{course_code}")
def update_course(course_code: str, course: Courses):
    cursor.execute(
        '''UPDATE "Courses" SET name=%s, coordinator_name=%s, total_sections=%s, credit=%s, lab=%s
           WHERE course_code=%s RETURNING *''',
        (course.name, course.coordinator_name, course.total_sections, course.credit, course.lab, course_code)
    )
    updated = cursor.fetchone()
    conn.commit()
    if updated is None:
        raise HTTPException(status_code=404, detail="Course not found")
    return updated
