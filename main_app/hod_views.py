import json
import requests
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import (HttpResponse, HttpResponseRedirect,
                              get_object_or_404, redirect, render)
from django.templatetags.static import static
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import UpdateView

from .forms import *
from .models import *


def admin_home(request):
    total_staff = Staff.objects.all().count()
    total_students = Student.objects.all().count()
    subjects = Subject.objects.all()
    total_subject = subjects.count()
    total_course = Curso.objects.all().count()
    attendance_list = Attendance.objects.filter(subject__in=subjects)
    total_attendance = attendance_list.count()
    attendance_list = []
    subject_list = []
    for subject in subjects:
        attendance_count = Attendance.objects.filter(subject=subject).count()
        subject_list.append(subject.nombre[:7])
        attendance_list.append(attendance_count)

    # Total Subjects and students in Each Course
    course_all = Curso.objects.all()
    course_name_list = []
    subject_count_list = []
    student_count_list_in_course = []

    for course in course_all:
        subjects = Subject.objects.filter(curso_id=course.id).count()
        students = Student.objects.filter(curso_id=course.id).count()
        course_name_list.append(course.nombre)
        subject_count_list.append(subjects)
        student_count_list_in_course.append(students)
    
    subject_all = Subject.objects.all()
    subject_list = []
    student_count_list_in_subject = []
    for subject in subject_all:
        course = Curso.objects.get(id=subject.curso.id)
        student_count = Student.objects.filter(curso_id=course.id).count()
        subject_list.append(subject.nombre)
        student_count_list_in_subject.append(student_count)


    # For Students
    student_attendance_present_list=[]
    student_attendance_leave_list=[]
    student_name_list=[]

    students = Student.objects.all()
    for student in students:
        
        attendance = AttendanceReport.objects.filter(student_id=student.id, status=True).count()
        absent = AttendanceReport.objects.filter(student_id=student.id, status=False).count()
        leave = LeaveReportStudent.objects.filter(student_id=student.id, status=1).count()
        student_attendance_present_list.append(attendance)
        student_attendance_leave_list.append(leave+absent)
        student_name_list.append(student.admin.nombre)

    context = {
        'page_title': "Panel de Administrador",
        'total_students': total_students,
        'total_staff': total_staff,
        'total_course': total_course,
        'total_subject': total_subject,
        'subject_list': subject_list,
        'attendance_list': attendance_list,
        'student_attendance_present_list': student_attendance_present_list,
        'student_attendance_leave_list': student_attendance_leave_list,
        "student_name_list": student_name_list,
        "student_count_list_in_subject": student_count_list_in_subject,
        "student_count_list_in_course": student_count_list_in_course,
        "course_name_list": course_name_list,

    }
    return render(request, 'hod_template/home_content.html', context)


def add_staff(request):
    form = StaffForm(request.POST or None, request.FILES or None)
    context = {'form': form, 'page_title': 'Añadir Docente'}
    if request.method == 'POST':
        if form.is_valid():
            nombre = form.cleaned_data.get('nombre')
            apellido = form.cleaned_data.get('apellido')
            dirección = form.cleaned_data.get('dirección')
            email = form.cleaned_data.get('email')
            genero = form.cleaned_data.get('genero')
            password = form.cleaned_data.get('password')
            nacionalidad = form.cleaned_data.get('nacionalidad')
            fecha_de_nacimiento = form.cleaned_data.get('fecha_de_nacimiento')
            numero_de_telefono = form.cleaned_data.get('numero_de_telefono')
            curso = form.cleaned_data.get('curso')
            passport = request.FILES.get('imagen_de_perfil')
            fs = FileSystemStorage()
            filename = fs.save(passport.name, passport)
            passport_url = fs.url(filename)
            try:
                user = CustomUser.objects.create_user(
                    email=email, password=password, user_type=2, nombre=nombre, apellido=apellido, imagen_de_perfil=passport_url)
                user.genero = genero
                user.dirección = dirección
                user.nacionalidad = nacionalidad
                user.fecha_de_nacimiento = fecha_de_nacimiento
                user.numero_de_telefono = numero_de_telefono
                user.staff.curso = curso
                user.save()
                messages.success(request, "Añadido exitosamente")
                return redirect(reverse('add_staff'))

            except Exception as e:
                messages.error(request, "No se pudo agregar " + str(e))
        else:
            messages.error(request, "Por favor cumple con todos los requisitos")

    return render(request, 'hod_template/add_staff_template.html', context)


