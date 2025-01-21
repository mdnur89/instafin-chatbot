from django.contrib import admin
from unfold.admin import ModelAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import (
    User, UserProfile, UserPreferences, PreferenceHistory,
    UserCommunication, UserFeedback, UserEngagementMetrics
)

class CustomUserAdmin(ModelAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ('email', 'phone_number', 'is_staff', 'is_active', 'is_verified')
    list_filter = ('is_staff', 'is_active', 'is_verified')
    search_fields = ('email', 'phone_number')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone_number', 'date_of_birth', 'national_id')}),
        ('Financial', {'fields': ('credit_score', 'risk_level', 'current_balance')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_verified')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'phone_number', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )

# Register all models with Unfold's ModelAdmin
admin.site.register(User, CustomUserAdmin)
admin.site.register(UserProfile, ModelAdmin)
admin.site.register(UserPreferences, ModelAdmin)
admin.site.register(PreferenceHistory, ModelAdmin)
admin.site.register(UserCommunication, ModelAdmin)
admin.site.register(UserFeedback, ModelAdmin)
admin.site.register(UserEngagementMetrics, ModelAdmin)