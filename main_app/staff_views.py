import json

from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import (HttpResponseRedirect, get_object_or_404,redirect, render)
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .forms import *
from .models import *


def staff_home(request):
    docente = get_object_or_404(Staff, admin=request.user)
    total_students = Student.objects.filter(curso=docente.curso).count()
    total_leave = LeaveReportStaff.objects.filter(docente=docente).count()
    subjects = Subject.objects.filter(docente=docente)
    total_subject = subjects.count()
    attendance_list = Attendance.objects.filter(subject__in=subjects)
    total_attendance = attendance_list.count()
    attendance_list = []
    subject_list = []
    for subject in subjects:
        attendance_count = Attendance.objects.filter(subject=subject).count()
        subject_list.append(subject.nombre)
        attendance_list.append(attendance_count)
    context = {
        'page_title': 'Panel Docente - ' + ' (' + str(docente.curso) + ')',
        'total_students': total_students,
        'total_attendance': total_attendance,
        'total_leave': total_leave,
        'total_subject': total_subject,
        'subject_list': subject_list,
        'attendance_list': attendance_list
    }
    return render(request, 'staff_template/home_content.html', context)


def staff_take_attendance(request):
    docente = get_object_or_404(Staff, admin=request.user)
    subjects = Subject.objects.filter(staff_id=docente)
    sessions = Session.objects.all()
    context = {
        'subjects': subjects,
        'sessions': sessions,
        'page_title': 'Tomar la asistencia'
    }

    return render(request, 'staff_template/staff_take_attendance.html', context)


@csrf_exempt
def get_students(request):
    subject_id = request.POST.get('subject')
    session_id = request.POST.get('session')
    try:
        subject = get_object_or_404(Subject, id=subject_id)
        session = get_object_or_404(Session, id=session_id)
        students = Student.objects.filter(
            course_id=subject.curso.id, session=session)
        student_data = []
        for student in students:
            data = {
                    "id": student.id,
                    "nombre": student.admin.nombre + " " + student.admin.apellido
                    }
            student_data.append(data)
        return JsonResponse(json.dumps(student_data), content_type='application/json', safe=False)
    except Exception as e:
        return e


@csrf_exempt
def save_attendance(request):
    student_data = request.POST.get('student_ids')
    date = request.POST.get('date')
    subject_id = request.POST.get('subject')
    session_id = request.POST.get('session')
    students = json.loads(student_data)
    try:
        session = get_object_or_404(Session, id=session_id)
        subject = get_object_or_404(Subject, id=subject_id)
        attendance = Attendance(session=session, subject=subject, date=date)
        attendance.save()

        for student_dict in students:
            student = get_object_or_404(Student, id=student_dict.get('id'))
            attendance_report = AttendanceReport(student=student, attendance=attendance, status=student_dict.get('status'))
            attendance_report.save()
    except Exception as e:
        return None

    return HttpResponse("OK")


def staff_update_attendance(request):
    docente = get_object_or_404(Staff, admin=request.user)
    subjects = Subject.objects.filter(staff_id=docente)
    sessions = Session.objects.all()
    context = {
        'subjects': subjects,
        'sessions': sessions,
        'page_title': 'Actualizar asistencia'
    }

    return render(request, 'staff_template/staff_update_attendance.html', context)


@csrf_exempt
def get_student_attendance(request):
    attendance_date_id = request.POST.get('attendance_date_id')
    try:
        date = get_object_or_404(Attendance, id=attendance_date_id)
        attendance_data = AttendanceReport.objects.filter(attendance=date)
        student_data = []
        for attendance in attendance_data:
            data = {"id": attendance.student.admin.id,
                    "nombre":  attendance.student.admin.nombre + " " + attendance.student.admin.apellido,
                    "status": attendance.status}
            student_data.append(data)
        return JsonResponse(json.dumps(student_data), content_type='application/json', safe=False)
    except Exception as e:
        return e


@csrf_exempt
def update_attendance(request):
    student_data = request.POST.get('student_ids')
    date = request.POST.get('date')
    students = json.loads(student_data)
    try:
        attendance = get_object_or_404(Attendance, id=date)

        for student_dict in students:
            student = get_object_or_404(
                Student, admin_id=student_dict.get('id'))
            attendance_report = get_object_or_404(AttendanceReport, student=student, attendance=attendance)
            attendance_report.status = student_dict.get('status')
            attendance_report.save()
    except Exception as e:
        return None

    return HttpResponse("OK")