def add_student(request):
    student_form = StudentForm(request.POST or None, request.FILES or None)
    context = {'form': student_form, 'page_title': 'Añadir Estudiante'}
    if request.method == 'POST':
        if student_form.is_valid():
            nombre = student_form.cleaned_data.get('nombre')
            apellido = student_form.cleaned_data.get('apellido')
            dirección = student_form.cleaned_data.get('dirección')
            email = student_form.cleaned_data.get('email')
            genero = student_form.cleaned_data.get('genero')
            password = student_form.cleaned_data.get('password')
            nacionalidad = student_form.cleaned_data.get('nacionalidad')
            fecha_de_nacimiento = student_form.cleaned_data.get('fecha_de_nacimiento')
            numero_de_telefono = student_form.cleaned_data.get('numero_de_telefono')
            curso = student_form.cleaned_data.get('curso')
            session = student_form.cleaned_data.get('session')
            passport = request.FILES['imagen_de_perfil']
            fs = FileSystemStorage()
            filename = fs.save(passport.name, passport)
            passport_url = fs.url(filename)
            try:
                user = CustomUser.objects.create_user(
                    email=email, password=password, user_type=3, nombre=nombre, apellido=apellido, imagen_de_perfil=passport_url)
                user.genero = genero
                user.dirección = dirección
                user.nacionalidad = nacionalidad
                user.fecha_de_nacimiento = fecha_de_nacimiento
                user.numero_de_telefono = numero_de_telefono
                user.student.session = session
                user.student.curso = curso
                user.save()
                messages.success(request, "Añadido exitosamente")
                return redirect(reverse('add_student'))
            except Exception as e:
                messages.error(request, "No se pudo agregar: " + str(e))
        else:
            messages.error(request, "No se pudo agregar ")
    return render(request, 'hod_template/add_student_template.html', context)


def add_course(request):
    form = CourseForm(request.POST or None)
    context = {
        'form': form,
        'page_title': 'Añadir curso'
    }
    if request.method == 'POST':
        if form.is_valid():
            nombre = form.cleaned_data.get('nombre')
            descripción = form.cleaned_data.get('descripción')
            try:
                course = Curso()
                course.descripción = descripción
                course.nombre = nombre
                course.save()
                messages.success(request, "Añadido exitosamente")
                return redirect(reverse('add_course'))
            except:
                messages.error(request, "No se pudo agregar")
        else:
            messages.error(request, "No se pudo agregar")
    return render(request, 'hod_template/add_course_template.html', context)


def add_subject(request):
    form = SubjectForm(request.POST or None)
    context = {
        'form': form,
        'page_title': 'Añadir asignatura'
    }
    if request.method == 'POST':
        if form.is_valid():
            nombre = form.cleaned_data.get('nombre')
            curso = form.cleaned_data.get('curso')
            docente = form.cleaned_data.get('docente')
            descripción = form.cleaned_data.get('descripción')
            try:
                subject = Subject()
                subject.nombre = nombre
                subject.docente = docente
                subject.curso = curso
                subject.descripción = descripción
                subject.save()
                messages.success(request, "Añadido exitosamente")
                return redirect(reverse('add_subject'))

            except Exception as e:
                messages.error(request, "No se pudo agregar " + str(e))
        else:
            messages.error(request, "No se pudo agregar")

    return render(request, 'hod_template/add_subject_template.html', context)


def manage_staff(request):
    allStaff = CustomUser.objects.filter(user_type=2)
    context = {
        'allStaff': allStaff,
        'page_title': 'Administrar docente'
    }
    return render(request, "hod_template/manage_staff.html", context)


def manage_student(request):
    students = CustomUser.objects.filter(user_type=3)
    context = {
        'students': students,
        'page_title': 'Administrar estudiante'
    }
    return render(request, "hod_template/manage_student.html", context)


