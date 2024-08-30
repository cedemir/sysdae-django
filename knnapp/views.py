from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from rest_framework.parsers import JSONParser

from knnapp import models, serializers
from services import risk_calculation as rc
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from base64 import urlsafe_b64encode, urlsafe_b64decode
from cryptography.fernet import Fernet

import pandas as pd
import json

def generate_key_from_password(password):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b'salt_123', 
        iterations=100000,
        backend=default_backend()
    )
    key = urlsafe_b64encode(kdf.derive(password.encode('utf-8')))
    return key

def generate_fernet_key():
    return Fernet.generate_key()

def encrypt_name(name, key):
    cipher_suite = Fernet(key)
    encrypted_name = cipher_suite.encrypt(name.encode('utf-8'))
    return urlsafe_b64encode(encrypted_name)

def decrypt_name(encrypted_name, key):
    cipher_suite = Fernet(key)
    decrypted_name = cipher_suite.decrypt(urlsafe_b64decode(encrypted_name)).decode('utf-8')
    return decrypted_name

name_pairs = []
secret_key = generate_fernet_key()

def import_csv(request):
    output_file_path = 'ZVFITUJ1VWVfQnd2NW16blo5T.txt'
    if request.method == 'POST' and 'csv_file' in request.FILES:
        csv_file = request.FILES['csv_file']

        try:
            dados = pd.read_excel(csv_file)
            students_data = dados.to_dict(orient='records')

            return render(request, 'admin/import_csv_template.html', {'students_data': students_data})

        except pd.errors.ParserError as e:
            return HttpResponse(f'Error parsing Excel file: {e}')
    
    elif request.method == 'POST' and 'csv_file' is not request.FILES:
        selected_students = request.POST.getlist('selected_students')

        for student_matricula in selected_students:
            matricula = request.POST[f'matricula_{student_matricula}']
            aluno = request.POST[f'aluno_{student_matricula}']
            curso = request.POST[f'curso_{student_matricula}']
            nome_pai = request.POST[f'nome_pai_{student_matricula}']
            telefone_pai = request.POST[f'telefone_pai_{student_matricula}']
            nome_mae = request.POST[f'nome_mae_{student_matricula}']
            telefone_mae = request.POST[f'telefone_mae_{student_matricula}']
            email_responsavel = request.POST[f'email_responsavel_{student_matricula}']

            cript_mae = encrypt_name(nome_mae,secret_key)
            cript_pai = encrypt_name(nome_pai,secret_key)
            cript_mae_tel = encrypt_name(telefone_mae,secret_key)
            cript_pai_tel = encrypt_name(telefone_pai,secret_key)

            desc_mae = decrypt_name(cript_mae,secret_key)
            desc_mae_tel = decrypt_name(cript_mae_tel,secret_key)
            desc_pai = decrypt_name(cript_pai,secret_key)
            desc_pai_tel = decrypt_name(cript_pai_tel,secret_key)

            bin_mae = cript_mae.decode('utf-8')
            bin_pai = cript_pai.decode('utf-8')
            bin_mae_tel = cript_mae_tel.decode('utf-8')
            bin_pai_tel = cript_pai_tel.decode('utf-8')
            name_pairs.append({
                               bin_mae: desc_mae,
                               bin_mae_tel: desc_mae_tel,
                               bin_pai: desc_pai,
                               bin_pai_tel: desc_pai_tel,
                            })

            models.Students.objects.create(
                registration=matricula,
                name=aluno,
                namefather=bin_pai,
                telfather=bin_pai_tel,
                namemother=bin_mae,
                telmother=bin_mae_tel,
                email=email_responsavel,
                career=curso,
            )
        
        with open(output_file_path, 'w') as output_file:
            json.dump(name_pairs, output_file)
            output_file.write('\n')

        return HttpResponse(f'Successfully imported {len(selected_students)} students from CSV.')

    else:
        return HttpResponse('No CSV file provided for import.')


