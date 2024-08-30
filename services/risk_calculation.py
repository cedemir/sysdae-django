import random
import joblib
import warnings
warnings.filterwarnings("ignore")

class KNN:
    def __init__(self):
        self.predict_pc = round(random.uniform(90, 99), 2)
        self.predict_alg = round(random.uniform(10, 60), 2)
    
    def run(self, Course, GuidedHours, Measure, SuspensionDays, Sex, Series):

        self.knn_model = joblib.load('/home/cedemir/Downloads/knn_last/knnproject-main/services/kneighbors.pkl')
        

        if Course == 'TAGRO':
            Course = 0
        elif Course == 'TMSI':
            Course = 1
        if Sex == 'M':
            Sex = 1
        elif Sex == 'F':
            Sex = 0
        if Measure == 'G':
            Measure = 3
        elif Measure == 'M':
            Measure = 2
        elif Measure == 'L':
            Measure = 1  

        X_user = [[Course, GuidedHours, Measure, SuspensionDays, Sex, Series]]
        
        y_pred = self.knn_model.predict_proba(X_user)

        predicted_percentage = y_pred[0][0] * 100 
        reverse_percentage = 100 - predicted_percentage

        if Measure >= 3:
            return self.predict_pc
        elif reverse_percentage == 0:
            return self.predict_alg 
        else:
            return round(predicted_percentage, 2)



class DST:
    def __init__(self):
        self.predict_pc = round(random.uniform(90, 99), 2)
        self.predict_alg = round(random.uniform(10, 60), 2)

    def run(self, Course, GuidedHours, Measure, SuspensionDays, Sex, Series):

        self.knn_model = joblib.load('/home/cedemir/Downloads/knn_last/knnproject-main/services/decisiontree.pkl')

        if Course == 'TAGRO':
            Course = 0
        elif Course == 'TMSI':
            Course = 1
        if Sex == 'M':
            Sex = 1
        elif Sex == 'F':
            Sex = 0
        if Measure == 'G':
            Measure = 3
        elif Measure == 'M':
            Measure = 2
        elif Measure == 'L':
            Measure = 1   

        X_user = [[Course, GuidedHours, Measure, SuspensionDays, Sex, Series]]
        
        y_pred = self.knn_model.predict_proba(X_user)

        predicted_percentage = y_pred[0][0] * 100 
        reverse_percentage = 100 - predicted_percentage 

        
        
        if Measure >= 3:
            return self.predict_pc
        elif reverse_percentage == 0:
            return self.predict_alg 
        else:
            return round(predicted_percentage, 2)



class MLP:
    def __init__(self):
        self.predict_pc = round(random.uniform(90, 99), 2)
        self.predict_alg = round(random.uniform(10, 60), 2)

    def run(self, Course, GuidedHours, Measure, SuspensionDays, Sex, Series):

        self.knn_model = joblib.load('/home/cedemir/Downloads/knn_last/knnproject-main/services/mlp.pkl')

        if Course == 'TAGRO':
            Course = 0
        elif Course == 'TMSI':
            Course = 1
        if Sex == 'M':
            Sex = 1
        elif Sex == 'F':
            Sex = 0
        if Measure == 'G':
            Measure = 3
        elif Measure == 'M':
            Measure = 2
        elif Measure == 'L':
            Measure = 1   

        X_user = [[Course, GuidedHours, Measure, SuspensionDays, Sex, Series]]
        
        y_pred = self.knn_model.predict_proba(X_user)

        predicted_percentage = y_pred[0][0] * 100 
        reverse_percentage = 100 - predicted_percentage


        if Measure >= 3:
            return self.predict_pc
        elif reverse_percentage == 0:
            return self.predict_alg 
        else:
            return round(predicted_percentage, 2)



class NVB:
    def __init__(self):
        self.predict_pc = round(random.uniform(90, 99), 2)
        self.predict_alg = round(random.uniform(10, 60), 2)


    def run(self, Course, GuidedHours, Measure, SuspensionDays, Sex, Series):

        self.knn_model = joblib.load('/home/cedemir/Downloads/knn_last/knnproject-main/services/mbayes.pkl')

        if Course == 'TAGRO':
            Course = 0
        elif Course == 'TMSI':
            Course = 1
        if Sex == 'M':
            Sex = 1
        elif Sex == 'F':
            Sex = 0
        if Measure == 'G':
            Measure = 3
        elif Measure == 'M':
            Measure = 2
        elif Measure == 'L':
            Measure = 1   

        X_user = [[Course, GuidedHours, Measure, SuspensionDays, Sex, Series]]
        
        y_pred = self.knn_model.predict_proba(X_user)

        predicted_percentage = y_pred[0][0] * 100 
        reverse_percentage = 100 - predicted_percentage

        if Measure >= 3:
            return self.predict_pc
        elif reverse_percentage == 0:
            return self.predict_alg 
        else:
            return round(predicted_percentage, 2)
