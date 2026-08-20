"""Test factory helpers."""
from apps.catalog.models import Exercise, IntensityTechnique, Muscle
from apps.splits.models import Split, SplitDay
from apps.users.models import Role, User


def make_role(name='user', description='') -> Role:
    return Role.objects.create(name=name, description=description)


def make_user(email='test@example.com', user_name='tester', password='TestPass123!', role_name='user') -> User:
    role, _ = Role.objects.get_or_create(name=role_name, defaults={'description': role_name})
    user = User.objects.create(
        idRole=role,
        firstName='Test',
        lastName='User',
        userName=user_name,
        email=email,
    )
    user.set_password(password)
    user.save()
    return user


def make_muscle(name='Pectoral mayor') -> Muscle:
    return Muscle.objects.create(name=name)


def make_exercise(name='Press banca', muscle: Muscle = None) -> Exercise:
    exercise = Exercise.objects.create(name=name)
    if muscle:
        from apps.catalog.models import ExerciseMuscle
        ExerciseMuscle.objects.create(idExercise=exercise, idMuscle=muscle, role='primary')
    return exercise


def make_technique(name='Drop set') -> IntensityTechnique:
    return IntensityTechnique.objects.create(name=name)


def make_split(name='Push/Pull/Legs') -> Split:
    return Split.objects.create(name=name)


def make_split_day(split: Split, day_number=1, day_name='Push') -> SplitDay:
    return SplitDay.objects.create(idSplit=split, dayNumber=day_number, name=day_name)