def staff_apply_leave(request):
    form = LeaveReportStaffForm(request.POST or None)
    docente = get_object_or_404(Staff, admin_id=request.user.id)
    context = {
        'form': form,
        'leave_history': LeaveReportStaff.objects.filter(docente=docente),
        'page_title': 'Solicitar permiso'
    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.docente = docente
                obj.save()
                messages.success(
                    request, " ")
                return redirect(reverse('staff_apply_leave'))
            except Exception:
                messages.error(request, "No se aplico")
        else:
            messages.error(request, "Hay algun error")
    return render(request, "staff_template/staff_apply_leave.html", context)


def staff_feedback(request):
    form = FeedbackStaffForm(request.POST or None)
    docente = get_object_or_404(Staff, admin_id=request.user.id)
    context = {
        'form': form,
        'comentarios': FeedbackStaff.objects.filter(docente=docente),
        'page_title': 'Agregar comentarios'
    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.docente = docente
                obj.save()
                messages.success(request, "Comentarios enviados para revisión")
                return redirect(reverse('staff_feedback'))
            except Exception:
                messages.error(request, "No se pudo enviar")
        else:
            messages.error(request, "No se pudo enviar")
    return render(request, "staff_template/staff_feedback.html", context)


def staff_view_profile(request):
    docente = get_object_or_404(Staff, admin=request.user)
    form = StaffEditForm(request.POST or None, request.FILES or None,instance=docente)
    context = {'form': form, 'page_title': 'Editar perfil'}
    if request.method == 'POST':
        try:
            if form.is_valid():
                nombre = form.cleaned_data.get('nombre')
                apellido = form.cleaned_data.get('apellido')
                password = form.cleaned_data.get('password') or None
                address = form.cleaned_data.get('address')
                gender = form.cleaned_data.get('gender')
                passport = request.FILES.get('imagen_de_perfil') or None
                admin = docente.admin
                if password != None:
                    admin.set_password(password)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    admin.imagen_de_perfil = passport_url
                admin.nombre = nombre
                admin.apellido = apellido
                admin.address = address
                admin.gender = gender
                admin.save()
                docente.save()
                messages.success(request, "Perfil actualizado")
                return redirect(reverse('staff_view_profile'))
            else:
                messages.error(request, "No se pudo actulizar")
                return render(request, "staff_template/staff_view_profile.html", context)
        except Exception as e:
            messages.error(
                request, "No se pudo actulizar " + str(e))
            return render(request, "staff_template/staff_view_profile.html", context)

    return render(request, "staff_template/staff_view_profile.html", context)


@csrf_exempt
def staff_fcmtoken(request):
    token = request.POST.get('token')
    try:
        staff_user = get_object_or_404(CustomUser, id=request.user.id)
        staff_user.fcm_token = token
        staff_user.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


def staff_view_notification(request):
    docente = get_object_or_404(Staff, admin=request.user)
    notifications = NotificationStaff.objects.filter(docente=docente)
    context = {
        'notifications': notifications,
        'page_title': "Ver notificaciones"
    }
    return render(request, "staff_template/staff_view_notification.html", context)


def staff_add_result(request):
    docente = get_object_or_404(Staff, admin=request.user)
    subjects = Subject.objects.filter(docente=docente)
    sessions = Session.objects.all()
    context = {
        'page_title': 'Actualizar nota',
        'subjects': subjects,
        'sessions': sessions
    }
    if request.method == 'POST':
        try:
            student_id = request.POST.get('student_list')
            subject_id = request.POST.get('subject')
            test = request.POST.get('test')
            exam = request.POST.get('exam')
            student = get_object_or_404(Student, id=student_id)
            subject = get_object_or_404(Subject, id=subject_id)
            try:
                data = StudentResult.objects.get(
                    student=student, subject=subject)
                data.exam = exam
                data.test = test
                data.save()
                messages.success(request, "Nota actualizada")
            except:
                result = StudentResult(student=student, subject=subject, test=test, exam=exam)
                result.save()
                messages.success(request, "Nota guardada")
        except Exception as e:
            messages.warning(request, "Error")
    return render(request, "staff_template/staff_add_result.html", context)


@csrf_exempt
def fetch_student_result(request):
    try:
        subject_id = request.POST.get('subject')
        student_id = request.POST.get('student')
        student = get_object_or_404(Student, id=student_id)
        subject = get_object_or_404(Subject, id=subject_id)
        result = StudentResult.objects.get(student=student, subject=subject)
        result_data = {
            'exam': result.exam,
            'test': result.test
        }
        return HttpResponse(json.dumps(result_data))
    except Exception as e:
        return HttpResponse('False')