from django.contrib import admin
from unfold.admin import ModelAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import (
    User, UserProfile, UserPreferences, PreferenceHistory,
    UserCommunication, UserFeedback, UserEngagementMetrics,
    AgeVerification, GuardianControl
)

class CustomUserAdmin(ModelAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ('email', 'phone_number','wisrod_account_id', 'is_staff', 'is_active', 'is_verified')
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

@admin.register(AgeVerification)
class AgeVerificationAdmin(ModelAdmin, admin.ModelAdmin):
    list_display = ('user', 'date_of_birth', 'verification_status', 'verified_at')
    list_filter = ('verification_status',)
    search_fields = ('user__email',)
    readonly_fields = ('verified_at',)

@admin.register(GuardianControl)
class GuardianControlAdmin(ModelAdmin, admin.ModelAdmin):
    list_display = ('guardian', 'minor', 'daily_transaction_limit', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('guardian__email', 'minor__email')
    readonly_fields = ('created_at', 'updated_at', 'last_notification_sent')