from rest_framework.serializers import ModelSerializer

from .models import Students, Regulations, Measures, Violations


class StudentsSerializer(ModelSerializer):
    class Meta:
        model = Students
        fields = '__all__'


class RegulationsSerializer(ModelSerializer):
    class Meta:
        model = Regulations
        fields = '__all__'


class MeasuresSerializer(ModelSerializer):
    class Meta:
        model = Measures
        fields = '__all__'


class ViolationsSerializer(ModelSerializer):
    class Meta:
        model = Violations
        fields = '__all__'