def manage_course(request):
    courses = Curso.objects.all()
    context = {
        'courses': courses,
        'page_title': 'Administrar curso'
    }
    return render(request, "hod_template/manage_course.html", context)


def manage_subject(request):
    subjects = Subject.objects.all()
    context = {
        'subjects': subjects,
        'page_title': 'Administrar asignatura'
    }
    return render(request, "hod_template/manage_subject.html", context)


def edit_staff(request, staff_id):
    docente = get_object_or_404(Staff, id=staff_id)
    form = StaffForm(request.POST or None, instance=docente)
    context = {
        'form': form,
        'staff_id': staff_id,
        'page_title': 'Editar docente'
    }
    if request.method == 'POST':
        if form.is_valid():
            nombre = form.cleaned_data.get('nombre')
            apellido = form.cleaned_data.get('apellido')
            dirección = form.cleaned_data.get('dirección')
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            genero = form.cleaned_data.get('genero') or None
            password = form.cleaned_data.get('password') or None
            nacionalidad = form.cleaned_data.get('nacionalidad')
            fecha_de_nacimiento = form.cleaned_data.get('fecha_de_nacimiento')
            numero_de_telefono = form.cleaned_data.get('numero_de_telefono')
            curso = form.cleaned_data.get('curso')
            passport = request.FILES.get('imagen_de_perfil') or None
            try:
                user = CustomUser.objects.get(id=docente.admin.id)
                user.username = username
                user.email = email
                if password != None:
                    user.set_password(password)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    user.imagen_de_perfil = passport_url
                user.nombre = nombre
                user.apellido = apellido
                user.genero = genero
                user.dirección = dirección
                user.nacionalidad = nacionalidad
                user.fecha_de_nacimiento = fecha_de_nacimiento
                user.numero_de_telefono = numero_de_telefono
                docente.curso = curso
                user.save()
                docente.save()
                messages.success(request, "Añadido exitosamente")
                return redirect(reverse('edit_staff', args=[staff_id]))
            except Exception as e:
                messages.error(request, "No se pudo agregar " + str(e))
        else:
            messages.error(request, "No se pudo agregar")
    else:
        user = CustomUser.objects.get(id=staff_id)
        docente = Staff.objects.get(id=user.id)
        return render(request, "hod_template/edit_staff_template.html", context)


def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    form = StudentForm(request.POST or None, instance=student)
    context = {
        'form': form,
        'student_id': student_id,
        'page_title': 'Editar Estudiante'
    }
    if request.method == 'POST':
        if form.is_valid():
            nombre = form.cleaned_data.get('nombre')
            apellido = form.cleaned_data.get('apellido')
            dirección = form.cleaned_data.get('dirección')
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            genero = form.cleaned_data.get('genero')
            password = form.cleaned_data.get('password') or None
            nacionalidad = form.cleaned_data.get('nacionalidad')
            fecha_de_nacimiento = form.cleaned_data.get('fecha_de_nacimiento')
            numero_de_telefono = form.cleaned_data.get('numero_de_telefono')
            curso = form.cleaned_data.get('curso')
            session = form.cleaned_data.get('session')
            passport = request.FILES.get('imagen_de_perfil') or None
            try:
                user = CustomUser.objects.get(id=student.admin.id)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    user.imagen_de_perfil = passport_url
                user.username = username
                user.email = email
                if password != None:
                    user.set_password(password)
                user.nombre = nombre
                user.apellido = apellido
                student.session = session
                user.genero = genero
                user.dirección = dirección
                user.nacionalidad = nacionalidad
                user.fecha_de_nacimiento = fecha_de_nacimiento
                user.numero_de_telefono = numero_de_telefono
                student.curso = curso
                user.save()
                student.save()
                messages.success(request, "Añadido exitosamente")
                return redirect(reverse('edit_student', args=[student_id]))
            except Exception as e:
                messages.error(request, "No se pudo agregar " + str(e))
        else:
            messages.error(request, "No se pudo agregar")
    else:
        return render(request, "hod_template/edit_student_template.html", context)


