from django import forms
from .models import WasteReport


class WasteReportForm(forms.ModelForm):
    class Meta:
        model = WasteReport
        fields = ['waste_type', 'location', 'description']
        widgets = {
            'waste_type': forms.Select(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Along Ngong Road, near Adams Arcade'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe what you found (optional)'
            }),
        }