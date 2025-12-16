from django.db import models

# Create your models here.
# citizen_app/models.py

# 1. ADMINISTRATIVE_UNIT
class AdministrativeUnit(models.Model):
    Unit_ID = models.CharField(primary_key=True, max_length=10)
    Unit_Name = models.CharField(max_length=100)
    Address = models.CharField(max_length=200, blank=True, null=True)
    Unit_Type = models.CharField(max_length=50)

    class Meta:
        managed = True # Hoặc False nếu bạn muốn dùng DB có sẵn mà không migrate
        db_table = 'ADMINISTRATIVE_UNIT'
    def __str__(self):
        return self.Unit_Name

# 2. CITIZEN (Yêu cầu phải có HouseholdBook để FK hoạt động)
# Tạm thời để HouseholdBook là CharField, sau đó dùng lệnh SQL để liên kết nếu dùng DB có sẵn
class Citizen(models.Model):
    RESIDENCE_STATUS_CHOICES = [
        ('Permanent', 'Permanent'),
        ('Temporary_Resident', 'Temporary Resident'),
        ('Temporary_Absent', 'Temporary Absent'),
    ]
    
    CCCD_ID = models.CharField(primary_key=True, max_length=20)
    Full_Name = models.CharField(max_length=100)
    Date_of_Birth = models.DateField()
    Gender = models.CharField(max_length=10)
    
    # ... (Các trường VARCHAR, TEXT khác) ...
    
    # Khóa ngoại tự tham chiếu (Self-Referencing FKs)
    Father_CCCD_ID = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children_by_father')
    Mother_CCCD_ID = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children_by_mother')
    Spouse_CCCD_ID = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='married_to')

    # Khóa ngoại đến HouseholdBook (Chủ hộ)
    Head_of_Household_CCCD_ID = models.ForeignKey('HouseholdBook', on_delete=models.SET_NULL, null=True, blank=True, related_name='headed_citizens', to_field='Head_of_Household_CCCD_ID')
    Household_Book_ID = models.ForeignKey('HouseholdBook', on_delete=models.SET_NULL, null=True, blank=True, related_name='members', to_field='Household_Book_ID')

    Management_Unit_ID = models.ForeignKey(AdministrativeUnit, on_delete=models.SET_NULL, null=True, blank=True)
    Date_of_Death = models.DateField(null=True, blank=True)
    
    class Meta:
        managed = True
        db_table = 'CITIZEN'

# 3. HOUSEHOLD_BOOK
class HouseholdBook(models.Model):
    Household_Book_ID = models.CharField(primary_key=True, max_length=50)
    
    # Khóa ngoại Chủ hộ (Phải là OneToOne nếu mỗi công dân chỉ là Chủ hộ của 1 Sổ)
    Head_of_Household_CCCD_ID = models.OneToOneField(Citizen, on_delete=models.CASCADE, related_name='is_head_of', primary_key=False) # Không dùng primary_key=True ở đây.
    
    Permanent_Residence_Address = models.CharField(max_length=200)
    Issue_Date = models.DateTimeField(auto_now_add=True) 
    Number_of_Members = models.IntegerField()
    Issuing_Unit_ID = models.ForeignKey(AdministrativeUnit, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'HOUSEHOLD_BOOK'
    def __str__(self):
        return self.Household_Book_ID

# 4. TEMPORARY_RESIDENCE
class TemporaryResidence(models.Model):
    Temp_Residence_ID = models.CharField(primary_key=True, max_length=50)
    CCCD_ID = models.ForeignKey(Citizen, on_delete=models.CASCADE)
    Temporary_Address = models.CharField(max_length=200)
    Start_Date = models.DateField()
    End_Date = models.DateField(null=True, blank=True)
    Registration_Unit_ID = models.ForeignKey(AdministrativeUnit, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        managed = True
        db_table = 'TEMPORARY_RESIDENCE'
    # ... (Các Models còn lại trong citizen_app) ...