def edit_course(request, course_id):
    instance = get_object_or_404(Curso, id=course_id)
    form = CourseForm(request.POST or None, instance=instance)
    context = {
        'form': form,
        'course_id': course_id,
        'page_title': 'Editar curso'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('nombre')
            descripción = form.cleaned_data.get('descripción')
            try:
                course = Curso.objects.get(id=course_id)
                course.descripción = descripción
                course.nombre = name
                course.save()
                messages.success(request, "Añadido exitosamente")
            except:
                messages.error(request, "No se pudo agregar")
        else:
            messages.error(request, "No se pudo agregar")

    return render(request, 'hod_template/edit_course_template.html', context)


def edit_subject(request, subject_id):
    instance = get_object_or_404(Subject, id=subject_id)
    form = SubjectForm(request.POST or None, instance=instance)
    context = {
        'form': form,
        'subject_id': subject_id,
        'page_title': 'Editar asignatura'
    }
    if request.method == 'POST':
        if form.is_valid():
            nombre = form.cleaned_data.get('nombre')
            curso = form.cleaned_data.get('curso')
            docente = form.cleaned_data.get('docente')
            descripción = form.cleaned_data.get('descripción')
            try:
                subject = Subject.objects.get(id=subject_id)
                subject.name = nombre
                subject.docente = docente
                subject.curso = curso
                subject.descripción = descripción
                subject.save()
                messages.success(request, "Añadido exitosamente")
                return redirect(reverse('edit_subject', args=[subject_id]))
            except Exception as e:
                messages.error(request, "No se pudo agregar " + str(e))
        else:
            messages.error(request, "No se pudo agregar")
    return render(request, 'hod_template/edit_subject_template.html', context)


def add_session(request):
    form = SessionForm(request.POST or None)
    context = {'form': form, 'page_title': 'Añadir Duración'}
    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Añadido exitosamente")
                return redirect(reverse('add_session'))
            except Exception as e:
                messages.error(request, 'No se pudo agregar ' + str(e))
        else:
            messages.error(request, 'No se pudo agregar ')
    return render(request, "hod_template/add_session_template.html", context)


def manage_session(request):
    sessions = Session.objects.all()
    context = {'sessions': sessions, 'page_title': 'Administrar Duración'}
    return render(request, "hod_template/manage_session.html", context)


def edit_session(request, session_id):
    instance = get_object_or_404(Session, id=session_id)
    form = SessionForm(request.POST or None, instance=instance)
    context = {'form': form, 'session_id': session_id, 'page_title': 'Editar Duración'}
    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Sesión actualizada")
                return redirect(reverse('edit_session', args=[session_id]))
            except Exception as e:
                messages.error(
                    request, "No se pudo agregar " + str(e))
                return render(request, "hod_template/edit_session_template.html", context)
        else:
            messages.error(request, "No se pudo agregar ")
            return render(request, "hod_template/edit_session_template.html", context)
    else:
        return render(request, "hod_template/edit_session_template.html", context)

@csrf_exempt
def check_email_availability(request):
    email = request.POST.get("email")
    try:
        user = CustomUser.objects.filter(email=email).exists()
        if user:
            return HttpResponse(True)
        return HttpResponse(False)
    except Exception as e:
        return HttpResponse(False)


@csrf_exempt
def student_feedback_message(request):
    if request.method != 'POST':
        comentarios = FeedbackStudent.objects.all()
        context = {
            'comentarios': comentarios,
            'page_title': 'Comentarios de estudiantes'
        }
        return render(request, 'hod_template/student_feedback_template.html', context)
    else:
        comentario_id = request.POST.get('id')
        try:
            comentario = get_object_or_404(FeedbackStudent, id=comentario_id)
            reply = request.POST.get('reply')
            comentario.reply = reply
            comentario.save()
            return HttpResponse(True)
        except Exception as e:
            return HttpResponse(False)

@csrf_exempt
def staff_feedback_message(request):
    if request.method != 'POST':
        comentarios = FeedbackStaff.objects.all()
        context = {
            'comentarios': comentarios,
            'page_title': 'Comentarios de docentes'
        }
        return render(request, 'hod_template/staff_feedback_template.html', context)
    else:
        comentario_id = request.POST.get('id')
        try:
            comentario = get_object_or_404(FeedbackStaff, id=comentario_id)
            reply = request.POST.get('reply')
            comentario.reply = reply
            comentario.save()
            return HttpResponse(True)
        except Exception as e:
            return HttpResponse(False)


@csrf_exempt
def view_staff_leave(request):
    if request.method != 'POST':
        allLeave = LeaveReportStaff.objects.all()
        context = {
            'allLeave': allLeave,
            'page_title': 'Salir de la aplicacion'
        }
        return render(request, "hod_template/staff_leave_view.html", context)
    else:
        id = request.POST.get('id')
        status = request.POST.get('status')
        if (status == '1'):
            status = 1
        else:
            status = -1
        try:
            leave = get_object_or_404(LeaveReportStaff, id=id)
            leave.status = status
            leave.save()
            return HttpResponse(True)
        except Exception as e:
            return False


@csrf_exempt
def view_student_leave(request):
    if request.method != 'POST':
        allLeave = LeaveReportStudent.objects.all()
        context = {
            'allLeave': allLeave,
            'page_title': 'Salir de la aplicacion'
        }
        return render(request, "hod_template/student_leave_view.html", context)
    else:
        id = request.POST.get('id')
        status = request.POST.get('status')
        if (status == '1'):
            status = 1
        else:
            status = -1
        try:
            leave = get_object_or_404(LeaveReportStudent, id=id)
            leave.status = status
            leave.save()
            return HttpResponse(True)
        except Exception as e:
            return False


def admin_view_attendance(request):
    subjects = Subject.objects.all()
    sessions = Session.objects.all()
    context = {
        'subjects': subjects,
        'sessions': sessions,
        'page_title': 'Ver asistencia'
    }

    return render(request, "hod_template/admin_view_attendance.html", context)


@csrf_exempt
def get_admin_attendance(request):
    subject_id = request.POST.get('subject')
    session_id = request.POST.get('session')
    attendance_date_id = request.POST.get('attendance_date_id')
    try:
        subject = get_object_or_404(Subject, id=subject_id)
        session = get_object_or_404(Session, id=session_id)
        attendance = get_object_or_404(
            Attendance, id=attendance_date_id, session=session)
        attendance_reports = AttendanceReport.objects.filter(
            attendance=attendance)
        json_data = []
        for report in attendance_reports:
            data = {
                "status":  str(report.status),
                "name": str(report.student)
            }
            json_data.append(data)
        return JsonResponse(json.dumps(json_data), safe=False)
    except Exception as e:
        return None


def admin_view_profile(request):
    admin = get_object_or_404(Admin, admin=request.user)
    form = AdminForm(request.POST or None, request.FILES or None,
                     instance=admin)
    context = {'form': form,
               'page_title': 'Editar perfil'
               }
    if request.method == 'POST':
        try:
            if form.is_valid():
                nombre = form.cleaned_data.get('nombre')
                apellido = form.cleaned_data.get('apellido')
                nacionalidad = form.cleaned_data.get('nacionalidad')
                fecha_de_nacimiento = form.cleaned_data.get('fecha_de_nacimiento')
                numero_de_telefono = form.cleaned_data.get('numero_de_telefono')
                dirección = form.cleaned_data.get('dirección')
                genero = form.cleaned_data.get('genero')
                password = form.cleaned_data.get('password') or None
                passport = request.FILES.get('imagen_de_perfil') or None
                custom_user = admin.admin
                if password != None:
                    custom_user.set_password(password)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    custom_user.imagen_de_perfil = passport_url
                custom_user.nombre = nombre
                custom_user.apellido = apellido
                custom_user.nacionalidad = nacionalidad
                custom_user.fecha_de_nacimiento = fecha_de_nacimiento
                custom_user.numero_de_telefono = numero_de_telefono
                custom_user.dirección = dirección
                custom_user.genero = genero
                custom_user.save()
                messages.success(request, "Perfil actualizado")
                return redirect(reverse('admin_view_profile'))
            else:
                messages.error(request, "Datos no válidos")
        except Exception as e:
            messages.error(
                request, "Error " + str(e))
    return render(request, "hod_template/admin_view_profile.html", context)


def admin_notify_staff(request):
    docente = CustomUser.objects.filter(user_type=2)
    context = {
        'page_title': "Enviar anuncio a docente",
        'allStaff': docente
    }
    return render(request, "hod_template/staff_notification.html", context)


def admin_notify_student(request):
    student = CustomUser.objects.filter(user_type=3)
    context = {
        'page_title': "Enviar anuncio a estudiante",
        'students': student
    }
    return render(request, "hod_template/student_notification.html", context)


@csrf_exempt
def send_student_notification(request):
    id = request.POST.get('id')
    message = request.POST.get('message')
    student = get_object_or_404(Student, admin_id=id)
    try:
        url = "https://fcm.googleapis.com/fcm/send"
        body = {
            'notification': {
                'title': "Systema",
                'body': message,
                'click_action': reverse('student_view_notification'),
                'icon': static('dist/img/AdminLTELogo.png')
            },
            'to': student.admin.fcm_token
        }
        headers = {'Authorization':
                   'key=AAAA3Bm8j_M:APA91bElZlOLetwV696SoEtgzpJr2qbxBfxVBfDWFiopBWzfCfzQp2nRyC7_A2mlukZEHV4g1AmyC6P_HonvSkY2YyliKt5tT3fe_1lrKod2Daigzhb2xnYQMxUWjCAIQcUexAMPZePB',
                   'Content-Type': 'application/json'}
        data = requests.post(url, data=json.dumps(body), headers=headers)
        notification = NotificationStudent(student=student, message=message)
        notification.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


@csrf_exempt
def send_staff_notification(request):
    id = request.POST.get('id')
    message = request.POST.get('message')
    docente = get_object_or_404(Staff, admin_id=id)
    try:
        url = "https://fcm.googleapis.com/fcm/send"
        body = {
            'notification': {
                'title': "Sistema de gestión de estudiantes",
                'body': message,
                'click_action': reverse('staff_view_notification'),
                'icon': static('dist/img/AdminLTELogo.png')
            },
            'to': docente.admin.fcm_token
        }
        headers = {'Authorization':
                   'key=AAAA3Bm8j_M:APA91bElZlOLetwV696SoEtgzpJr2qbxBfxVBfDWFiopBWzfCfzQp2nRyC7_A2mlukZEHV4g1AmyC6P_HonvSkY2YyliKt5tT3fe_1lrKod2Daigzhb2xnYQMxUWjCAIQcUexAMPZePB',
                   'Content-Type': 'application/json'}
        data = requests.post(url, data=json.dumps(body), headers=headers)
        notification = NotificationStaff(docente=docente, message=message)
        notification.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


def delete_staff(request, staff_id):
    docente = get_object_or_404(CustomUser, staff__id=staff_id)
    docente.delete()
    messages.success(request, "Docente eliminado")
    return redirect(reverse('manage_staff'))


def delete_student(request, student_id):
    student = get_object_or_404(CustomUser, student__id=student_id)
    student.delete()
    messages.success(request, "Estudiante eliminado")
    return redirect(reverse('manage_student'))


def delete_course(request, course_id):
    course = get_object_or_404(Curso, id=course_id)
    try:
        course.delete()
        messages.success(request, "Curso eliminado")
    except Exception:
        messages.error(
            request, "Lo sentimos, algunos estudiantes ya están asignados a este curso. Por favor cambie el curso del estudiante afectado y vuelva a intentarlo.")
    return redirect(reverse('manage_course'))


def delete_subject(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    subject.delete()
    messages.success(request, "Asignatura eliminada")
    return redirect(reverse('manage_subject'))


def delete_session(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    try:
        session.delete()
        messages.success(request, "Sesión eliminada")
    except Exception:
        messages.error(
            request, "Hay estudiantes asignados a esta sesión. Muévalos a otra sesión.")
    return redirect(reverse('manage_session'))