def risk_calculation(request):

    students = models.Students.objects.all()
    violations = models.Violations.objects.all()
    measures = models.Measures.objects.all()

    serializer_student = serializers.StudentsSerializer(students, many=True)
    serializer_violation = serializers.ViolationsSerializer(violations, many=True)

    serializerstudent = serializers.StudentsSerializer(students, many=True)
    datastudent = serializerstudent.data

    serializermeasures = serializers.MeasuresSerializer(measures, many=True)
    datameasures = serializermeasures.data

    serializerviolations = serializers.ViolationsSerializer(violations, many=True)
    dataviolations = serializerviolations.data

    hours = 15
    suspension = 5
    series = 2
    career = []
    genre = []
    measure = []


    for datas in datastudent:
        career.append(datas['career'])
        genre.append(datas['genre'])

    for datav in dataviolations:
        for datam in datameasures:
            if datav['measure'] == datam['id']:
                measure.append(datam['classification'])

    result = []
    n = 0
    for i in serializer_student.data:
        list = []
        for j in serializer_violation.data:
            if (j["student"] == i["id"]):
                list.append([[j["measure"]]])
        result.append((i["id"], rc.KNN().run(career[n],hours,measure[n],suspension,genre[n],series), rc.DST().run(career[n],hours,measure[n],suspension,genre[n],series),rc.MLP().run(career[n],hours,measure[n],suspension,genre[n],series),rc.NVB().run(career[n],hours,measure[n],suspension,genre[n],series)))

        n +=1

    for res in result:
        try:
            student = models.Students.objects.get(pk=res[0])
            print(result,'RESULT', student.name, 'STUDENT', student.registration, 'REGISTRATION')
        except models.Students.DoesNotExist:
            return HttpResponse(status=404)


        serializer = serializers.StudentsSerializer(student, data={
            'registration': student.registration,
            'name': student.name,
            'risk_knn': res[1],
            'risk_skl': res[2],
            'risk_tree': res[3],
            'risk_mlp': res[4],
        }, context={'request': request})
        if serializer.is_valid():
            serializer.save()
        else:
            return HttpResponse("Serializer não é valida")
    
    return HttpResponse("Riscos dos alunos atualizado com sucesso!")

@csrf_exempt
def students_list(request):
    if request.method == 'GET':
        students = models.Students.objects.all()
        serializer = serializers.StudentsSerializer(students, many=True)
        return JsonResponse(serializer.data[0], safe=False)
    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = serializers.StudentsSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)


@csrf_exempt
def student_detail(request, pk):
    try:
        student = models.Students.objects.get(pk=pk)
    except models.Students.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = serializers.StudentsSerializer(student)
        return JsonResponse(serializer.data)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = serializers.StudentsSerializer(student, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        student.delete()
        return HttpResponse(status=204)


@csrf_exempt
def measures_list(request):
    if request.method == 'GET':
        measures = models.Measures.objects.all()
        serializer = serializers.StudentsSerializer(measures, many=True)
        return JsonResponse(serializer.data, safe=False)
    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = serializers.MeasuresSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)


@csrf_exempt
def measures_detail(request, pk):
    try:
        measure = models.Measures.objects.get(pk=pk)
    except models.Measures.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = serializers.MeasuresSerializer(measure)
        return JsonResponse(serializer.data)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = serializers.MeasuresSerializer(measure, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        measure.delete()
        return HttpResponse(status=204)


@csrf_exempt
def regulations_list(request):
    if request.method == 'GET':
        regulations = models.Regulations.objects.all()
        serializer = serializers.RegulationsSerializer(regulations, many=True)
        return JsonResponse(serializer.data, safe=False)
    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = serializers.RegulationsSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)


@csrf_exempt
def regulations_detail(request, pk):
    try:
        regulation = models.Regulations.objects.get(pk=pk)
    except models.Regulations.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = serializers.RegulationsSerializer(regulation)
        return JsonResponse(serializer.data)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = serializers.RegulationsSerializer(regulation, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        regulation.delete()
        return HttpResponse(status=204)


@csrf_exempt
def violations_list(request):
    if request.method == 'GET':
        violations = models.Violations.objects.all()
        serializer = serializers.ViolationsSerializer(violations, many=True)
        return JsonResponse(serializer.data, safe=False)
    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = serializers.ViolationsSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)


@csrf_exempt
def violations_detail(request, pk):
    try:
        violation = models.Violations.objects.get(pk=pk)
    except models.Violations.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = serializers.ViolationsSerializer(violation)
        return JsonResponse(serializer.data)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = serializers.ViolationsSerializer(violation, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        violation.delete()
        return HttpResponse(status=204)
    