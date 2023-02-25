import sys
from django.utils.timezone import now
try:
    from django.db import models
except Exception:
    print("There was an error loading django modules. Do you have django installed?")
    sys.exit()

from django.conf import settings
import uuid


# Instructor model
class Instructor(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    full_time = models.BooleanField(default=True)
    total_learners = models.IntegerField()

    def __str__(self):
        return self.user.username


# Learner model
class Learner(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    STUDENT = 'student'
    DEVELOPER = 'developer'
    DATA_SCIENTIST = 'data_scientist'
    DATABASE_ADMIN = 'dba'
    OCCUPATION_CHOICES = [
        (STUDENT, 'Student'),
        (DEVELOPER, 'Developer'),
        (DATA_SCIENTIST, 'Data Scientist'),
        (DATABASE_ADMIN, 'Database Admin')
    ]
    occupation = models.CharField(
        null=False,
        max_length=20,
        choices=OCCUPATION_CHOICES,
        default=STUDENT
    )
    social_link = models.URLField(max_length=200)

    def __str__(self):
        return self.user.username + "," + \
               self.occupation


# Course model
class Course(models.Model):
    name = models.CharField(null=False, max_length=30, default='online course')
    image = models.ImageField(upload_to='course_images/')
    description = models.CharField(max_length=1000)
    pub_date = models.DateField(null=True)
    instructors = models.ManyToManyField(Instructor)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Enrollment')
    total_enrollment = models.IntegerField(default=0)
    is_enrolled = False

    def __str__(self):
        return "Name: " + self.name + "," + \
               "Description: " + self.description


# Lesson model
class Lesson(models.Model):
    title = models.CharField(max_length=200, default="title")
    order = models.IntegerField(default=0)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    content = models.TextField()

# Enrollment model
# <HINT> Once a user enrolled a class, an enrollment entry should be created between the user and course
# And we could use the enrollment to track information such as exam submissions
class Enrollment(models.Model):
    AUDIT = 'audit'
    HONOR = 'honor'
    BETA = 'BETA'
    COURSE_MODES = [
        (AUDIT, 'Audit'),
        (HONOR, 'Honor'),
        (BETA, 'BETA')
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date_enrolled = models.DateField(default=now)
    mode = models.CharField(max_length=5, choices=COURSE_MODES, default=AUDIT)
    rating = models.FloatField(default=5.0)


# <HINT> Create a Question Model with:
    # Used to persist question content for a course
class Question(models.Model):
    # Has a One-To-Many relationship with course
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    # ManyToOne relationship with Lesson
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    # Has question content
    content = models.TextField()
    # Has a grade point for each question
    grade = models.FloatField()
    # Other fields and methods you would like to design

    def get_score(self, selected_ids):
        """
        Return the score for the question based on the selected choices
            It uses the award-penalty method
        """
        # from models import Case, When, Count
        # # Define the two count expressions using conditional expressions
        # selected_correct_expr = Count(Case(When(is_correct=True, then=1)))
        # selected_not_correct_expr = Count(Case(When(is_correct=False, then=1)))

        # # Retrieve the counts in a single query
        # selected_choices = Choice.objects.filter(id__in=selected_ids)
        # counts = selected_choices.aggregate(selected_correct=selected_correct_expr, selected_not_correct=selected_not_correct_expr)

        # # Extract the counts from the result dictionary
        # selected_correct = counts['selected_correct']
        # selected_not_correct = counts['selected_not_correct']

        all_choices = self.choice_set
        selected_choices = self.choice_set.filter(id__in=selected_ids)
        correct_choices = self.choice_set.filter(is_correct=True)
        
        correct = selected_choices.intersection(correct_choices)
        incorrect = selected_choices.difference(correct_choices)

        #  answer worth = total number of points assigned to the question divided by the total number of answer choices.
        worth = self.grade / correct_choices.count()
        
        print("all choices: ", all_choices)
        print("selected choices: ", selected_choices)
        print("correct choices: ", correct_choices)
        print("got_correct: ", correct)
        print("got_incorrect: ", incorrect)

        score = max(0, worth * ( correct.count() - incorrect.count() ) )
        print(score)
        return score
    
        

        
        # counts = selected_choices.aggregate(
        #     selected_correct=models.Count(models.Case(models.When(is_correct=True, then=1))), 
        #     selected_not_correct=models.Count(models.Case(models.When(is_correct=False, then=1)))
        # )
        # # Extract the counts from the result dictionary
        # selected_correct = counts['selected_correct']
        # selected_not_correct = counts['selected_not_correct']

        return (selected_correct - selected_not_correct) / all_answers * self.grade


#  <HINT> Create a Choice Model with:
    # Used to persist choice content for a question
class Choice(models.Model):
    # One-To-Many (or Many-To-Many if you want to reuse choices) relationship with Question
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    # Choice content
    choice_text = models.TextField()
    # Indicate if this choice of the question is a correct one or not
    is_correct = models.BooleanField(default=False)
    # Other fields and methods you would like to design

# <HINT> The submission model
# ManyToOne relationship with Enrollment
    # One enrollment could have multiple submission
# ManyToMany relationship with Choice
    # One submission could have multiple choices
    # One choice could belong to multiple submissions
class Submission(models.Model):
   enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
   choices = models.ManyToManyField(Choice)
#    Other fields and methods you would like to design